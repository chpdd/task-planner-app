from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from typing import TYPE_CHECKING

from src.core.database import Base

if TYPE_CHECKING:
    from src.models import Allocation, Task


class FailedTask(Base):
    __tablename__ = "failed_tasks"
    __table_args__ = (
        UniqueConstraint("allocation_id", "task_id", name="unique_allocation_failed_task"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    allocation_id: Mapped[int] = mapped_column(ForeignKey("allocations.id", ondelete="CASCADE"), index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), index=True)

    allocation: Mapped["Allocation"] = relationship("Allocation")
    task: Mapped["Task"] = relationship("Task")
