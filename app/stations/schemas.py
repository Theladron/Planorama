from pydantic import BaseModel, ConfigDict

class StationBase(BaseModel):
    station_name: str

class StationCreate(StationBase):
    trip_id: int
    day_number: int

class StationSchema(StationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    station_name_de: str
    latitude: float
    longitude: float
    country: str


class StationWithLinkIdSchema(StationSchema):
    model_config = ConfigDict(from_attributes=True)
    
    link_id: int
    day_number: int
