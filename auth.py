import os
import sys
import hashlib
import sqlite3

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_connection

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = "ai_resume_analyzer_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def register_user(username: str, email: str, password: str):
    """Register a new user in the SQLite database."""
    if not username or not email or not password:
        return False, "All fields are required."
    
    conn = get_connection()
    cursor = conn.cursor()
    
    pwd_hash = hash_password(password)
    try:
        cursor.execute("""
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
        """, (username.strip(), email.strip().lower(), pwd_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return True, {"id": user_id, "username": username.strip(), "email": email.strip().lower()}
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username or Email already exists."
    except Exception as e:
        conn.close()
        return False, f"Registration failed: {str(e)}"

def authenticate_user(username_or_email: str, password: str):
    """Authenticate existing user credentials."""
    if not username_or_email or not password:
        return False, "Credentials required."
    
    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    
    cursor.execute("""
    SELECT id, username, email FROM users 
    WHERE (username = ? OR email = ?) AND password_hash = ?
    """, (username_or_email.strip(), username_or_email.strip().lower(), pwd_hash))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return True, dict(row)
    else:
        return False, "Invalid username/email or password."
