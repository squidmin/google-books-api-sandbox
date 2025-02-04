import os
from urllib.parse import quote_plus

import requests

from util.db_util import insert_book_to_db, get_isbn_by_title


def get_book_info_by_title(title: str) -> dict:
    """Fetch book info including ISBN from Google Books API based on book title."""
    url_encoded_title = quote_plus(title)
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{url_encoded_title}&maxResults=1&key={os.getenv('GOOGLE_BOOKS_API_KEY')}"
    print(f"Fetching ISBN for: {url_encoded_title} | URL: {url}")  # Debugging: Log the request URL
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data for {url_encoded_title}. Status code: {response.status_code}")
        return {}

    data = response.json()
    print(f"API response for {url_encoded_title}: {data}")  # Debugging: Print raw response

    # Extract the ISBN (13 digits)
    book_info = {}
    if "items" in data:
        for item in data["items"]:
            volume_info = item.get("volumeInfo", {})
            industry_identifiers = volume_info.get("industryIdentifiers", [])
            isbn = None
            subtitle = None
            if subtitle in volume_info:
                subtitle = volume_info["subtitle"]
            authors = volume_info["authors"]
            publisher = volume_info["publisher"]
            published_date = volume_info["publishedDate"]
            description = volume_info["description"]
            page_count = volume_info["pageCount"]
            categories = volume_info["categories"]
            average_rating = None
            if "averageRating" in volume_info:
                average_rating = volume_info["averageRating"]
            ratings_count = None
            if "ratingsCount" in volume_info:
                ratings_count = volume_info["ratingsCount"]
            image_links = volume_info["imageLinks"]
            language = volume_info["language"]
            preview_link = volume_info["previewLink"]
            info_link = volume_info["infoLink"]
            canonical_volume_link = volume_info["canonicalVolumeLink"]

            # Default to empty string if canonical_volume_link is None
            if not canonical_volume_link:
                canonical_volume_link = ""

            if not image_links:
                image_links = {"thumbnail": ""}
            thumbnail = image_links["thumbnail"]
            small_thumbnail = image_links["smallThumbnail"]

            for identifier in industry_identifiers:
                if identifier["type"] == "ISBN_13":
                    isbn = identifier["identifier"]
                    book_info = {
                        "isbn": isbn,
                        "title": title,
                        "subtitle": subtitle,
                        "authors": authors,
                        "publisher": publisher,
                        "published_date": published_date,
                        "description": description,
                        "page_count": page_count,
                        "categories": categories,
                        "average_rating": average_rating,
                        "ratings_count": ratings_count,
                        "image_links": image_links,
                        "thumbnail": thumbnail,
                        "small_thumbnail": small_thumbnail,
                        "language": language,
                        "preview_link": preview_link,
                        "info_link": info_link,
                        "canonical_volume_link": canonical_volume_link,
                    }

                    existing_isbn = get_isbn_by_title(title)

                    if existing_isbn != isbn:
                        # Insert book into the database if it's not already present
                        insert_book_to_db(
                            title,
                            url_encoded_title,
                            isbn,
                            canonical_volume_link,
                            thumbnail,
                            small_thumbnail,
                            description
                        )

    return book_info
