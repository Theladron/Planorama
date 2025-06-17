from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, JSON, ForeignKey
from typing import TYPE_CHECKING
from app.core.database import Base

if TYPE_CHECKING:
    from app.trips.models import Trip

class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=False)
    activity_name: Mapped[str] = mapped_column(String(100), nullable=False)
    activity_website: Mapped[str] = mapped_column(String(2083), nullable=False)
    route_to_activity: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="activities")
