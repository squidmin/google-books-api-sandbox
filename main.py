import sqlite3

from flask import Flask, jsonify, send_from_directory, request, render_template
from flask_httpauth import HTTPBasicAuth
from gevent.pywsgi import WSGIServer
from werkzeug.security import check_password_hash

import config
import json
from urllib.parse import quote_plus
from util import fromdir
from util.db_util import init_db, insert_book_to_db, get_book_by_title
from util.google_books_util import get_book_info_by_title

app = Flask(__name__, static_url_path="", static_folder="static")
auth = HTTPBasicAuth()

books_cache = {}


# @app.route("/catalog")
# @app.route("/catalog/<path:path>")
# @auth.login_required
# def catalog(path=""):
#     view_mode = request.args.get("view", "list")  # default to 'list' view
#     c = fromdir(request.root_url, request.url, config.CONTENT_BASE_DIR, path)
#
#     # Read the catalog entries from the sample JSON payload
#     catalog_entries = []
#     try:
#         with open('./docs/sample_payloads/catalog_entries.json', 'r') as json_file:
#             catalog_entries = json.load(json_file)
#             print(f"Catalog entries loaded from file: {len(catalog_entries)} entries found.")
#     except Exception as e:
#         print(f"Error reading catalog entries from file: {e}")
#
#     # You can still include any processing logic if needed
#     # For example, you might want to do additional transformations or checks on catalog_entries.
#
#     return c.render(view_mode=view_mode, catalog_entries=catalog_entries, loading=True)


@app.route("/catalog")
@app.route("/catalog/<path:path>")
@auth.login_required
def catalog(path=""):
    view_mode = request.args.get("view", "list")  # default to 'list' view
    c = fromdir(request.root_url, request.url, config.CONTENT_BASE_DIR, path)

    catalog_entries = []
    for entry in c.entries:
        title = entry.title
        book_info = None
        if title in books_cache:
            book_info = books_cache[title]
        if not book_info:  # If the book info is not in the cache, check the database
            book_info = get_book_by_title(title)
            print(f"Book info from database: {book_info}")
        if not book_info:  # If no info is found, fetch it from Google Books API
            book_info = get_book_info_by_title(title)
            print(f"Book info from Google Books API: {book_info}")
        if book_info:
            books_cache[title] = book_info  # Cache the book info
            insert_book_to_db(
                book_info["title"],
                quote_plus(title),
                book_info["isbn"],
                book_info["canonical_volume_link"],
                book_info["thumbnail"],
                book_info["small_thumbnail"],
                book_info["description"],
            )  # Insert into database if new

        entry.isbn = book_info["isbn"] if book_info else []
        entry.canonical_volume_link = book_info["canonical_volume_link"] if book_info else ""
        entry.thumbnail = book_info["thumbnail"] if book_info else ""
        entry.small_thumbnail = book_info["small_thumbnail"] if book_info else ""
        entry.description = book_info["description"] if book_info else ""

        # Convert entry to dictionary before appending
        catalog_entries.append(entry.to_dict())

    return c.render(view_mode=view_mode, catalog_entries=catalog_entries, loading=True)


@app.route("/view_books")
@auth.login_required
def view_books():
    """Display books from the database in an HTML table."""
    try:
        conn = sqlite3.connect('ebooks.db')
        cursor = conn.cursor()

        cursor.execute("SELECT filename, title, isbn, canonical_volume_link, thumbnail, description FROM books")
        books = cursor.fetchall()

        conn.close()

        return render_template("view_books.html", books=books)

    except Exception as e:
        print(f"Error fetching books: {e}")
        return jsonify({"error": "Failed to retrieve books from the database"}), 500


@app.route("/check_and_update_books", methods=["POST"])
def check_and_update_books():
    """Check all book titles for ISBNs and update the memory if necessary."""
    try:
        books_data = request.get_json()["books_data"]

        books_to_check = [str(book) for book in books_data]

        for title in books_to_check:
            if title not in books_cache:
                # Fetch the ISBN if it's not in the cache or database
                isbns = get_book_info_by_title([title])
                if isbns:
                    books_data[title] = isbns
                else:
                    books_data[title] = []  # No ISBN found

        print(f"Books data to be saved: {books_data}")
        print("ISBN data updated.")

        return jsonify({"message": "ISBN data successfully updated"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to update ISBN data"}), 500


@app.route("/isbn_lookup", methods=["POST"])
def isbn_lookup():
    """Endpoint to get ISBNs for a list of book titles."""
    try:
        request_data = request.get_json()
        book_titles = request_data.get("book_titles", [])

        if not book_titles:
            return jsonify({"error": "No book titles provided"}), 400

        result = {}
        for title in book_titles:
            if title in books_cache and books_cache[title]:
                result[title] = books_cache[title]
            else:
                isbns = get_book_info_by_title([title])
                result[title] = isbns
                books_cache[title] = isbns

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth.verify_password
def verify_password(username, password):
    if not config.READOPS_ADMIN_PASSWORD:
        return True
    elif username in config.users and check_password_hash(
            config.users.get(username), password
    ):
        return username


@app.route("/")
@app.route("/health")
def health():
    return "ok"


@app.route("/content/<path:path>")
@auth.login_required
def send_content(path):
    return send_from_directory(config.CONTENT_BASE_DIR, path)


if __name__ == "__main__":
    init_db()
    http_server = WSGIServer(("", 5000), app)
    http_server.serve_forever()
