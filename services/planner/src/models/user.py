from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.models import AIConversation, Calendar, ManualDay, Task


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    hashed_password: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    # Direct ownership
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="owner", cascade="all, delete-orphan",
                                               passive_deletes=True)
    manual_days: Mapped[list["ManualDay"]] = relationship("ManualDay", back_populates="owner",
                                                          cascade="all, delete-orphan", passive_deletes=True)
    # Calendar ownership (new - Day/TaskExecution owned through Calendar->Allocation chain)
    calendars: Mapped[list["Calendar"]] = relationship("Calendar", back_populates="owner",
                                                       cascade="all, delete-orphan", passive_deletes=True)
    ai_conversations: Mapped[list["AIConversation"]] = relationship(
        "AIConversation",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
