"""Station management service functions."""
from sqlalchemy.orm import Session, joinedload
from app.stations.models import Station
from app.trips.models import Trip
from app.users.models import User
from app.trip_stations.models import TripStation
from app.trip_stations.schemas import TripStationReorderItem, TripStationCreate
from app.stations.schemas import StationCreate, StationWithLinkIdSchema
from app.trip_stations.services import (get_trip_station_by_trip_and_day,
                                        create_trip_station,
                                        sync_travel_routes_for_trip_stations,
                                        get_trip_stations_for_trip,
                                        delete_trip_station)
from fastapi import HTTPException
from typing import cast, List
from app.core.connector_loader import openroute_connector, googletrans_connector


def get_station(db: Session, station_id: int):
    """Retrieve a station by its ID.
    
    Args:
        db: Database session.
        station_id: Unique station identifier.
        
    Returns:
        Station object if found, None otherwise.
    """
    return db.query(Station).filter(Station.id == station_id).first()


def get_trip(db: Session, trip_id: int):
    """Retrieve a trip by its ID.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        
    Returns:
        Trip object if found, None otherwise.
    """
    return db.query(Trip).filter_by(id=trip_id).first()


def get_all_stations(db: Session):
    """Retrieve all stations from the database.
    
    Args:
        db: Database session.
        
    Returns:
        List of all Station objects.
    """
    return db.query(Station).all()


def get_user_language_preference(db: Session, user_id: str):
    """Retrieve a user's language preference.
    
    Args:
        db: Database session.
        user_id: Auth0 user identifier.
        
    Returns:
        User's language preference code ('en' or 'de'), defaults to 'en'.
        
    Raises:
        HTTPException: If user not found.
    """
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.language_preference or "en"


def get_trip_stations_with_link_id(db: Session, trip_id: int, user_id: str) -> List[TripStation]:
    """Retrieve TripStation objects linked to a trip owned by user.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        user_id: Unique user identifier for authorization.
        
    Returns:
        List of StationWithLinkIdSchema objects ordered by day_number.
        
    Raises:
        HTTPException: If trip_id is invalid or user is unauthorized.
    """
    if trip_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid trip ID")

    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized or trip not found")

    trip_stations = (
        db.query(TripStation)
        .filter_by(trip_id=trip_id)
        .order_by(TripStation.day_number)
        .options(joinedload(TripStation.station))
        .all()
    )
    return [
        StationWithLinkIdSchema(
            id=trip_station.station.id,
            station_name=trip_station.station.station_name,
            station_name_de=trip_station.station.station_name_de,
            latitude=trip_station.station.latitude,
            longitude=trip_station.station.longitude,
            country=trip_station.station.country,
            link_id=trip_station.id,
            day_number=trip_station.day_number,
        )
        for trip_station in trip_stations
    ]


