from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.trip_stations.models import TripStation

class Station(Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_name: Mapped[str] = mapped_column(String(100), nullable=False)
    station_name_de: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)

    trip_stations: Mapped[list["TripStation"]] = relationship("TripStation",
                                                              back_populates="station",
                                                              cascade="all, delete-orphan")