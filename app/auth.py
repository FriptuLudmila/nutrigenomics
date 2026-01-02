"""
Authentication Module
====================
User registration, login, and JWT token management.
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass, asdict
from functools import wraps
from flask import request, jsonify

# JWT Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days


@dataclass
class User:
    """User model"""
    user_id: str
    email: str
    password_hash: str
    name: str
    created_at: datetime
    last_login: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict):
        """Create from MongoDB document"""
        return cls(**data)

    def to_safe_dict(self) -> Dict:
        """Return user data without password hash"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_token(user_id: str, email: str) -> str:
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[Dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Authentication required'}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Add user info to request context
        request.user_id = payload['user_id']
        request.user_email = payload['email']

        return f(*args, **kwargs)

    return decorated_function


# Database operations for users
def save_user(db, user: User) -> bool:
    """Save user to database"""
    try:
        db.users.update_one(
            {'email': user.email},
            {'$set': user.to_dict()},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save user: {e}")
        return False


def get_user_by_email(db, email: str) -> Optional[User]:
    """Get user by email"""
    try:
        doc = db.users.find_one({'email': email})
        if doc:
            doc.pop('_id', None)
            return User.from_dict(doc)
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get user: {e}")
        return None


def get_user_by_id(db, user_id: str) -> Optional[User]:
    """Get user by ID"""
    try:
        doc = db.users.find_one({'user_id': user_id})
        if doc:
            doc.pop('_id', None)
            return User.from_dict(doc)
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get user: {e}")
        return None
