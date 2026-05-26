"""
BorrowService, ReturnService, FineService - Business Logic Layer
Core transaction logic as specified in SRS and Design document.
"""

import configparser
import os
from datetime import date, timedelta

from dao.book_dao import BookDAO
from dao.member_dao import MemberDAO
from dao.borrow_dao import BorrowDAO, FineDAO

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

BORROW_DAYS = {
    'Student': int(config.get('borrowing', 'student_borrow_days', fallback=14)),
    'Faculty': int(config.get('borrowing', 'faculty_borrow_days', fallback=30)),
    'Staff':   int(config.get('borrowing', 'staff_borrow_days',   fallback=21)),
}
BORROW_LIMITS = {
    'Student': int(config.get('borrowing', 'student_borrow_limit', fallback=3)),
    'Faculty': int(config.get('borrowing', 'faculty_borrow_limit', fallback=5)),
    'Staff':   int(config.get('borrowing', 'staff_borrow_limit',   fallback=4)),
}
DAILY_FINE = float(config.get('fines', 'daily_fine_rate', fallback=2.0))


class BorrowService:

    @staticmethod
    def issue_book(member_id, isbn, staff_id):
        """
        Borrow Book Sequence (per Design doc §6.1.1):
        1. Verify member is active
        2. Verify book is available
        3. Check borrow limit
        4. Calculate due date
        5. Store record + decrement copies
        """
        member = MemberDAO.get_by_id(member_id)
        if not member:
            return False, "Member not found."
        if member['status'] != 'Active':
            return False, f"Member account is {member['status']}. Cannot borrow."

        book = BookDAO.get_by_isbn(isbn)
        if not book:
            return False, "Book not found with that ISBN."
        if book['available_copies'] < 1:
            return False, "No available copies of this book."

        active_count = BorrowDAO.get_active_borrow_count(member_id)
        limit = BORROW_LIMITS.get(member['membership_type'], 3)
        if active_count >= limit:
            return False, f"Member has reached the borrowing limit ({limit} books)."

        already = BorrowDAO.get_active_by_member_and_book(member_id, book['book_id'])
        if already:
            return False, "Member already has an active borrowing for this book."

        today = date.today()
        days = BORROW_DAYS.get(member['membership_type'], 14)
        due = today + timedelta(days=days)

        borrow_id = BorrowDAO.insert({
            'member_id': member_id,
            'book_id': book['book_id'],
            'issue_date': today.isoformat(),
            'due_date': due.isoformat(),
            'staff_id': staff_id,
        })
        BookDAO.decrement_available(book['book_id'])

        return True, {
            'borrow_id': borrow_id,
            'member_name': member['full_name'],
            'book_title': book['title'],
            'issue_date': today.isoformat(),
            'due_date': due.isoformat(),
        }


class ReturnService:

    @staticmethod
    def return_book(member_id, isbn):
        """
        Return Book Sequence (per Design doc §6.1.2):
        1. Find borrowing record
        2. Check overdue
        3. Calculate fine if overdue
        4. Store fine, update borrowing, update book copies
        """
        book = BookDAO.get_by_isbn(isbn)
        if not book:
            return False, "Book not found with that ISBN."

        borrow = BorrowDAO.get_active_by_member_and_book(member_id, book['book_id'])
        if not borrow:
            return False, "No active borrowing found for this member and book."

        today = date.today()
        due = date.fromisoformat(borrow['due_date'])

        fine_amount = 0.0
        days_late = 0
        if today > due:
            days_late = (today - due).days
            fine_amount = round(days_late * DAILY_FINE, 2)
            FineDAO.insert({
                'borrow_id': borrow['borrow_id'],
                'member_id': member_id,
                'amount': fine_amount,
                'date_created': today.isoformat(),
            })

        BorrowDAO.mark_returned(borrow['borrow_id'], today.isoformat())
        BookDAO.increment_available(book['book_id'])

        member = MemberDAO.get_by_id(member_id)
        return True, {
            'member_name': member['full_name'],
            'book_title': book['title'],
            'return_date': today.isoformat(),
            'due_date': borrow['due_date'],
            'days_late': days_late,
            'fine_amount': fine_amount,
        }


class FineService:

    @staticmethod
    def get_all():
        return FineDAO.get_all_with_details()

    @staticmethod
    def mark_paid(fine_id):
        FineDAO.mark_paid(fine_id)
        return True, "Fine marked as paid."

    @staticmethod
    def get_unpaid_for_member(member_id):
        return FineDAO.get_unpaid_by_member(member_id)
