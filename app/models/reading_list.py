from sqlalchemy.orm import Mapped, mapped_column
from ..db import db
from sqlalchemy import DateTime, Enum, ForeignKey
import enum
from datetime import datetime, timezone

class ReadingStatus(enum.Enum):
    WANT_TO_READ = "want_to_read"
    CURRENTLY_READING = "currently_reading"
    COMPLETED = "completed"

class ReadingList(db.Model):
    __tablename__ = "reading_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    status: Mapped[ReadingStatus] = mapped_column(Enum(ReadingStatus), nullable=False)
    date_added: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    date_started: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    date_completed: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)