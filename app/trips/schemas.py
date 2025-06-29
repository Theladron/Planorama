from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class TripBase(BaseModel):
    trip_name: str
    trip_countries: List[str] = []
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

class TripUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None