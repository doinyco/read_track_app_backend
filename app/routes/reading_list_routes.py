from flask import Blueprint, request, jsonify, session
from ..db import db
from ..models.book import Book
from ..models.reading_list import ReadingList, ReadingStatus
from datetime import datetime, timezone

bp = Blueprint("reading_list", __name__, url_prefix="/reading-list")

# route to add a book to the user's library
@bp.route("/library/books", methods=["POST"])
def add_book_to_library():
    data = request.get_json()

    user_id = session.get("user_id")
    isbn = data.get("isbn")
    title = data.get("title")
    author = data.get("author")
    total_pages = data.get("total_pages")

    missing = [f for f in ("isbn", "title", "author")
               if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # query the database to see if the book already exists, based on the ISBN. If it doesn't exist, create a new book entry.
    book = Book.query.filter_by(isbn=isbn).first()

    if not book:
        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            cover_image_url=data.get("cover_image_url"),
            description=data.get("description"),
            total_pages=total_pages,
            source=data.get("source", "user_added"),
        )
        db.session.add(book)
        db.session.flush()

    # Check if the book is already in the user's library
    existing_entry = ReadingList.query.filter_by(user_id=user_id, book_id=book.id).first()
    if existing_entry:
        return jsonify({"error": "Book already in your library"}), 409

    entry = ReadingList(
        user_id=user_id,
        book_id=book.id,
        status=ReadingStatus.WANT_TO_READ,
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "message": "Book added to library",
        "book_id": book.id,
        "reading_list_id": entry.id,
    }), 201

# route to get a specific book in a user's library by reading_list_id
@bp.route("/books/<int:reading_list_id>", methods=["GET"])
def get_reading_list_entry(reading_list_id):
    entry = ReadingList.query.get(reading_list_id)

    if not entry:
        return jsonify({"error": "Reading list entry not found"}), 404

    book = Book.query.get(entry.book_id)

    return jsonify({
        "reading_list_id": entry.id,
        "book_id": book.id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "total_pages": book.total_pages,
        "cover_image_url": book.cover_image_url,
        "description": book.description,
        "status": entry.status.value,
        "date_added": entry.date_added.isoformat(),
        "date_started": entry.date_started.isoformat() if entry.date_started else None,
        "date_completed": entry.date_completed.isoformat() if entry.date_completed else None,
    }), 200

# route to get all books in a user's library
@bp.route("/library/books", methods=["GET"])
def get_user_library():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    entries = ReadingList.query.filter_by(user_id=user_id).all()

    result = []
    for entry in entries:
        book = Book.query.get(entry.book_id)
        result.append({
            "reading_list_id": entry.id,
            "book_id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "total_pages": book.total_pages,
            "cover_image_url": book.cover_image_url,
            "status": entry.status.value,
            "date_added": entry.date_added.isoformat(),
            "date_started": entry.date_started.isoformat() if entry.date_started else None,
            "date_completed": entry.date_completed.isoformat() if entry.date_completed else None,
        })

    return jsonify(result), 200

# route to update the reading status of a book in the user's library
@bp.route("/books/<int:reading_list_id>", methods=["PATCH"])
def update_reading_status(reading_list_id):
    entry = ReadingList.query.get(reading_list_id)

    # Check if the entry exists
    if not entry:
        return jsonify({"error": "Reading list entry not found"}), 404

    data = request.get_json()
    new_status = data.get("status")

    # Validate the new status
    if new_status not in [s.value for s in ReadingStatus]:
        return jsonify({"error": "Invalid status value"}), 400

    entry.status = ReadingStatus(new_status)

    # Auto-set timestamps based on the status change
    if entry.status == ReadingStatus.CURRENTLY_READING and not entry.date_started:
        entry.date_started = datetime.now(timezone.utc)
    elif entry.status == ReadingStatus.COMPLETED and not entry.date_completed:
        entry.date_completed = datetime.now(timezone.utc)

    db.session.commit()

    return jsonify({
        "message": "Status updated",
        "reading_list_id": entry.id,
        "status": entry.status.value,
        "date_started": entry.date_started.isoformat() if entry.date_started else None,
        "date_completed": entry.date_completed.isoformat() if entry.date_completed else None,
    }), 200

# route to delete a book from the user's library
@bp.route("/books/<int:reading_list_id>", methods=["DELETE"])
def delete_reading_list_entry(reading_list_id):
    entry = ReadingList.query.get(reading_list_id)

    if not entry:
        return jsonify({"error": "Reading list entry not found"}), 404

    db.session.delete(entry)
    db.session.commit()

    return jsonify({
        "message": "Book removed from library",
        "reading_list_id": reading_list_id,
    }), 200