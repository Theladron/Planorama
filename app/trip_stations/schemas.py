from pydantic import BaseModel, ConfigDict
from typing import List


class TripStationBase(BaseModel):
    trip_id: int
    station_id: int
    day_number: int


class TripStationCreate(TripStationBase):
    pass


class TripStationSchema(TripStationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class TripStationReorderItem(BaseModel):
    link_id: int
    day_number: int


class TripStationsReorderRequest(BaseModel):
    trip_id: int
    stations: List[TripStationReorderItem]
