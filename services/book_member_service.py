"""
BookService & MemberService - Business Logic Layer
Enforces business rules before calling DAO layer.
"""

from dao.book_dao import BookDAO
from dao.member_dao import MemberDAO


class BookService:

    @staticmethod
    def get_all():
        return BookDAO.get_all()

    @staticmethod
    def search(query):
        if not query or not query.strip():
            return BookDAO.get_all()
        return BookDAO.search(query.strip())

    @staticmethod
    def add_book(data):
        errors = BookService._validate(data)
        if errors:
            return False, errors

        existing = BookDAO.get_by_isbn(data['isbn'])
        if existing:
            return False, "A book with this ISBN already exists."

        BookDAO.insert(data)
        return True, "Book added successfully."

    @staticmethod
    def update_book(book_id, data):
        errors = BookService._validate(data)
        if errors:
            return False, errors

        existing = BookDAO.get_by_isbn(data['isbn'])
        if existing and existing['book_id'] != int(book_id):
            return False, "Another book with this ISBN already exists."

        BookDAO.update(book_id, data)
        return True, "Book updated successfully."

    @staticmethod
    def delete_book(book_id):
        book = BookDAO.get_by_id(book_id)
        if not book:
            return False, "Book not found."
        if book['total_copies'] != book['available_copies']:
            return False, "Cannot delete: book has active borrowings."
        BookDAO.delete(book_id)
        return True, "Book deleted successfully."

    @staticmethod
    def _validate(data):
        required = ['isbn', 'title', 'author', 'total_copies']
        for f in required:
            if not data.get(f):
                return f"Field '{f}' is required."
        try:
            copies = int(data['total_copies'])
            if copies < 1:
                raise ValueError
        except (ValueError, TypeError):
            return "Total copies must be a positive integer."
        return None


class MemberService:

    @staticmethod
    def get_all():
        MemberDAO.auto_update_status()
        return MemberDAO.get_all()

    @staticmethod
    def search(query):
        if not query or not query.strip():
            return MemberDAO.get_all()
        return MemberDAO.search(query.strip())
    
    @staticmethod
    def register(data):
        import sqlite3
        errors = MemberService._validate(data)
        if errors:
            return False, errors
        try:
            MemberDAO.insert(data)
        except sqlite3.IntegrityError as e:
            if "email" in str(e).lower():
                return False, "A member with this email address already exists."
            raise e
        return True, "Member registered successfully."
    
    @staticmethod
    def update(member_id, data):
        import sqlite3
        errors = MemberService._validate(data, update=True)
        if errors:
            return False, errors
        try:
            MemberDAO.update(member_id, data)
        except sqlite3.IntegrityError as e:
            if "email" in str(e).lower():
                return False, "A member with this email address already exists."
            raise e
        return True, "Member updated successfully."

    @staticmethod
    def delete(member_id):
        member = MemberDAO.get_by_id(member_id)
        if not member:
            return False, "Member not found."
        MemberDAO.delete(member_id)
        return True, "Member deleted successfully."

    @staticmethod
    def _validate(data, update=False):
        if not data.get('full_name'):
            return "Full name is required."
        if not data.get('membership_type'):
            return "Membership type is required."
        if not data.get('expiry_date'):
            return "Expiry date is required."
        if not update and not data.get('start_date'):
            return "Start date is required."
        return None
