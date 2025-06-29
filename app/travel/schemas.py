from pydantic import BaseModel
from typing import Optional, Dict


class TravelCreate(BaseModel):
    trip_id: int
    from_station_id: int
    to_station_id: int


class TravelSchema(BaseModel):
    id: int
    trip_id: int
    from_station_id: int
    to_station_id: int
    method_of_transport: str
    cost_euros: Optional[float]
    travel_route_description: Dict

    class Config:
        orm_mode = True
