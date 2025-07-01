from pydantic import BaseModel
from typing import List, Optional

class StationBase(BaseModel):
    day_number: int
    station_name: str

class StationCreate(StationBase):
    trip_id: int

class StationReorderItem(BaseModel):
    station_id: int
    day_number: int

class StationSchema(StationBase):
    id: int
    trip_id: int
    latitude: float
    longitude: float
    country: Optional[str] = None

    class Config:
        from_attributes = True

class StationsReorderRequest(BaseModel):
    trip_id: int
    stations: List[StationReorderItem]
