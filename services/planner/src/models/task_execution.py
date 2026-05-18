from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models import Allocation, Day, Task


class TaskExecution(Base):
    __tablename__ = "task_executions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doing_hours: Mapped[int] = mapped_column()
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    day_id: Mapped[int] = mapped_column(ForeignKey("days.id", ondelete="CASCADE"))
    allocation_id: Mapped[int] = mapped_column(
        ForeignKey("allocations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    is_done: Mapped[bool] = mapped_column(default=False)

    allocation: Mapped["Allocation"] = relationship("Allocation", back_populates="task_executions", lazy="selectin")
    day: Mapped["Day"] = relationship("Day", back_populates="task_executions", lazy="selectin")
    task: Mapped["Task"] = relationship("Task", back_populates="task_executions", lazy="selectin")
