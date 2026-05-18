import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import settings
from src.core.database import Base

if TYPE_CHECKING:
    from src.models import Calendar, TaskExecution


class Day(Base):
    __tablename__ = "days"
    __table_args__ = (
        CheckConstraint("0 <= work_hours AND work_hours <= 24", name="check_work_hours_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[dt.date] = mapped_column()
    work_hours: Mapped[int] = mapped_column(default=settings.default_day_work_hours)
    calendar_id: Mapped[int] = mapped_column(
        ForeignKey("calendars.id", ondelete="CASCADE"), index=True
    )

    calendar: Mapped["Calendar"] = relationship("Calendar", back_populates="days")
    task_executions: Mapped[list["TaskExecution"]] = relationship(
        "TaskExecution", back_populates="day",
        cascade="all, delete-orphan", passive_deletes=True
    )
