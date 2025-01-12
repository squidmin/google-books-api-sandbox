import sqlite3


def init_db():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()

    # Clear the books table each time the application starts
    cursor.execute("DELETE FROM books")  # This clears the table

    # Re-create the table (if needed, to ensure schema is correct)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        isbn TEXT NOT NULL,
        UNIQUE(title, isbn)
    )
    ''')

    conn.commit()
    conn.close()


def insert_book_to_db(title, isbn):
    """Insert a book and its ISBN into the SQLite database if not already present."""
    if not isbn:
        print(f"Invalid ISBN for book {title}. Skipping insertion.")  # Debugging
        return  # Skip invalid ISBNs

    # Ensure ISBN is a string
    isbn = str(isbn)

    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()
    try:
        print(f"Inserting book into the database: {title}; {isbn}")
        cursor.execute('''
            INSERT OR IGNORE INTO books (title, isbn)
            VALUES (?, ?)
        ''', (title, isbn))
        conn.commit()
    except sqlite3.InterfaceError as e:
        print(f"Error inserting {title} with ISBN {isbn}: {e}")  # Debugging
    finally:
        conn.close()


def get_books_from_db():
    """Retrieve all books from the database."""
    conn = sqlite3.connect('ebooks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, isbn FROM books")
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
