from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class TripBase(BaseModel):
    trip_name: str
    trip_countries: Optional[List[str]] = None
    start_date: date
    end_date: date


class TripCreate(TripBase):
    user_id: int


class TripSchema(TripBase):
    id: int
    user_id: int
    created_at: date

    class Config:
        from_attributes = True
