from pydantic import BaseModel
from typing import List


class TripStationBase(BaseModel):
    trip_id: int
    station_id: int
    day_number: int


class TripStationCreate(TripStationBase):
    pass


class TripStationSchema(TripStationBase):
    id: int

    class Config:
        from_attributes = True


class TripStationReorderItem(BaseModel):
    station_id: int
    day_number: int


class TripStationsReorderRequest(BaseModel):
    trip_id: int
    stations: List[TripStationReorderItem]