from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.trips.models import Trip
    from app.stations.models import Station

class TripStation(Base):
    __tablename__ = "trip_stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=False)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), nullable=False)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="trip_stations")
    station: Mapped["Station"] = relationship("Station", back_populates="trip_stations")

    __table_args__ = (
        UniqueConstraint('trip_id', 'station_id', 'day_number', name='uq_trip_station_day'),
    )