async def create_station(db: Session, station_data: StationCreate, user_id: str) -> Station:
    """Create a new station and link it to a trip.
    
    Args:
        db: Database session.
        station_data: StationCreate schema with station information.
        user_id: Unique user identifier for authorization.
        
    Returns:
        Created or existing Station object.
        
    Raises:
        HTTPException: If validation fails, location lookup fails, or unauthorized.
    """
    if station_data.trip_id <= 0 or station_data.day_number <= 0:
        raise HTTPException(status_code=400, detail="Trip ID and day number must be positive integers")

    trip = get_trip(db, station_data.trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Trip not found or unauthorized")

    duration_days = (trip.end_date - trip.start_date).days + 1
    if station_data.day_number > duration_days:
        raise HTTPException(status_code=400, detail="Day number is out of trip range")

    existing_trip_station = get_trip_station_by_trip_and_day(db, station_data.trip_id, station_data.day_number)
    if existing_trip_station:
        raise HTTPException(status_code=400, detail=f"A station already exists on day {station_data.day_number}.")

    location_info = openroute_connector.get_location_info(station_data.station_name)
    if not location_info:
        raise HTTPException(status_code=400, detail="Location lookup failed")

    lat = location_info.get("lat")
    lon = location_info.get("lon")
    country_raw = location_info.get("country")

    if lat is None or lon is None or not country_raw:
        raise HTTPException(status_code=400, detail="Incomplete location information")

    origin_lang = get_user_language_preference(db, user_id)
    if origin_lang not in ["en", "de"]:
        raise HTTPException(status_code=400, detail="Unsupported language preference")

    if origin_lang == "en":
        station_name_en = station_data.station_name
        station_name_de = await googletrans_connector.translate(station_data.station_name, "de", origin_lang)
    else:
        station_name_de = station_data.station_name
        station_name_en = await googletrans_connector.translate(station_data.station_name, "en", origin_lang)

    if not station_name_en or not station_name_de:
        raise HTTPException(status_code=400, detail="Failed to translate station name")

    country_en = await googletrans_connector.translate(country_raw, "en", origin_lang)
    if not country_en:
        raise HTTPException(status_code=400, detail="Failed to translate country name")

    existing_station = db.query(Station).filter(Station.station_name == station_name_en).first()

    if existing_station:
        all_trip_stations = get_trip_stations_for_trip(db, station_data.trip_id)
        all_trip_stations.sort(key=lambda trip_station: trip_station.day_number)

        ordered_station_ids = [trip_station.station_id for trip_station in all_trip_stations]
        insert_index = next(
            (index for index, trip_station in enumerate(all_trip_stations) if trip_station.day_number > station_data.day_number),
            len(all_trip_stations)
        )

        new_order_station_ids = ordered_station_ids.copy()
        new_order_day_numbers = [trip_station.day_number for trip_station in all_trip_stations]
        new_order_station_ids.insert(insert_index, existing_station.id)
        new_order_day_numbers.insert(insert_index, station_data.day_number)

        for idx in range(len(new_order_station_ids) - 1):
            if new_order_station_ids[idx] == new_order_station_ids[idx + 1]:
                day1 = new_order_day_numbers[idx]
                day2 = new_order_day_numbers[idx + 1]

                if station_data.day_number == max(day1, day2):
                    return existing_station

                day_to_delete = max(day1, day2)
                delete_trip_station(db, trip_id=station_data.trip_id, day_number=day_to_delete, user_id=user_id)
                db.flush()
                break

        create_trip_station(db, data=TripStationCreate(
            trip_id=station_data.trip_id,
            station_id=existing_station.id,
            day_number=station_data.day_number,
        ))
        db.commit()
        return existing_station

    new_station = Station(
        station_name=station_name_en,
        station_name_de=station_name_de,
        latitude=lat,
        longitude=lon,
        country=country_en
    )
    db.add(new_station)
    db.flush()

    create_trip_station(db, data=TripStationCreate(
        trip_id=station_data.trip_id,
        station_id=new_station.id,
        day_number=station_data.day_number,
    ))

    current_countries = set(trip.trip_countries or [])
    if country_en not in current_countries:
        trip.trip_countries = list(current_countries.union({country_en}))
        db.add(trip)

    db.commit()
    db.refresh(new_station)
    return new_station





def delete_station(
    db: Session,
    link_id: int,
    user_id: str
):
    """Delete a station link from a trip.
    
    Args:
        db: Database session.
        link_id: Unique TripStation link identifier.
        user_id: Unique user identifier for authorization.
        
    Returns:
        Dictionary with success message.
        
    Raises:
        HTTPException: If link_id is invalid, link not found, or unauthorized.
    """
    if link_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid TripStation link ID")

    trip_station = db.query(TripStation).filter(TripStation.id == link_id).first()
    if not trip_station:
        raise HTTPException(status_code=404, detail="TripStation not found")

    trip = db.query(Trip).filter(Trip.id == trip_station.trip_id).first()
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized or trip not found")

    country_to_check = trip_station.station.country

    db.delete(trip_station)
    db.commit()
    db.refresh(trip)

    _remove_country_if_unused(db, trip, country_to_check)

    trip_station_links = (
        db.query(TripStation)
        .filter(TripStation.trip_id == trip.id)
        .order_by(TripStation.day_number)
        .all()
    )

    to_delete_links = []
    previous_station_name = None
    for trip_station in trip_station_links:
        current_name = trip_station.station.station_name
        if current_name == previous_station_name:
            to_delete_links.append(trip_station)
        else:
            previous_station_name = current_name

    for trip_station in to_delete_links:
        db.delete(trip_station)

    db.commit()

    sync_travel_routes_for_trip_stations(db, trip.id)

    return {"detail": "TripStation link deleted successfully"}



def admin_delete_station(db: Session, station_id: int):
    """Delete a station and all its links (admin only).
    
    Args:
        db: Database session.
        station_id: Unique station identifier.
        
    Returns:
        Dictionary with success message including number of affected trips.
        
    Raises:
        HTTPException: If station_id is invalid or station not found.
    """
    if station_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid station ID")

    station = get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    trip_station_links = db.query(TripStation).filter_by(station_id=station_id).all()

    if not trip_station_links:
        db.delete(station)
        db.commit()
        return {"detail": "Station deleted (no links existed)"}

    affected_trip_ids = {trip_station.trip_id for trip_station in trip_station_links}
    country_to_check = station.country

    for link in trip_station_links:
        db.delete(link)

    db.delete(station)
    db.commit()

    for trip_id in affected_trip_ids:
        trip = db.query(Trip).filter_by(id=trip_id).first()
        if trip:
            _remove_country_if_unused(db, trip, country_to_check)
            sync_travel_routes_for_trip_stations(db, trip.id)

    return {"detail": f"Station and all associated links "
                      f"deleted from {len(affected_trip_ids)} trip(s)"}



def reorder_stations(
    db: Session,
    trip_id: int,
    reorder_items: List[TripStationReorderItem],
    user_id: str
) -> List[TripStation]:
    """Reorder stations within a trip by updating day numbers.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        reorder_items: List of TripStationReorderItem with new day numbers.
        user_id: Unique user identifier for authorization.
        
    Returns:
        List of reordered StationWithLinkIdSchema objects.
        
    Raises:
        HTTPException: If validation fails, stations not found, or unauthorized.
    """
    if trip_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid trip ID")

    trip = db.query(Trip).filter_by(id=trip_id).first()
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized or trip not found")

    if not trip.start_date or not trip.end_date:
        raise HTTPException(status_code=400, detail="Trip must have a start and end date")

    duration_days = (trip.end_date - trip.start_date).days + 1

    seen_days = set()
    for item in reorder_items:
        if item.day_number <= 0:
            raise HTTPException(status_code=400, detail="Day numbers must be positive integers")
        if item.day_number > duration_days:
            raise HTTPException(status_code=400, detail=f"Day number {item.day_number} exceeds trip range")
        if item.day_number in seen_days:
            raise HTTPException(status_code=400, detail="Duplicate day_numbers not allowed")
        seen_days.add(item.day_number)

    trip_station_ids = [item.link_id for item in reorder_items]
    trip_stations = db.query(TripStation).filter(TripStation.id.in_(trip_station_ids)).all()

    if len(trip_stations) != len(reorder_items):
        raise HTTPException(status_code=404, detail="One or more TripStations not found")

    for trip_station in trip_stations:
        if trip_station.trip_id != trip_id:
            raise HTTPException(status_code=400, detail="TripStation does not belong to specified trip")

    id_to_day = {item.link_id: item.day_number for item in reorder_items}
    for trip_station in trip_stations:
        trip_station.day_number = id_to_day[trip_station.id]

    db.flush()

    all_trip_stations = get_trip_stations_for_trip(db, trip_id)
    to_delete: List[TripStation] = []
    previous_name = None
    for trip_station in all_trip_stations:
        current_name = trip_station.station.station_name
        if current_name == previous_name:
            to_delete.append(trip_station)
        else:
            previous_name = current_name

    for trip_station in to_delete:
        db.delete(trip_station)

    db.commit()

    sync_travel_routes_for_trip_stations(db, trip_id)

    remaining_stations = get_trip_stations_with_link_id(db, trip_id, user_id)
    return remaining_stations




def get_stations_by_trip(db: Session, trip_id: int, user_id: str) -> List[Station]:
    """Retrieve all stations for a specific trip in order.
    
    Args:
        db: Database session.
        trip_id: Unique trip identifier.
        user_id: Unique user identifier for authorization.
        
    Returns:
        List of Station objects ordered by day_number.
        
    Raises:
        HTTPException: If trip_id is invalid or user is unauthorized.
    """
    if trip_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid trip ID")

    trip = get_trip(db, trip_id)
    if not trip or trip.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized or trip not found")

    trip_stations = db.query(TripStation)\
        .filter_by(trip_id=trip_id)\
        .order_by(TripStation.day_number)\
        .all()

    station_ids = [trip_station.station_id for trip_station in trip_stations]

    if not station_ids:
        return []

    stations = db.query(Station).filter(Station.id.in_(station_ids)).all()
    stations_by_id = {station.id: station for station in stations}
    ordered_stations = [stations_by_id[station_id] for station_id in station_ids if station_id in stations_by_id]

    return ordered_stations


def _remove_country_if_unused(db: Session, trip: Trip, country: str | None):
    """Remove a country from trip_countries if no stations reference it.
    
    Args:
        db: Database session.
        trip: Trip object to update.
        country: Country name to check and potentially remove.
    """
    if not country or not trip.trip_countries:
        return

    db.refresh(trip)

    trip_stations = get_trip_stations_for_trip(db, trip.id)

    station_ids = [trip_station.station_id for trip_station in trip_stations]

    if not station_ids:
        if country in trip.trip_countries:
            current_countries = set(trip.trip_countries)
            current_countries.discard(country)
            trip.trip_countries = list(current_countries)
            db.add(trip)
            db.commit()
        return

    stations_in_country = db.query(Station).filter(
        Station.id.in_(station_ids),
        Station.country == country
    ).first()

    if not stations_in_country and country in trip.trip_countries:
        current_countries = set(trip.trip_countries)
        current_countries.discard(country)
        trip.trip_countries = list(current_countries)
        db.add(trip)
        db.commit()
