from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, JSON, Date, ForeignKey, func
from datetime import date
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.users.models import User
    from app.travel.models import Travel
    from app.activities.models import Activity
    from app.trip_stations.models import TripStation

class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    trip_name: Mapped[str] = mapped_column(String(100), nullable=False)
    trip_countries: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[date] = mapped_column(Date, server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="trips")
    travels: Mapped[list["Travel"]] = relationship("Travel", back_populates="trip",
                                                   cascade="all, delete-orphan")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="trip",
                                                        cascade="all, delete-orphan")
    trip_stations: Mapped[list["TripStation"]] = relationship("TripStation", back_populates="trip",
                                                              cascade="all, delete-orphan")