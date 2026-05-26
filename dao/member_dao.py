"""
MemberDAO - Data Access Layer
All SQL operations for the Members table.
"""

from dao.db_connection import get_connection
from datetime import date


class MemberDAO:

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM members ORDER BY member_id ASC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(member_id):
        conn = get_connection()
        row = conn.execute("SELECT * FROM members WHERE member_id = ?", (member_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def search(query):
        conn = get_connection()
        q = f"%{query}%"
        rows = conn.execute(
            """SELECT * FROM members
            WHERE full_name LIKE ? OR email LIKE ? OR CAST(member_id AS TEXT) LIKE ?
            ORDER BY member_id ASC""",
            (q, q, q)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def insert(data):
        conn = get_connection()
        conn.execute(
            """INSERT INTO members
               (full_name, department, contact_number, email, membership_type,
                start_date, expiry_date, status)
               VALUES (?,?,?,?,?,?,?,?)""",
            (data['full_name'], data.get('department'), data.get('contact_number'),
             data.get('email'), data['membership_type'],
             data['start_date'], data['expiry_date'], 'Active')
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update(member_id, data):
        conn = get_connection()
        conn.execute(
            """UPDATE members SET
               full_name=?, department=?, contact_number=?, email=?,
               membership_type=?, expiry_date=?, status=?
               WHERE member_id=?""",
            (data['full_name'], data.get('department'), data.get('contact_number'),
             data.get('email'), data['membership_type'],
             data['expiry_date'], data.get('status', 'Active'), member_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(member_id):
        conn = get_connection()
        conn.execute("DELETE FROM members WHERE member_id = ?", (member_id,))

        # Reorder all member_ids to close the gap
        members = conn.execute("SELECT member_id FROM members ORDER BY member_id ASC").fetchall()
        for new_id, row in enumerate(members, start=1):
            if row[0] != new_id:
                conn.execute("UPDATE members SET member_id = ? WHERE member_id = ?", (new_id, row[0]))

        # Reset the autoincrement counter to continue from the last ID
        conn.execute("UPDATE sqlite_sequence SET seq = (SELECT MAX(member_id) FROM members) WHERE name = 'members'")

        conn.commit()
        conn.close()

    @staticmethod
    def auto_update_status():
        """Suspend members with expired membership."""
        conn = get_connection()
        today = date.today().isoformat()
        conn.execute(
            "UPDATE members SET status='Suspended' WHERE expiry_date < ? AND status='Active'",
            (today,)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_stats():
        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) as total, SUM(status='Active') as active FROM members"
        ).fetchone()
        conn.close()
        return dict(row)
