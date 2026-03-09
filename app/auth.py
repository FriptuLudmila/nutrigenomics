"""
Authentication Module
====================
User registration, login, and JWT token management.
"""

import os
import jwt
import bcrypt
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass, asdict
from functools import wraps
from flask import request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    age: int
    sex: str  # 'male', 'female', 'other'
    created_at: datetime
    email_verified: bool = False
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
            'age': self.age,
            'sex': self.sex,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


@dataclass
class VerificationCode:
    """Email verification code model"""
    email: str
    code: str
    created_at: datetime
    expires_at: datetime

    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict):
        """Create from MongoDB document"""
        return cls(**data)

    def is_expired(self) -> bool:
        """Check if verification code has expired"""
        return datetime.utcnow() > self.expires_at


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


# Alias for clarity
verify_token = decode_token


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


# ============================================
# Email Verification Functions
# ============================================

def generate_verification_code() -> str:
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))


def save_verification_code(db, email: str, code: str) -> bool:
    """Save verification code to database"""
    try:
        verification = VerificationCode(
            email=email,
            code=code,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=15)  # Expires in 15 minutes
        )
        db.verification_codes.update_one(
            {'email': email},
            {'$set': verification.to_dict()},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save verification code: {e}")
        return False


def get_verification_code(db, email: str) -> Optional[VerificationCode]:
    """Get verification code by email"""
    try:
        doc = db.verification_codes.find_one({'email': email})
        if doc:
            doc.pop('_id', None)
            return VerificationCode.from_dict(doc)
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get verification code: {e}")
        return None


def delete_verification_code(db, email: str) -> bool:
    """Delete verification code after successful verification"""
    try:
        db.verification_codes.delete_one({'email': email})
        return True
    except Exception as e:
        print(f"[ERROR] Failed to delete verification code: {e}")
        return False


def send_verification_email(email: str, code: str, name: str) -> bool:
    """Send verification code via email"""
    try:
        # Email configuration from environment
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SMTP_EMAIL')
        sender_password = os.getenv('SMTP_PASSWORD')

        if not sender_email or not sender_password:
            print("[WARNING] SMTP credentials not configured. Verification code:", code)
            return False

        # Create email message
        message = MIMEMultipart('alternative')
        message['Subject'] = 'Verify Your NutriGenome Account'
        message['From'] = f"NutriGenome <{sender_email}>"
        message['To'] = email

        # Email body
        text = f"""
Hello {name},

Thank you for signing up for NutriGenome!

Your verification code is: {code}

This code will expire in 15 minutes.

If you didn't create an account, please ignore this email.

Best regards,
The NutriGenome Team
        """

        html = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #2563eb;">Welcome to NutriGenome!</h2>
      <p>Hello {name},</p>
      <p>Thank you for signing up for NutriGenome. To complete your registration, please use the verification code below:</p>

      <div style="background-color: #f3f4f6; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
        <h1 style="color: #2563eb; font-size: 32px; letter-spacing: 8px; margin: 0;">{code}</h1>
      </div>

      <p style="color: #6b7280; font-size: 14px;">This code will expire in 15 minutes.</p>

      <p>If you didn't create an account, please ignore this email.</p>

      <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

      <p style="color: #6b7280; font-size: 12px;">
        Best regards,<br>
        The NutriGenome Team
      </p>
    </div>
  </body>
</html>
        """

        # Attach text and HTML versions
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        message.attach(part1)
        message.attach(part2)

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())

        print(f"[OK] Verification email sent to {email}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to send verification email: {e}")
        print(f"[DEBUG] Verification code for {email}: {code}")
        return False
