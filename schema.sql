-- =============================================
-- Library Management System - Database Schema
-- Based on SRS & Design Document
-- Addis Ababa University - Computer Engineering
-- =============================================

PRAGMA foreign_keys = ON;

-- =============================================
-- USERS TABLE (Library Staff)
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    username  VARCHAR(50)  NOT NULL UNIQUE,
    password  VARCHAR(255) NOT NULL,   -- bcrypt hashed
    role      VARCHAR(20)  NOT NULL CHECK(role IN ('Librarian','Assistant')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Default admin: admin / admin123 (hashed)
-- INSERT done from app.py on first run

-- =============================================
-- BOOKS TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS books (
    book_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn              VARCHAR(20)  NOT NULL UNIQUE,
    title             VARCHAR(100) NOT NULL,
    author            VARCHAR(100) NOT NULL,
    publisher         VARCHAR(100),
    publication_year  INTEGER,
    category          VARCHAR(50),
    edition           VARCHAR(20),
    language          VARCHAR(30)  DEFAULT 'English',
    total_copies      INTEGER      NOT NULL DEFAULT 1,
    available_copies  INTEGER      NOT NULL DEFAULT 1,
    shelf_location    VARCHAR(50),
    status            VARCHAR(20)  NOT NULL DEFAULT 'Available'
                      CHECK(status IN ('Available','Issued','Lost')),
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- MEMBERS TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS members (
    member_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       VARCHAR(100) NOT NULL,
    department      VARCHAR(50),
    contact_number  VARCHAR(20),
    email           VARCHAR(100),
    membership_type VARCHAR(20)  NOT NULL CHECK(membership_type IN ('Student','Faculty','Staff')),
    start_date      DATE         NOT NULL,
    expiry_date     DATE         NOT NULL,
    status          VARCHAR(20)  NOT NULL DEFAULT 'Active'
                    CHECK(status IN ('Active','Suspended')),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- BORROWINGS TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS borrowings (
    borrow_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id   INTEGER NOT NULL REFERENCES members(member_id),
    book_id     INTEGER NOT NULL REFERENCES books(book_id),
    issue_date  DATE    NOT NULL,
    due_date    DATE    NOT NULL,
    return_date DATE,
    staff_id    INTEGER NOT NULL REFERENCES users(user_id),
    status      VARCHAR(20) NOT NULL DEFAULT 'Borrowed'
                CHECK(status IN ('Borrowed','Returned')),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- FINES TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS fines (
    fine_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    borrow_id    INTEGER        NOT NULL REFERENCES borrowings(borrow_id),
    member_id    INTEGER        NOT NULL REFERENCES members(member_id),
    amount       DECIMAL(10,2)  NOT NULL,
    paid         BOOLEAN        NOT NULL DEFAULT 0,
    date_created DATE           NOT NULL,
    date_paid    DATE,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- INDEXES for performance
-- =============================================
CREATE INDEX IF NOT EXISTS idx_books_isbn      ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_title     ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author    ON books(author);
CREATE INDEX IF NOT EXISTS idx_members_name    ON members(full_name);
CREATE INDEX IF NOT EXISTS idx_borrowings_member ON borrowings(member_id);
CREATE INDEX IF NOT EXISTS idx_borrowings_book   ON borrowings(book_id);
CREATE INDEX IF NOT EXISTS idx_fines_member    ON fines(member_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_members_email_unique
    ON members(email) WHERE email IS NOT NULL AND email != '';