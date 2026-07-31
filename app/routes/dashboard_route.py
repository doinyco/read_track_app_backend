from flask import Blueprint, jsonify, session
from ..models.user import User
from ..models.book import Book
from ..models.reading_list import ReadingList, ReadingStatus
from ..db import db

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)
@dashboard_bp.route("", methods=["GET"])

def get_dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    reading_list = ReadingList.query.filter_by(
        user_id=user_id
    ).all()
    currently_reading = []
    completed = []
    want_to_read = []

    for entry in reading_list:
        book = Book.query.get(entry.book_id)
        book_data = {
            "reading_list_id": entry.id,
            "book_id": book.id,
            "title": book.title,
            "author": book.author,
            "cover_image_url": book.cover_image_url,
            "status": entry.status.value
        }
        if entry.status == ReadingStatus.CURRENTLY_READING:
            currently_reading.append(book_data)
        elif entry.status == ReadingStatus.COMPLETED:
            completed.append(book_data)
        elif entry.status == ReadingStatus.WANT_TO_READ:
            want_to_read.append(book_data)

    return jsonify({
        "username": user.username,
        "stats": {
            "books_read": len(completed),
            "currently_reading": len(currently_reading),
            "want_to_read": len(want_to_read)
        },
        "currently_reading": currently_reading,
        "completed_books": completed,
        "wishlist": want_to_read
    }), 200


