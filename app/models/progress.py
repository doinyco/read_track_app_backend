from sqlalchemy.orm import Mapped, mapped_column
from ..db import db
from sqlalchemy import DateTime, ForeignKey
from datetime import datetime, timezone

# Relationships
# Many-to-One -> ReadingList (a progress update belongs to one reading list entry)

class Progress(db.Model):
    __tablename__ = "progress"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    reading_list_id: Mapped[int] = mapped_column(ForeignKey("reading_lists.id"))
    pages_read: Mapped[int] = mapped_column(nullable=False)
    percentage_completed: Mapped[float] = mapped_column(nullable=False)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )