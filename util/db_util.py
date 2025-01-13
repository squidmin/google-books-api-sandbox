import sqlite3


def init_db():
    """Initialize the database by creating the table if it doesn't exist."""
    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()

    # Drop the table if it exists, so we can recreate it with the correct schema
    cursor.execute("DROP TABLE IF EXISTS books")  # Comment this line to keep the existing table between runs

    # Create the books table with the filename column
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        title TEXT NOT NULL,
        isbn TEXT NOT NULL,
        canonical_volume_link TEXT NOT NULL,
        thumbnail TEXT NOT NULL,
        small_thumbnail TEXT NOT NULL,
        UNIQUE(title, isbn)
    )
    ''')

    conn.commit()
    conn.close()


def insert_book_to_db(title, filename, isbn, canonical_volume_link, thumbnail, small_thumbnail):
    """Insert a book and its ISBN into the SQLite database if not already present."""
    if not isbn:
        print(f"Invalid ISBN for book {title}. Skipping insertion.")  # Debugging
        return  # Skip invalid ISBNs

    isbn = str(isbn)  # Ensure ISBN is a string

    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()

    try:
        print(f"Inserting book into the database: {filename}; {title}; {isbn}; {canonical_volume_link}; {thumbnail}")
        cursor.execute("""
        INSERT OR REPLACE INTO books (
                filename,
                title,
                isbn,
                canonical_volume_link,
                thumbnail,
                small_thumbnail
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (filename,
              title,
              isbn,
              canonical_volume_link,
              thumbnail,
              small_thumbnail))
        conn.commit()
        print(f"Book inserted successfully: {title}")
    except sqlite3.InterfaceError as e:
        print(f"Error inserting {title} with ISBN {isbn}: {e}")  # Debugging
    finally:
        conn.close()


def get_books_from_db():
    """Retrieve all books from the database."""
    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT
        filename,
        title,
        isbn,
        canonical_volume_link,
        thumbnail,
        small_thumbnail
    FROM books
    """)
    books = cursor.fetchall()
    conn.close()
    return books


def get_book_by_title(title):
    """Retrieve a book from the database by title."""
    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT filename,
               title,
               isbn,
               canonical_volume_link,
               thumbnail,
               small_thumbnail
        FROM books
        WHERE title = ?
        """,
                   (title,)
                   )
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "filename": result[0],
            "title": result[1],
            "isbn": result[2],
            "canonical_volume_link": result[3],
            "thumbnail": result[4],
            "small_thumbnail": result[5]
        }
    return None


def get_isbn_by_title(title):
    """Retrieve ISBN for a given title from the database."""
    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT isbn FROM books WHERE title = ?", (title,))
    result = cursor.fetchone()
    conn.close()
    # Ensure it returns a valid ISBN or None
    return result[0] if result else None
