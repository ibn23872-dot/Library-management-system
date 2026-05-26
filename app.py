"""
Library Management System - Flask Application
Addis Ababa University - Computer Engineering
Three-tier architecture: Presentation → Service → DAO → Database
"""

import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify)

from dao.db_connection import init_db
from dao.user_dao import UserDAO
from dao.book_dao import BookDAO
from dao.member_dao import MemberDAO
from dao.borrow_dao import BorrowDAO, FineDAO
from services.book_member_service import BookService, MemberService
from services.transaction_services import BorrowService, ReturnService, FineService

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'lms-aau-secret-2024-change-in-prod')


# ─────────────────────────────────────────────
# Auth helpers
# ─────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def librarian_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'Librarian':
            flash('Only Librarians may perform this action.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
# Auth routes
# ─────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = UserDAO.get_by_username(username)
        if user and check_password_hash(user["password"], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ─────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    book_stats   = BookDAO.get_stats()
    member_stats = MemberDAO.get_stats()
    borrow_stats = BorrowDAO.get_stats()
    fine_stats   = FineDAO.get_stats()
    overdue      = BorrowDAO.get_overdue()

    return render_template('dashboard.html',
        book_stats=book_stats,
        member_stats=member_stats,
        borrow_stats=borrow_stats,
        fine_stats=fine_stats,
        overdue=overdue[:5]
    )


# ─────────────────────────────────────────────
# Book Management
# ─────────────────────────────────────────────

@app.route('/books')
@login_required
def books():
    query = request.args.get('q', '')
    book_list = BookService.search(query)
    return render_template('books.html', books=book_list, query=query)


@app.route('/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        data = {k: v.strip() for k, v in request.form.items()}
        ok, msg = BookService.add_book(data)
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('books'))
    return render_template('book_form.html', book=None, action='Add')


@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = BookDAO.get_by_id(book_id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('books'))

    if request.method == 'POST':
        data = {k: v.strip() for k, v in request.form.items()}
        ok, msg = BookService.update_book(book_id, data)
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('books'))
    return render_template('book_form.html', book=book, action='Edit')


@app.route('/books/delete/<int:book_id>', methods=['POST'])
@librarian_required
def delete_book(book_id):
    ok, msg = BookService.delete_book(book_id)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('books'))


# ─────────────────────────────────────────────
# Member Management
# ─────────────────────────────────────────────

@app.route('/members')
@login_required
def members():
    query = request.args.get('q', '')
    member_list = MemberService.search(query)
    return render_template('members.html', members=member_list, query=query)


@app.route('/members/add', methods=['GET', 'POST'])
@login_required
def add_member():
    if request.method == 'POST':
        data = {k: v.strip() for k, v in request.form.items()}
        ok, msg = MemberService.register(data)
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('members'))
    return render_template('member_form.html', member=None, action='Register')


@app.route('/members/edit/<int:member_id>', methods=['GET', 'POST'])
@login_required
def edit_member(member_id):
    member = MemberDAO.get_by_id(member_id)
    if not member:
        flash('Member not found.', 'danger')
        return redirect(url_for('members'))

    if request.method == 'POST':
        data = {k: v.strip() for k, v in request.form.items()}
        ok, msg = MemberService.update(member_id, data)
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('members'))
    return render_template('member_form.html', member=member, action='Edit')


@app.route('/members/delete/<int:member_id>', methods=['POST'])
@librarian_required
def delete_member(member_id):
    ok, msg = MemberService.delete(member_id)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('members'))


# ─────────────────────────────────────────────
# Borrow Book
# ─────────────────────────────────────────────

@app.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    result = None
    if request.method == 'POST':
        member_id = request.form.get('member_id', '').strip()
        isbn      = request.form.get('isbn', '').strip()

        if not member_id or not isbn:
            flash('Both Member ID and ISBN are required.', 'warning')
        else:
            ok, data = BorrowService.issue_book(int(member_id), isbn, session['user_id'])
            if ok:
                result = data
                flash('Book issued successfully!', 'success')
            else:
                flash(data, 'danger')

    return render_template('borrow.html', result=result)


# ─────────────────────────────────────────────
# Return Book
# ─────────────────────────────────────────────

@app.route('/return', methods=['GET', 'POST'])
@login_required
def return_book():
    result = None
    if request.method == 'POST':
        member_id = request.form.get('member_id', '').strip()
        isbn      = request.form.get('isbn', '').strip()

        if not member_id or not isbn:
            flash('Both Member ID and ISBN are required.', 'warning')
        else:
            ok, data = ReturnService.return_book(int(member_id), isbn)
            if ok:
                result = data
                flash('Book returned successfully!', 'success')
            else:
                flash(data, 'danger')

    return render_template('return.html', result=result)


# ─────────────────────────────────────────────
# Fine Tracking
# ─────────────────────────────────────────────

@app.route('/fines')
@login_required
def fines():
    fine_list = FineService.get_all()
    return render_template('fines.html', fines=fine_list)


@app.route('/fines/pay/<int:fine_id>', methods=['POST'])
@login_required
def pay_fine(fine_id):
    ok, msg = FineService.mark_paid(fine_id)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('fines'))


# ─────────────────────────────────────────────
# Borrowing History
# ─────────────────────────────────────────────

@app.route('/transactions')
@login_required
def transactions():
    tx_list = BorrowDAO.get_all_with_details()
    from datetime import date
    return render_template('transactions.html', transactions=tx_list,
                           today_str=date.today().isoformat())


# ─────────────────────────────────────────────
# API helpers (AJAX)
# ─────────────────────────────────────────────

@app.route('/api/member/<int:member_id>')
@login_required
def api_member(member_id):
    m = MemberDAO.get_by_id(member_id)
    if m:
        return jsonify({'status': 'ok', 'name': m['full_name'],
                        'type': m['membership_type'], 'account_status': m['status']})
    return jsonify({'status': 'error', 'message': 'Not found'}), 404


@app.route('/api/book/<isbn>')
@login_required
def api_book(isbn):
    b = BookDAO.get_by_isbn(isbn)
    if b:
        return jsonify({'status': 'ok', 'title': b['title'],
                        'available': b['available_copies']})
    return jsonify({'status': 'error', 'message': 'Not found'}), 404


# ─────────────────────────────────────────────
# App startup
# ─────────────────────────────────────────────

def bootstrap():
    """Initialize DB and create default admin user."""
    init_db()
    if UserDAO.count() == 0:
        hashed = generate_password_hash('admin123')
        UserDAO.insert('admin', hashed, 'Librarian')
        print("Default admin created: admin / admin123")


if __name__ == '__main__':
    bootstrap()
    app.run(debug=True, host='0.0.0.0', port=5000)
