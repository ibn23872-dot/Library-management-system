"""
UserDAO - Data Access Layer
All SQL operations for the Users (staff) table.
"""

from dao.db_connection import get_connection


class UserDAO:

    @staticmethod
    def get_by_username(username):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def insert(username, hashed_password, role='Librarian'):
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?,?,?)",
            (username, hashed_password, role)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def count():
        conn = get_connection()
        row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
        conn.close()
        return row['cnt']
