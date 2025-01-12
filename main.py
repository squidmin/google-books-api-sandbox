import sqlite3

from flask import Flask, jsonify, send_from_directory, request
from flask_httpauth import HTTPBasicAuth
from gevent.pywsgi import WSGIServer
from werkzeug.security import check_password_hash

import config
from urllib.parse import quote_plus
from util import fromdir
from util.db_util import init_db, insert_book_to_db, get_isbn_from_db
from util.google_books_util import get_isbn_by_title

app = Flask(__name__, static_url_path="", static_folder="static")
auth = HTTPBasicAuth()

books_cache = {}


@app.route("/catalog")
@app.route("/catalog/<path:path>")
@auth.login_required
def catalog(path=""):
    view_mode = request.args.get("view", "list")  # default to 'list' view
    c = fromdir(request.root_url, request.url, config.CONTENT_BASE_DIR, path)

    catalog_entries = []
    for entry in c.entries:
        title = entry.title
        isbn = None
        if title in books_cache:
            isbn = books_cache[title]
        if not isbn:  # If the ISBN is not in the cache, check the database
            isbn = get_isbn_from_db(title)
            print(f"ISBN FROM DB: {isbn}")

            # If no ISBN is found in cache or database, fetch from Google Books API
        if not isbn:
            isbn = get_isbn_by_title(title)
            if isbn:
                print(f"ISBN FROM GOOGLE BOOKS: {isbn}")
                books_cache[title] = isbn  # Cache fetched ISBN
                insert_book_to_db(title, quote_plus(title), isbn)  # Insert into database if new

        entry.isbn = isbn if isbn else []  # Ensure the ISBN field is updated with the correct value
        catalog_entries.append(entry)

    return c.render(view_mode=view_mode, catalog_entries=catalog_entries, loading=True)


@app.route("/view_books")
@auth.login_required
def view_books():
    """Display books from the database in an HTML table."""
    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT filename, title, isbn FROM books")
    books = cursor.fetchall()
    conn.close()

    # Render the results as an HTML table
    html = "<h1>books</h1><table border='1'><tr><th>Filename</th><th>Title</th><th>ISBN</th></tr>"
    for book in books:
        html += f"<tr><td>{book[0]}</td><td>{book[1]}</td><td>{book[2]}</td></tr>"
    html += "</table>"

    return html


@app.route("/check_and_update_books", methods=["POST"])
def check_and_update_books():
    """Check all book titles for ISBNs and update the memory if necessary."""
    try:
        books_data = request.get_json()["books_data"]

        # Example book titles to update or check
        books_to_check = [str(book) for book in books_data]

        # Check for each title if it exists in the database
        for title in books_to_check:
            if title not in books_cache:
                # Fetch the ISBN if it's not in the cache or database
                isbns = get_isbn_by_title([title])
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
                isbns = get_isbn_by_title([title])
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
