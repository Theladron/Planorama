from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.auth.services import get_current_active_user
from app.core.database import get_db
from app.users.models import User
from app.stations.schemas import StationCreate, StationSchema, StationWithLinkIdSchema
from app.trip_stations.schemas import TripStationsReorderRequest
from app.stations.services import (
    get_all_stations,
    create_station,
    reorder_stations,
    delete_station,
    admin_delete_station,
    get_station,
    get_stations_by_trip,
    get_trip_stations_with_link_id
)

station_router = APIRouter(prefix="/stations", tags=["Stations"])
admin_station_router = APIRouter(prefix="/admin/stations", tags=["Admin"])


@station_router.post(
    "/",
    response_model=StationSchema,
    summary="Create a new station for a user's trip",
    description=(
        "Creates a new station and links it to one of the current user's trips via the linking table. "
        "Each trip day can only have one station assigned, so you cannot add multiple stations with the same day_number. "
        "The day_number and trip_id provided are stored in the linking table, not directly on the station. "
        "The station's day_number must fall within the trip's duration. "
        "Coordinates are automatically retrieved from an external service."
    )
)
async def create_new_station(
    station: StationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if station.trip_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid trip_id")
    return await create_station(db, station, current_user.id)


@station_router.get(
    "/by-trip/{trip_id}",
    response_model=list[StationWithLinkIdSchema],
    summary="Get all stations for a trip including linked TripStation ID",
    description=(
        "Returns all stations linked to a trip belonging to the current user, "
        "including the linking TripStation ID (link_id), "
        "ordered by day_number as stored in the linking table."
    )
)
def list_stations_for_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves TripStations linked to a user's trip and returns them
    with station details, TripStation link id, and day_number.
    """
    return get_trip_stations_with_link_id(db, trip_id, current_user.id)


@station_router.put(
    "/reorder",
    response_model=List[StationWithLinkIdSchema],
    summary="Bulk reorder trip stations using link IDs",
    description=(
        "Updates the order of stations within a user's trip by modifying their `day_number`s "
        "in the TripStation link table.\n\n"
        "**Important:**\n"
        "- Use the `link_id` from the `/stations/by-trip` endpoint.\n"
        "- `link_id` refers to the TripStation entry, **not** the Station ID.\n"
        "- Duplicate `day_number`s are not allowed.\n"
        "- The same station can appear multiple times on different days.\n"
        "- Only affects the linking table; original Station records are untouched.\n"
        "- Automatically removes consecutive duplicate station links."
    ),
)
def put_reorder_stations(
    reorder_request: TripStationsReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Reorders stations in a trip by updating the `day_number` field in the TripStation link table.
    Accepts a list of objects with `link_id` (TripStation.id) and a new `day_number`.

    Validations:
    - All day numbers must be positive integers within trip duration.
    - No duplicate day_numbers allowed.
    - Each TripStation must belong to the specified trip and the current user.

    Returns the updated list of TripStations with full station info.
    """
    if not reorder_request.stations:
        raise HTTPException(status_code=400, detail="Station list cannot be empty")
    if reorder_request.trip_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid trip_id")

    try:
        return reorder_stations(
            db=db,
            trip_id=reorder_request.trip_id,
            reorder_items=reorder_request.stations,
            user_id=current_user.id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))



@station_router.delete(
    "/{link_id}",
    summary="Remove a station from a trip using link ID",
    description=(
        "Removes a specific instance of a station from a trip. "
        "`link_id` refers to the **TripStation link ID**, not the station itself. "
        "This only affects the specified trip — the Station object remains intact if used in other trips.\n\n"
        "Also handles:\n"
        "- Cleaning up unused countries from the trip.\n"
        "- Automatically removing adjacent duplicate stations.\n"
        "- Syncing updated route data."
    ),
)
def user_delete_station(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Deletes a TripStation link by its ID (which removes the station from the specific trip).

    Note:
        While this endpoint deletes the TripStation link, the underlying Station object
        itself is **only deleted** if no other TripStation links exist referencing it.
        Otherwise, the Station object remains intact.

    Args:
        link_id (int): The ID of the TripStation link (not the Station itself).
        db (Session): The database session.
        current_user (User): The authenticated user.

    Returns:
        dict: A success message upon deletion.
    """
    if link_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid link_id")

    try:
        return delete_station(db, link_id, current_user.id)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error occurred")



@admin_station_router.get(
    "/",
    response_model=list[StationSchema],
    summary="Admin: List all stations",
    description="Returns a list of all stations in the system. Admin access required."
)
def admin_list_all_stations(db: Session = Depends(get_db)):
    return get_all_stations(db)


@admin_station_router.delete(
    "/{station_id}",
    summary="Admin: Delete any station by ID",
    description="Allows an admin to delete any station by its ID."
)
def admin_delete_station_by_id(station_id: int, db: Session = Depends(get_db)):
    if station_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid station_id")
    success = admin_delete_station(db, station_id)
    if not success:
        raise HTTPException(status_code=404, detail="Station not found")
    return {"message": "Station deleted"}
