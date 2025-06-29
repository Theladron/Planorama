from pydantic import BaseModel
from typing import Optional

class StationBase(BaseModel):
    day_number: int
    station_name: str
    location_name: str  # assuming it's used to get lat/lon from OpenRoute

class StationCreate(StationBase):
    trip_id: int

class StationUpdate(BaseModel):
    day_number: Optional[int] = None

class StationSchema(StationBase):
    id: int
    trip_id: int
    latitude: float
    longitude: float

    class Config:
        from_attributes = True