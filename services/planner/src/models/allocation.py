import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

ALLOCATION_TYPE_CODES: tuple[str, ...] = (
    "interest",
    "importance",
    "interest_importance",
    "points_allocation",
    "force_procrastinate",
)

if TYPE_CHECKING:
    from src.models import Calendar, TaskExecution


class AllocationType(Base):
    __tablename__ = "allocation_types"

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)


class Allocation(Base):
    __tablename__ = "allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128))
    type: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("allocation_types.code"),
        default="points_allocation",
    )
    day_limits: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    calendar_id: Mapped[int] = mapped_column(ForeignKey("calendars.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.utcnow)

    calendar: Mapped["Calendar"] = relationship("Calendar", back_populates="allocations")
    allocation_type: Mapped["AllocationType"] = relationship("AllocationType")
    task_executions: Mapped[list["TaskExecution"]] = relationship(
        "TaskExecution",
        back_populates="allocation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
