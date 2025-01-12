import sqlite3


def init_db():
    """Initialize the database by creating the table if it doesn't exist."""
    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()

    # Drop the table if it exists, so we can recreate it with the correct schema
    cursor.execute("DROP TABLE IF EXISTS books")

    # Create the books table with the filename column
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        title TEXT NOT NULL,
        isbn TEXT NOT NULL,
        UNIQUE(title, isbn)
    )
    ''')

    conn.commit()
    conn.close()


def insert_book_to_db(title, filename, isbn):
    """Insert a book and its ISBN into the SQLite database if not already present."""
    if not isbn:
        print(f"Invalid ISBN for book {title}. Skipping insertion.")  # Debugging
        return  # Skip invalid ISBNs

    # Ensure ISBN is a string
    isbn = str(isbn)

    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()
    try:
        print(f"Inserting book into the database: {filename}; {title}; {isbn}")
        cursor.execute('''
            INSERT OR IGNORE INTO books (filename, title, isbn)
            VALUES (?, ?, ?)
        ''', (filename, title, isbn))  # Make sure filename is being inserted
        conn.commit()
    except sqlite3.InterfaceError as e:
        print(f"Error inserting {title} with ISBN {isbn}: {e}")  # Debugging
    finally:
        conn.close()


def get_books_from_db():
    """Retrieve all books from the database."""
    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT filename, title, isbn FROM books")
    books = cursor.fetchall()
    conn.close()
    return books


def get_isbn_from_db(title):
    """Retrieve ISBN for a given title from the database."""
    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT isbn FROM books WHERE title = ?", (title,))
    result = cursor.fetchone()
    conn.close()
    # Ensure it returns a valid ISBN or None
    return result[0] if result else None
