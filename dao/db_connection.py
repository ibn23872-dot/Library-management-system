"""
DBConnection - Data Access Layer
Handles all database connections and query execution.
"""

import sqlite3
import os
import configparser

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.ini')

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

DB_PATH = os.path.join(
    os.path.dirname(__file__), '..',
    config.get('database', 'db_path', fallback='library.db')
)


def get_connection():
    """Return a new SQLite connection with row factory."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize database schema from schema.sql."""
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
    conn = get_connection()
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
