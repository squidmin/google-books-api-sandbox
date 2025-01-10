import config
import os
import requests
from flask import Flask, jsonify, send_from_directory, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from gevent.pywsgi import WSGIServer
from urllib.parse import quote_plus

app = Flask(__name__)

app = Flask(__name__, static_url_path="", static_folder="static")
auth = HTTPBasicAuth()

CONTENT_BASE_DIR = '/library'

books_cache = {}


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
                isbns = get_isbn_from_google_books(title)
                result[title] = isbns
                books_cache[title] = isbns

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_isbn_from_google_books(title):
    """Fetch ISBN from Google Books API based on book title."""
    title = quote_plus(title)
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}&maxResults=1&key={os.getenv('GOOGLE_BOOKS_API_KEY')}"
    print(f"Fetching ISBN for: {title} | URL: {url}")  # Debugging: Log the request URL
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data for {title}. Status code: {response.status_code}")
        return []

    data = response.json()
    print(f"API response for {title}: {data}")  # Debugging: Print raw response

    # Extract the ISBN (13 digits)
    isbn_list = []
    if "items" in data:
        for item in data["items"]:
            volume_info = item.get("volumeInfo", {})
            industry_identifiers = volume_info.get("industryIdentifiers", [])
            for identifier in industry_identifiers:
                if identifier["type"] == "ISBN_13":
                    isbn_list.append(identifier["identifier"])

    if not isbn_list:
        print(f"No ISBN found for {title}")  # Debugging: Log if no ISBN is found
    return isbn_list


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
    http_server = WSGIServer(("", 5000), app)
    http_server.serve_forever()
