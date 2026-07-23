from sqlalchemy.orm import Mapped, mapped_column
from ..db import db

class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    # isbn is a unique identifier for books, we want to ensure that no two books in our database have the same ISBN
    isbn: Mapped[str] = mapped_column(unique=True, nullable=False)
    # cover_image_url is optional, as not all books may have a cover image available (this could point to an S3 bucket or a local file path)
    cover_image_url: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    total_pages: Mapped[int] = mapped_column(nullable=False)
    source: Mapped[str] = mapped_column(nullable=False)