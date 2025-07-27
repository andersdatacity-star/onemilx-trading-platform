import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import jwt
import os

class UserAuth:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-this')
        self.init_database()
    
    def init_database(self):
        """Initialize database with users and invites tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                api_key TEXT,
                api_secret TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Invites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invite_code TEXT UNIQUE NOT NULL,
                created_by INTEGER,
                used_by INTEGER,
                is_used BOOLEAN DEFAULT 0,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id),
                FOREIGN KEY (used_by) REFERENCES users (id)
            )
        ''')
        
        # Create admin user if not exists
        cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            admin_password = self.hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin@onemilx.com', admin_password, 'admin'))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return salt + hash_obj.hex()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        salt = password_hash[:32]
        stored_hash = password_hash[32:]
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex() == stored_hash
    
    def create_invite(self, created_by: int, expires_days: int = 7) -> str:
        """Create a new invite code"""
        invite_code = secrets.token_urlsafe(16)
        expires_at = datetime.now() + timedelta(days=expires_days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO invites (invite_code, created_by, expires_at)
            VALUES (?, ?, ?)
        ''', (invite_code, created_by, expires_at))
        conn.commit()
        conn.close()
        
        return invite_code
    
    def validate_invite(self, invite_code: str) -> bool:
        """Validate if invite code is valid and not expired"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM invites 
            WHERE invite_code = ? AND is_used = 0 AND expires_at > ?
        ''', (invite_code, datetime.now()))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def use_invite(self, invite_code: str, user_id: int):
        """Mark invite as used"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE invites SET is_used = 1, used_by = ?
            WHERE invite_code = ?
        ''', (user_id, invite_code))
        conn.commit()
        conn.close()
    
    def register_user(self, username: str, email: str, password: str, invite_code: str) -> Dict:
        """Register a new user with invite code"""
        if not self.validate_invite(invite_code):
            return {"success": False, "error": "Invalid or expired invite code"}
        
        if self.user_exists(username):
            return {"success": False, "error": "Username already exists"}
        
        if self.email_exists(email):
            return {"success": False, "error": "Email already exists"}
        
        password_hash = self.hash_password(password)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            
            user_id = cursor.lastrowid
            self.use_invite(invite_code, user_id)
            
            conn.commit()
            conn.close()
            
            return {"success": True, "user_id": user_id}
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return {"success": False, "error": str(e)}
    
    def login_user(self, username: str, password: str) -> Dict:
        """Login user and return JWT token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email, password_hash, role, api_key, api_secret
            FROM users WHERE username = ? AND is_active = 1
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return {"success": False, "error": "Invalid credentials"}
        
        user_id, username, email, password_hash, role, api_key, api_secret = user
        
        if not self.verify_password(password, password_hash):
            return {"success": False, "error": "Invalid credentials"}
        
        # Update last login
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user_id))
        conn.commit()
        conn.close()
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, self.secret_key, algorithm='HS256')
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "role": role,
                "api_key": api_key,
                "api_secret": api_secret
            }
        }
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def user_exists(self, username: str) -> bool:
        """Check if username exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def email_exists(self, email: str) -> bool:
        """Check if email exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email, role, api_key, api_secret, created_at, last_login
            FROM users WHERE id = ? AND is_active = 1
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "role": user[3],
                "api_key": user[4],
                "api_secret": user[5],
                "created_at": user[6],
                "last_login": user[7]
            }
        return None
    
    def get_all_users(self, admin_id: int) -> List[Dict]:
        """Get all users (admin only)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, email, role, is_active, created_at, last_login
            FROM users ORDER BY created_at DESC
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        return [{
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "role": user[3],
            "is_active": user[4],
            "created_at": user[5],
            "last_login": user[6]
        } for user in users]
    
    def get_active_invites(self, admin_id: int) -> List[Dict]:
        """Get active invites (admin only)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT i.id, i.invite_code, i.expires_at, i.created_at, u.username as created_by
            FROM invites i
            LEFT JOIN users u ON i.created_by = u.id
            WHERE i.is_used = 0 AND i.expires_at > ?
            ORDER BY i.created_at DESC
        ''', (datetime.now(),))
        
        invites = cursor.fetchall()
        conn.close()
        
        return [{
            "id": invite[0],
            "invite_code": invite[1],
            "expires_at": invite[2],
            "created_at": invite[3],
            "created_by": invite[4]
        } for invite in invites] 