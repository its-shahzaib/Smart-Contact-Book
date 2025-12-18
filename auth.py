# auth.py - authentication routes and helpers (Flask blueprint-style functions)
from flask import session, redirect, url_for, request, flash
from models import fetch_one, execute
from utils import hash_password

def login_user_logic(form):
    username = form.get('username','').strip()
    password = form.get('password','').strip()
    if not username or not password:
        return False, "Provide username and password"
    user = fetch_one("SELECT * FROM users WHERE username=%s", (username,)) if False else fetch_one("SELECT * FROM users WHERE username=?", (username,))
    # NOTE: we'll handle parameter style in app.py depending on DB_MODE
    # Instead, auth checks are done in app.py for simplicity.
    return username, password

# We keep real route handlers in app.py to avoid blueprint complexity.
