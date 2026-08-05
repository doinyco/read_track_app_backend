from flask import Blueprint, jsonify, request
import requests
import os
from app.services.s3_service import upload_book_cover

book_bp = Blueprint(
   "books",
   __name__,
   url_prefix="/books"
)


@book_bp.route("/search")
def search_books():
   query = request.args.get("q")

   if not query:
       return jsonify({
           "error": "Search query required"
       }), 400

   API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

   url = (
           "https://www.googleapis.com/books/v1/volumes"
           f"?q=intitle:{query}"
           "&maxResults=20"
           f"&key={API_KEY}"
       )

   response = requests.get(url)

   if response.status_code != 200:
       return jsonify({
           "error": response.text
       }), response.status_code

   data = response.json()
   books = []

   search_query  = query.lower().strip()

   for item in data.get("items", []):
    volume = item.get("volumeInfo", {})
    isbn = None

    for identifier in volume.get("industryIdentifiers", []):
        if identifier.get("type") == "ISBN_13":
            isbn = identifier.get("identifier")
            break

    title = volume.get("title")

    if not title:
        continue

    title_lower = title.lower()

    score = 0

    if title_lower == search_query:
        score = 100

    elif title_lower.startswith(search_query):
        score = 80

    elif search_query in title_lower:
        score = 60

    else:
        continue

    image_url = (
        volume
        .get("imageLinks", {})
        .get("thumbnail")
    )

    if not image_url:
        continue

    # Google sometimes returns http instead of https
    image_url = image_url.replace(
        "http://",
        "https://"
    )

    # Download cover image
    image_response = requests.get(image_url)

    if image_response.status_code != 200:
        continue

    # Use Google Books ID as filename
    # Same book = same S3 key
    google_id = item.get("id")


    filename = f"{google_id}.jpg"

    # Upload only if missing
    #    cover_url = upload_book_cover(
    #        image_response.content,
    #        filename
    #    )

    # Try to upload to S3, but fall back to Google's URL if it fails
    try:
        cover_url = upload_book_cover(
            image_response.content,
            filename
        )
    except Exception as e:
        print(f"S3 upload failed: {e}, using Google Books URL instead")
        cover_url = image_url  # Use Google Books thumbnail as fallback

    books.append({
           "score": score,
           "google_id": item.get("id"),
           "title": title,
           "author": volume.get("authors", ["Unknown"])[0],
           "isbn": isbn,
           "total_pages": volume.get("pageCount", 0),
           "description": volume.get("description"),
           "cover_image_url": cover_url,
           "source": "google_books"
    })

   books.sort(
       key=lambda x: x["score"],
       reverse=True
   )

   return jsonify(books[:10])