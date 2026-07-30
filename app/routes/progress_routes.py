from flask import Blueprint, request, jsonify
from ..db import db
from ..models.book import Book
from ..models.reading_list import ReadingList
from ..models.progress import Progress

bp = Blueprint("progress", __name__, url_prefix="/reading-list")


# route to log a progress update for a book in the user's library
@bp.route("/books/<int:reading_list_id>/progress", methods=["POST"])
def add_progress(reading_list_id):
    entry = ReadingList.query.get(reading_list_id)

    if not entry:
        return jsonify({"error": "Reading list entry not found"}), 404

    data = request.get_json()
    pages_read = data.get("pages_read")

    if pages_read is None:
        return jsonify({"error": "pages_read is required"}), 400

    book = Book.query.get(entry.book_id)

    if pages_read < 0 or pages_read > book.total_pages:
        return jsonify({"error": f"pages_read must be between 0 and {book.total_pages}"}), 400

    percentage_completed = round((pages_read / book.total_pages) * 100, 2)

    progress = Progress(
        reading_list_id=reading_list_id,
        pages_read=pages_read,
        percentage_completed=percentage_completed,
    )
    db.session.add(progress)
    db.session.commit()

    return jsonify({
        "message": "Progress logged",
        "progress_id": progress.id,
        "reading_list_id": reading_list_id,
        "pages_read": progress.pages_read,
        "percentage_completed": progress.percentage_completed,
        "logged_at": progress.logged_at.isoformat(),
    }), 201

#route to get the latest progress update for a book in the user's library
@bp.route("/books/<int:reading_list_id>/progress/latest", methods=["GET"])
def get_latest_progress(reading_list_id):
    entry = ReadingList.query.get(reading_list_id)
    if not entry:
        return jsonify({"error": "Reading list entry not found"}), 404

    latest = Progress.query.filter_by(reading_list_id=reading_list_id) \
                            .order_by(Progress.logged_at.desc()).first()

    if not latest:
        return jsonify({"message": "No progress logged yet"}), 200

    return jsonify({
        "progress_id": latest.id,
        "pages_read": latest.pages_read,
        "percentage_completed": latest.percentage_completed,
        "logged_at": latest.logged_at.isoformat(),
    }), 200

# route to get the full progress history for a book in the user's library
@bp.route("/books/<int:reading_list_id>/progress", methods=["GET"])
def get_progress_history(reading_list_id):
    entry = ReadingList.query.get(reading_list_id)

    if not entry:
        return jsonify({"error": "Reading list entry not found"}), 404

    history = Progress.query.filter_by(reading_list_id=reading_list_id) \
                            .order_by(Progress.logged_at.asc()).all()

    return jsonify([{
        "progress_id": p.id,
        "pages_read": p.pages_read,
        "percentage_completed": p.percentage_completed,
        "logged_at": p.logged_at.isoformat(),
    } for p in history]), 200

@bp.route("/progress/<int:progress_id>", methods=["DELETE"])
def delete_progress(progress_id):
    progress = Progress.query.get(progress_id)
    if not progress:
        return jsonify({"error": "Progress entry not found"}), 404
    db.session.delete(progress)
    db.session.commit()
    return jsonify({"message": "Progress entry deleted"}), 200