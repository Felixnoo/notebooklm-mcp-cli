"""Authentication database management for remote auth endpoints."""

import os
import sqlite3
import hashlib
import base64
import time
import uuid
from pathlib import Path
from typing import Dict, Optional, Any

from notebooklm_tools.core.auth import AuthTokens, Profile


class AuthDB:
    """Authentication database manager using SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the auth database."""
        if db_path is None:
            from notebooklm_tools.utils.config import get_auth_db_file
            self.db_path = get_auth_db_file()
        else:
            self.db_path = db_path
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    email TEXT,
                    created_at REAL NOT NULL,
                    last_login REAL NOT NULL
                )
            ''')
            # Create auth_tokens table with encrypted storage
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auth_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    cookies TEXT NOT NULL,
                    csrf_token TEXT,
                    session_id TEXT,
                    build_label TEXT,
                    extracted_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    encrypted BOOL NOT NULL DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            # Create api_keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    last_used REAL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            conn.commit()

    def _encrypt(self, data: str) -> str:
        """Encrypt data using a simple encryption method."""
        # In a real-world scenario, use a more secure encryption method
        # This is a basic example for demonstration purposes
        key = os.urandom(32)
        cipher = hashlib.sha256(key + data.encode()).digest()
        return base64.b64encode(key + cipher).decode()

    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt data."""
        try:
            data = base64.b64decode(encrypted_data.encode())
            key = data[:32]
            cipher = data[32:]
            # This is a basic example - in real world, use proper decryption
            return "decrypted_data"  # Placeholder
        except Exception:
            return ""

    def add_user(self, user_id: str, email: Optional[str] = None) -> bool:
        """Add a new user to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO users (user_id, email, created_at, last_login) VALUES (?, ?, ?, ?)",
                    (user_id, email, time.time(), time.time())
                )
                conn.commit()
            return True
        except Exception:
            return False

    def update_user_last_login(self, user_id: str) -> bool:
        """Update the last login timestamp for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE user_id = ?",
                    (time.time(), user_id)
                )
                conn.commit()
            return True
        except Exception:
            return False

    def save_auth_tokens(self, user_id: str, tokens: AuthTokens) -> bool:
        """Save auth tokens for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Calculate expiration time (1 week from now)
                expires_at = time.time() + (7 * 24 * 3600)
                
                # Encrypt cookies
                encrypted_cookies = self._encrypt(str(tokens.cookies))
                
                # Insert or update tokens
                cursor.execute('''
                    INSERT OR REPLACE INTO auth_tokens 
                    (user_id, cookies, csrf_token, session_id, build_label, extracted_at, expires_at, encrypted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    encrypted_cookies,
                    tokens.csrf_token,
                    tokens.session_id,
                    tokens.build_label,
                    tokens.extracted_at,
                    expires_at,
                    1
                ))
                conn.commit()
            return True
        except Exception:
            return False

    def get_auth_tokens(self, user_id: str) -> Optional[AuthTokens]:
        """Get auth tokens for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT cookies, csrf_token, session_id, build_label, extracted_at, expires_at "
                    "FROM auth_tokens WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Check if tokens are expired
                if time.time() > row[5]:
                    return None
                
                # Decrypt cookies
                try:
                    cookies = eval(self._decrypt(row[0]))
                except Exception:
                    cookies = {}
                
                return AuthTokens(
                    cookies=cookies,
                    csrf_token=row[1] or "",
                    session_id=row[2] or "",
                    build_label=row[3] or "",
                    extracted_at=row[4]
                )
        except Exception:
            return None

    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, email, created_at, last_login FROM users WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    "user_id": row[0],
                    "email": row[1],
                    "created_at": row[2],
                    "last_login": row[3]
                }
        except Exception:
            return None

    def delete_expired_tokens(self) -> int:
        """Delete expired tokens."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM auth_tokens WHERE expires_at < ?",
                    (time.time(),)
                )
                deleted = cursor.rowcount
                conn.commit()
            return deleted
        except Exception:
            return 0

    def list_users(self) -> list[Dict[str, Any]]:
        """List all users."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, email, created_at, last_login FROM users"
                )
                rows = cursor.fetchall()
                
                return [
                    {
                        "user_id": row[0],
                        "email": row[1],
                        "created_at": row[2],
                        "last_login": row[3]
                    }
                    for row in rows
                ]
        except Exception:
            return []

    def generate_api_key(self, user_id: str, description: Optional[str] = None) -> Optional[str]:
        """Generate a new API key for a user."""
        try:
            # Generate a secure API key
            api_key = f"nlm_{user_id}_{str(uuid.uuid4()).replace('-', '')}"
            
            # Calculate expiration time (30 days from now)
            expires_at = time.time() + (30 * 24 * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO api_keys (user_id, api_key, description, created_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                    (user_id, api_key, description, time.time(), expires_at)
                )
                conn.commit()
            
            return api_key
        except Exception:
            return None

    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return user information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, expires_at FROM api_keys WHERE api_key = ?",
                    (api_key,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                user_id, expires_at = row
                
                # Check if API key is expired
                if time.time() > expires_at:
                    return None
                
                # Update last_used timestamp
                cursor.execute(
                    "UPDATE api_keys SET last_used = ? WHERE api_key = ?",
                    (time.time(), api_key)
                )
                conn.commit()
                
                # Get user information
                user_info = self.get_user_info(user_id)
                if not user_info:
                    return None
                
                return user_info
        except Exception:
            return None

    def get_user_by_api_key(self, api_key: str) -> Optional[str]:
        """Get user ID by API key."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, expires_at FROM api_keys WHERE api_key = ?",
                    (api_key,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                user_id, expires_at = row
                
                # Check if API key is expired
                if time.time() > expires_at:
                    return None
                
                return user_id
        except Exception:
            return None

    def list_api_keys(self, user_id: str) -> list[Dict[str, Any]]:
        """List all API keys for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, api_key, description, created_at, expires_at, last_used FROM api_keys WHERE user_id = ?",
                    (user_id,)
                )
                rows = cursor.fetchall()
                
                return [
                    {
                        "id": row[0],
                        "api_key": row[1],
                        "description": row[2],
                        "created_at": row[3],
                        "expires_at": row[4],
                        "last_used": row[5],
                        "is_expired": time.time() > row[4]
                    }
                    for row in rows
                ]
        except Exception:
            return []

    def revoke_api_key(self, api_key: str, user_id: str) -> bool:
        """Revoke an API key for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM api_keys WHERE api_key = ? AND user_id = ?",
                    (api_key, user_id)
                )
                deleted = cursor.rowcount > 0
                conn.commit()
            return deleted
        except Exception:
            return False

    def delete_expired_api_keys(self) -> int:
        """Delete expired API keys."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM api_keys WHERE expires_at < ?",
                    (time.time(),)
                )
                deleted = cursor.rowcount
                conn.commit()
            return deleted
        except Exception:
            return 0


def get_auth_db() -> AuthDB:
    """Get the auth database instance."""
    return AuthDB()
