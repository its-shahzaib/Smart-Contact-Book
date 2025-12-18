# config.py - simple configuration (choose DB via environment or edit values)
import os

# DB_MODE: 'sqlite' or 'mysql'
DB_MODE = os.getenv('DB_MODE', 'mysql')

# SQLite path (file created in project root)
SQLITE_PATH = os.getenv('SQLITE_PATH', 'contacts.db')

# MySQL settings (used only if DB_MODE == 'mysql')
MYSQL = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3307)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'smart_contact_book'),
}
# Secret key for sessions
SECRET_KEY = os.getenv('SECRET_KEY', 'a-very-secret-key')