"""
BookDAO - Data Access Layer
All SQL operations for the Books table.
"""

from dao.db_connection import get_connection


class BookDAO:

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM books ORDER BY book_id ASC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(book_id):
        conn = get_connection()
        row = conn.execute("SELECT * FROM books WHERE book_id = ?", (book_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_isbn(isbn):
        conn = get_connection()
        row = conn.execute("SELECT * FROM books WHERE isbn = ?", (isbn,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def search(query):
        conn = get_connection()
        q = f"%{query}%"
        rows = conn.execute(
            """SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?
            ORDER BY book_id ASC""",
            (q, q, q, q)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def insert(data):
        conn = get_connection()
        conn.execute(
            """INSERT INTO books
               (isbn, title, author, publisher, publication_year, category,
                edition, language, total_copies, available_copies, shelf_location, status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (data['isbn'], data['title'], data['author'], data.get('publisher'),
             data.get('publication_year'), data.get('category'), data.get('edition'),
             data.get('language', 'English'), data['total_copies'], data['total_copies'],
             data.get('shelf_location'), 'Available')
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def update(book_id, data):
        conn = get_connection()
        current = conn.execute(
            "SELECT total_copies, available_copies FROM books WHERE book_id = ?",
            (book_id,)
        ).fetchone()

        old_total     = current['total_copies']
        old_available = current['available_copies']
        new_total     = int(data['total_copies'])

        borrowed = old_total - old_available

        new_available = max(0, new_total - borrowed)

        new_status = 'Available' if new_available > 0 else 'Issued'

        conn.execute(
            """UPDATE books SET
            isbn=?, title=?, author=?, publisher=?, publication_year=?,
            category=?, edition=?, language=?, total_copies=?,
            available_copies=?, shelf_location=?, status=?
            WHERE book_id=?""",
            (data['isbn'], data['title'], data['author'], data.get('publisher'),
            data.get('publication_year'), data.get('category'), data.get('edition'),
            data.get('language', 'English'), new_total,
            new_available, data.get('shelf_location'), new_status, book_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(book_id):
        conn = get_connection()
        conn.execute("DELETE FROM books WHERE book_id = ?", (book_id,))

        # Reorder all book_ids to close the gap
        books = conn.execute("SELECT book_id FROM books ORDER BY book_id ASC").fetchall()
        for new_id, row in enumerate(books, start=1):
            if row[0] != new_id:
                conn.execute("UPDATE books SET book_id = ? WHERE book_id = ?", (new_id, row[0]))

        # Reset the autoincrement counter to continue from the last ID
        conn.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(book_id) FROM books) WHERE name = 'books'")

        conn.commit()
        conn.close()
    
    @staticmethod
    def decrement_available(book_id):
        conn = get_connection()
        conn.execute(
            """UPDATE books
            SET available_copies = available_copies - 1,
                status = CASE WHEN available_copies - 1 <= 0 THEN 'Issued' ELSE 'Available' END
            WHERE book_id = ?""",
            (book_id,)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def increment_available(book_id):
        conn = get_connection()
        conn.execute(
            """UPDATE books
            SET available_copies = available_copies + 1,
                status = 'Available'
            WHERE book_id = ?""",
            (book_id,)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_stats():
        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) as total, SUM(available_copies) as avail FROM books"
        ).fetchone()
        conn.close()
        return dict(row)
