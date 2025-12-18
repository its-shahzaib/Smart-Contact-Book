# utils.py - small helper functions (hashing password simple)
import hashlib

def hash_password(password: str) -> str:
    # simple SHA256 hashing (for demo). For production use bcrypt or argon2.
    return hashlib.sha256(password.encode('utf-8')).hexdigest()