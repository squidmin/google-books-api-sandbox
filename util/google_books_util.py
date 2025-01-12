import os
from urllib.parse import quote_plus

import requests

from util.db_util import insert_book_to_db


def get_isbn_by_title(title: str) -> []:
    """Fetch ISBN from Google Books API based on book title."""
    url_encoded_title = quote_plus(title)
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{url_encoded_title}&maxResults=1&key={os.getenv('GOOGLE_BOOKS_API_KEY')}"
    print(f"Fetching ISBN for: {url_encoded_title} | URL: {url}")  # Debugging: Log the request URL
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data for {url_encoded_title}. Status code: {response.status_code}")
        return []

    data = response.json()
    print(f"API response for {url_encoded_title}: {data}")  # Debugging: Print raw response

    # Extract the ISBN (13 digits)
    isbn_list = []
    if "items" in data:
        for item in data["items"]:
            volume_info = item.get("volumeInfo", {})
            industry_identifiers = volume_info.get("industryIdentifiers", [])
            for identifier in industry_identifiers:
                if identifier["type"] == "ISBN_13":
                    identifier_ = identifier["identifier"]
                    isbn_list.append(identifier_)

                    # Insert book data into the database (avoid duplicates)
                    insert_book_to_db(title, url_encoded_title, identifier_)

    return isbn_list[0] if isbn_list else None  # Return the first ISBN if available
