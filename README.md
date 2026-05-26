# Library Management System
## Addis Ababa University — Software Engineering Project

### Group Members
- Ibsa Nemera       (ATE/3502/14)
- Abel Tadesse      (ATE/7552/14)
- Kaleab Solomon    (ATE/6915/14)

---

## Architecture
Three-Tier Layered Architecture (as per Design Document):

```
User → Presentation Layer (HTML/CSS/Jinja2)
     → Business Logic Layer (Flask Services)
     → Data Access Layer (DAO Classes)
     → Database Layer (SQLite)
```

## Project Structure
```
lms/
├── app.py                    # Flask app, routes (Presentation Layer)
├── config.ini                # Configurable borrowing rules & fine rates
├── schema.sql                # Database schema (all 5 tables)
├── requirements.txt
│
├── dao/                      # Data Access Layer
│   ├── db_connection.py      # DBConnection class
│   ├── book_dao.py           # BookDAO
│   ├── member_dao.py         # MemberDAO
│   ├── borrow_dao.py         # BorrowDAO + FineDAO
│   └── user_dao.py           # UserDAO
│
├── services/                 # Business Logic Layer
│   ├── book_member_service.py  # BookService, MemberService
│   └── transaction_services.py # BorrowService, ReturnService, FineService
│
├── templates/                # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── books.html / book_form.html
│   ├── members.html / member_form.html
│   ├── borrow.html
│   ├── return.html
│   ├── fines.html
│   └── transactions.html
│
└── static/
    ├── css/style.css
    └── js/main.js
```

## Setup & Run

### 1. Install Python 3.10+
### 2. Create a Virtual Environment
Bash
'python -m venv venv'
### 3. Activate the Virtual Environment
Bash
'venv\Scripts\activate'
### 4. Install Required Packages
Bash
'pip install -r requirements.txt'
### 5. Install dependencies
bash
pip install flask werkzeug

### 6. Run the application
```bash
python app.py
```

### 7. Open in browser
```
http://localhost:5000
```

### 8. Default login
- **Username:** admin
- **Password:** admin123

---

## Features (per SRS)
- ✅ Book Catalog Management (Add, Edit, Delete, Search by title/author/ISBN/category)
- ✅ Member Management (Register, Update, Delete, Auto status by expiry date)
- ✅ Book Borrowing with due date calculation by membership type
- ✅ Book Returning with automatic fine calculation (2 ETB/day)
- ✅ Fine Tracking and payment marking
- ✅ Full transaction history
- ✅ Role-based access (Librarian / Assistant)
- ✅ Dashboard with overdue alerts and statistics

## Configuration
Edit `config.ini` to change borrowing periods, limits, and fine rates without code changes.
