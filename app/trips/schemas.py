from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from datetime import date


class TripBase(BaseModel):
    trip_name: str
    trip_countries: List[str] = []
    start_date: date
    end_date: date


class TripCreate(TripBase):
    @field_validator('trip_name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Trip name must not be empty')
        if len(v.strip()) < 3:
            raise ValueError('Trip name must be at least 3 characters long')
        return v.strip()

    @model_validator(mode='before')
    def check_dates(cls, values):
        start = values.get('start_date')
        end = values.get('end_date')
        if start and end and start > end:
            raise ValueError('start_date must be before end_date')
        return values



class TripSchema(TripBase):
    id: int
    user_id: int
    created_at: date

    class Config:
        from_attributes = True

class TripUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None