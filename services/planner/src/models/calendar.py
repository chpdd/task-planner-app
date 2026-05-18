from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models import Day, User
    from src.models.allocation import Allocation


class Calendar(Base):
    __tablename__ = "calendars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128))

    owner: Mapped["User"] = relationship("User", back_populates="calendars")
    allocations: Mapped[list["Allocation"]] = relationship("Allocation", back_populates="calendar",
                                                            cascade="all, delete-orphan", passive_deletes=True)
    days: Mapped[list["Day"]] = relationship("Day", back_populates="calendar",
                                              cascade="all, delete-orphan", passive_deletes=True)
