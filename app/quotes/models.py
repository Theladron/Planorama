from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text
from app.core.database import Base

class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quote: Mapped[str] = mapped_column(Text, nullable=False)
