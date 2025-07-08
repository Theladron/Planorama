from pydantic import BaseModel

class StationBase(BaseModel):
    station_name: str

class StationCreate(StationBase):
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


class StationWithLinkIdSchema(StationSchema):
    link_id: int
    day_number: int

    class Config:
        from_attributes = True
