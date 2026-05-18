import datetime as dt
import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models import Calendar, TaskExecution


class AllocationType(str, enum.Enum):
    EVEN = "even"
    PRIORITY = "priority"
    COMPACT = "compact"


class Allocation(Base):
    __tablename__ = "allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128))
    type: Mapped[AllocationType] = mapped_column(
        SQLEnum(AllocationType, name="allocation_type_enum", create_type=False),
        default=AllocationType.EVEN,
    )
    day_limits: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    calendar_id: Mapped[int] = mapped_column(ForeignKey("calendars.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[dt.datetime] = mapped_column(default=dt.datetime.utcnow)

    calendar: Mapped["Calendar"] = relationship("Calendar", back_populates="allocations")
    task_executions: Mapped[list["TaskExecution"]] = relationship(
        "TaskExecution",
        back_populates="allocation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
