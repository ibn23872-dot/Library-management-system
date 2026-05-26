"""
BorrowDAO & FineDAO - Data Access Layer
All SQL operations for Borrowings and Fines tables.
"""

from dao.db_connection import get_connection


class BorrowDAO:

    @staticmethod
    def get_active_by_member(member_id):
        conn = get_connection()
        rows = conn.execute(
            """SELECT b.*, bk.title, bk.isbn FROM borrowings b
               JOIN books bk ON b.book_id = bk.book_id
               WHERE b.member_id = ? AND b.status = 'Borrowed'""",
            (member_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_active_borrow_count(member_id):
        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM borrowings WHERE member_id = ? AND status = 'Borrowed'",
            (member_id,)
        ).fetchone()
        conn.close()
        return row['cnt']

    @staticmethod
    def get_active_by_member_and_book(member_id, book_id):
        conn = get_connection()
        row = conn.execute(
            """SELECT * FROM borrowings
               WHERE member_id = ? AND book_id = ? AND status = 'Borrowed'""",
            (member_id, book_id)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def insert(data):
        conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO borrowings
               (member_id, book_id, issue_date, due_date, staff_id, status)
               VALUES (?,?,?,?,?,'Borrowed')""",
            (data['member_id'], data['book_id'], data['issue_date'],
             data['due_date'], data['staff_id'])
        )
        borrow_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return borrow_id

    @staticmethod
    def mark_returned(borrow_id, return_date):
        conn = get_connection()
        conn.execute(
            "UPDATE borrowings SET status='Returned', return_date=? WHERE borrow_id=?",
            (return_date, borrow_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_with_details():
        conn = get_connection()
        rows = conn.execute(
            """SELECT b.*, m.full_name, bk.title, bk.isbn
               FROM borrowings b
               JOIN members m ON b.member_id = m.member_id
               JOIN books bk ON b.book_id = bk.book_id
               ORDER BY b.created_at DESC"""
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_overdue():
        conn = get_connection()
        rows = conn.execute(
            """SELECT b.*, m.full_name, bk.title
               FROM borrowings b
               JOIN members m ON b.member_id = m.member_id
               JOIN books bk ON b.book_id = bk.book_id
               WHERE b.status = 'Borrowed' AND b.due_date < date('now')
               ORDER BY b.due_date"""
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_stats():
        conn = get_connection()
        row = conn.execute(
            """SELECT
               SUM(status='Borrowed') as active,
               SUM(status='Returned') as returned,
               COUNT(*) as total
               FROM borrowings"""
        ).fetchone()
        conn.close()
        return dict(row)


class FineDAO:

    @staticmethod
    def insert(data):
        conn = get_connection()
        conn.execute(
            """INSERT INTO fines (borrow_id, member_id, amount, paid, date_created)
               VALUES (?,?,?,0,?)""",
            (data['borrow_id'], data['member_id'], data['amount'], data['date_created'])
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_with_details():
        conn = get_connection()
        rows = conn.execute(
            """SELECT f.*, m.full_name, bk.title,
               b.issue_date, b.due_date, b.return_date
               FROM fines f
               JOIN members m ON f.member_id = m.member_id
               JOIN borrowings b ON f.borrow_id = b.borrow_id
               JOIN books bk ON b.book_id = bk.book_id
               ORDER BY f.date_created DESC"""
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_unpaid_by_member(member_id):
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM fines WHERE member_id = ? AND paid = 0", (member_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def mark_paid(fine_id):
        from datetime import date
        conn = get_connection()
        conn.execute(
            "UPDATE fines SET paid=1, date_paid=? WHERE fine_id=?",
            (date.today().isoformat(), fine_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_stats():
        conn = get_connection()
        row = conn.execute(
            """SELECT
               SUM(CASE WHEN paid=0 THEN amount ELSE 0 END) as unpaid_total,
               SUM(CASE WHEN paid=1 THEN amount ELSE 0 END) as paid_total,
               COUNT(*) as total
               FROM fines"""
        ).fetchone()
        conn.close()
        return dict(row)
