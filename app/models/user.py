from sqlalchemy.orm import Mapped, mapped_column
from ..db import db

# Relationships
# One-to-Many -> ReadingList (a user has many entries in their library)
# Progre(Progress is reached indirectly, through ReadingList

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
