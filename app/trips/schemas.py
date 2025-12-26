from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from typing import List, Optional
from datetime import date


class TripBase(BaseModel):
    trip_name: str
    trip_countries: List[str] = []
    start_date: date
    end_date: date


class TripCreate(TripBase):
    @field_validator('trip_name')
    def name_must_not_be_empty(cls, trip_name):
        if not trip_name or not trip_name.strip():
            raise ValueError('Trip name must not be empty')
        if len(trip_name.strip()) < 3:
            raise ValueError('Trip name must be at least 3 characters long')
        return trip_name.strip()

    @model_validator(mode='before')
    def check_dates(cls, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise ValueError('start_date must be before end_date')
        return data



class TripSchema(TripBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: date

class TripUpdate(BaseModel):
    trip_name: Optional[str] = None
    trip_countries: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None