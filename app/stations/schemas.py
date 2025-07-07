from pydantic import BaseModel
from typing import Optional


class StationBase(BaseModel):
    station_name: str  # Treated as user's preferred language


class StationCreate(StationBase):
    latitude: float
    longitude: float
    country: str

    # Used for trips_stations linking table
    trip_id: int
    day_number: int


class StationSchema(StationBase):
    id: int
    station_name_de: str
    latitude: float
    longitude: float
    country: str

    class Config:
        from_attributes = True
