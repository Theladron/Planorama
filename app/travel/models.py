from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, JSON, ForeignKey
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.trips.models import Trip

class Travel(Base):
    __tablename__ = "travel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=False)
    from_station_id: Mapped[int] = mapped_column(Integer, nullable=False)
    to_station_id: Mapped[int] = mapped_column(Integer, nullable=False)
    method_of_transport: Mapped[str] = mapped_column(String(100), nullable=False)
    cost_euros: Mapped[float] = mapped_column(Float, nullable=True)
    travel_route_description: Mapped[dict] = mapped_column(JSON, nullable=False)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="travels")
