# models.py - database abstraction. Supports simple SQLite and MySQL.
import sqlite3
from contextlib import contextmanager
from config import DB_MODE, SQLITE_PATH, MYSQL
import mysql.connector

# SQLite helpers
@contextmanager
def sqlite_conn():
    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

# MySQL helpers
@contextmanager
def mysql_conn():
    conn = mysql.connector.connect(
        host=MYSQL['host'],
        port=MYSQL['port'],
        user=MYSQL['user'],
        password=MYSQL['password'],
        database=MYSQL['database'],
        autocommit=True
    )
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    if DB_MODE == 'sqlite':
        with sqlite_conn() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
    else:
        # MySQL: assume database exists (use schema.sql to create it)
        with mysql_conn() as conn:
            cur = conn.cursor()
            cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB;
            ''')
            cur.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(100) NOT NULL,
                email VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            ''')

# Generic query helper (returns list of dicts)
def fetch_all(query, params=()):
    if DB_MODE == 'sqlite':
        with sqlite_conn() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    else:
        with mysql_conn() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(query, params)
            return cur.fetchall()

def fetch_one(query, params=()):
    rows = fetch_all(query, params)
    return rows[0] if rows else None

def execute(query, params=()):
    if DB_MODE == 'sqlite':
        with sqlite_conn() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.lastrowid
    else:
        with mysql_conn() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.lastrowid
