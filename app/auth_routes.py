"""
Authentication Routes
====================
API endpoints for user registration, email verification, and login.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid

from .database import get_db
from .auth import (
    User, hash_password, verify_password, generate_token,
    save_user, get_user_by_email,
    generate_verification_code, save_verification_code,
    get_verification_code, delete_verification_code,
    send_verification_email, require_auth
)
from .models import get_user_sessions

auth_bp = Blueprint('auth', __name__)


# ============================================
# ENDPOINT: Register (Send Verification Code)
# ============================================
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Step 1: Send verification code to email

    Request body:
    {
        "name": "John Doe",
        "age": 30,
        "sex": "male",
        "email": "john@example.com",
        "password": "secure123"
    }
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ['name', 'age', 'sex', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    name = data['name']
    age = data['age']
    sex = data['sex']
    email = data['email'].lower().strip()
    password = data['password']

    # Validate data
    if not name or len(name) < 2:
        return jsonify({'error': 'Name must be at least 2 characters'}), 400

    if not isinstance(age, int) or age < 18 or age > 120:
        return jsonify({'error': 'Age must be between 18 and 120'}), 400

    if sex not in ['male', 'female', 'other']:
        return jsonify({'error': 'Sex must be male, female, or other'}), 400

    if '@' not in email or '.' not in email:
        return jsonify({'error': 'Invalid email address'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    db = get_db()

    # Check if user already exists
    existing_user = get_user_by_email(db, email)
    if existing_user and existing_user.email_verified:
        return jsonify({'error': 'Email already registered'}), 409

    # Generate and save verification code
    code = generate_verification_code()
    if not save_verification_code(db, email, code):
        return jsonify({'error': 'Failed to generate verification code'}), 500

    # Send verification email
    email_sent = send_verification_email(email, code, name)

    # Store user data temporarily (unverified)
    user = User(
        user_id=str(uuid.uuid4()),
        email=email,
        password_hash=hash_password(password),
        name=name,
        age=age,
        sex=sex,
        created_at=datetime.utcnow(),
        email_verified=False
    )

    if not save_user(db, user):
        return jsonify({'error': 'Failed to create user'}), 500

    return jsonify({
        'success': True,
        'message': 'Verification code sent to your email',
        'email': email,
        'email_sent': email_sent,
        'debug_code': code if not email_sent else None  # Only show if email failed
    }), 200


# ============================================
# ENDPOINT: Verify Email
# ============================================
@auth_bp.route('/verify', methods=['POST'])
def verify_email():
    """
    Step 2: Verify email with code

    Request body:
    {
        "email": "john@example.com",
        "code": "123456"
    }
    """
    data = request.get_json()

    if 'email' not in data or 'code' not in data:
        return jsonify({'error': 'Email and code required'}), 400

    email = data['email'].lower().strip()
    code = data['code'].strip()

    db = get_db()

    # Get verification code from database
    verification = get_verification_code(db, email)
    if not verification:
        return jsonify({'error': 'No verification code found. Please register again.'}), 404

    # Check if code expired
    if verification.is_expired():
        delete_verification_code(db, email)
        return jsonify({'error': 'Verification code expired. Please register again.'}), 400

    # Verify code
    if verification.code != code:
        return jsonify({'error': 'Invalid verification code'}), 400

    # Get user and mark as verified
    user = get_user_by_email(db, email)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.email_verified = True
    if not save_user(db, user):
        return jsonify({'error': 'Failed to verify email'}), 500

    # Delete verification code
    delete_verification_code(db, email)

    # Generate JWT token
    token = generate_token(user.user_id, user.email)

    return jsonify({
        'success': True,
        'message': 'Email verified successfully',
        'token': token,
        'user': user.to_safe_dict()
    }), 200


# ============================================
# ENDPOINT: Resend Verification Code
# ============================================
@auth_bp.route('/resend-code', methods=['POST'])
def resend_verification_code():
    """
    Resend verification code to email

    Request body:
    {
        "email": "john@example.com"
    }
    """
    data = request.get_json()

    if 'email' not in data:
        return jsonify({'error': 'Email required'}), 400

    email = data['email'].lower().strip()
    db = get_db()

    # Check if user exists
    user = get_user_by_email(db, email)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.email_verified:
        return jsonify({'error': 'Email already verified'}), 400

    # Generate new code
    code = generate_verification_code()
    if not save_verification_code(db, email, code):
        return jsonify({'error': 'Failed to generate verification code'}), 500

    # Send email
    email_sent = send_verification_email(email, code, user.name)

    return jsonify({
        'success': True,
        'message': 'Verification code sent',
        'email_sent': email_sent,
        'debug_code': code if not email_sent else None
    }), 200


# ============================================
# ENDPOINT: Login
# ============================================
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login with email and password

    Request body:
    {
        "email": "john@example.com",
        "password": "secure123"
    }
    """
    data = request.get_json()

    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required'}), 400

    email = data['email'].lower().strip()
    password = data['password']

    db = get_db()

    # Get user
    user = get_user_by_email(db, email)
    if not user:
        print(f"[DEBUG] Login failed: User not found for email {email}")
        return jsonify({'error': 'Invalid email or password'}), 401

    # Check if email is verified
    if not user.email_verified:
        print(f"[DEBUG] Login failed: Email not verified for {email}")
        return jsonify({'error': 'Please verify your email first. Check your inbox for the verification code.'}), 403

    # Verify password
    print(f"[DEBUG] Verifying password for user {email}")
    if not verify_password(password, user.password_hash):
        print(f"[DEBUG] Login failed: Invalid password for {email}")
        return jsonify({'error': 'Invalid email or password'}), 401

    print(f"[DEBUG] Login successful for {email}")

    # Update last login
    user.last_login = datetime.utcnow()
    save_user(db, user)

    # Generate JWT token
    token = generate_token(user.user_id, user.email)

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'token': token,
        'user': user.to_safe_dict()
    }), 200


# ============================================
# ENDPOINT: Get Current User
# ============================================
@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    Get current user info (protected route)
    Requires JWT token in Authorization header
    """
    db = get_db()
    user = get_user_by_email(db, request.user_email)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'success': True,
        'user': user.to_safe_dict()
    }), 200


# ============================================
# ENDPOINT: Update Profile
# ============================================
@auth_bp.route('/update-profile', methods=['PUT'])
@require_auth
def update_profile():
    """
    Update user profile (name, age, sex)
    Requires JWT token in Authorization header

    Request body:
    {
        "name": "John Doe",
        "age": 30,
        "sex": "male"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    db = get_db()
    user = get_user_by_email(db, request.user_email)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update fields if provided
    if 'name' in data:
        name = data['name'].strip()
        if not name or len(name) < 2:
            return jsonify({'error': 'Name must be at least 2 characters'}), 400
        user.name = name

    if 'age' in data:
        age = data['age']
        if not isinstance(age, int) or age < 18 or age > 120:
            return jsonify({'error': 'Age must be between 18 and 120'}), 400
        user.age = age

    if 'sex' in data:
        sex = data['sex']
        if sex not in ['male', 'female', 'other']:
            return jsonify({'error': 'Sex must be male, female, or other'}), 400
        user.sex = sex

    # Save updated user
    if not save_user(db, user):
        return jsonify({'error': 'Failed to update profile'}), 500

    return jsonify({
        'success': True,
        'message': 'Profile updated successfully',
        'user': user.to_safe_dict()
    }), 200


# ============================================
# ENDPOINT: Check Account Status (Debug)
# ============================================
@auth_bp.route('/check-account', methods=['POST'])
def check_account():
    """
    Debug endpoint to check account status

    Request body:
    {
        "email": "john@example.com"
    }
    """
    data = request.get_json()

    if 'email' not in data:
        return jsonify({'error': 'Email required'}), 400

    email = data['email'].lower().strip()
    db = get_db()

    user = get_user_by_email(db, email)

    if not user:
        return jsonify({
            'exists': False,
            'message': 'No account found with this email'
        }), 200

    return jsonify({
        'exists': True,
        'email': user.email,
        'name': user.name,
        'email_verified': user.email_verified,
        'created_at': user.created_at.isoformat() if isinstance(user.created_at, datetime) else user.created_at,
        'message': 'Account found' if user.email_verified else 'Account found but email not verified'
    }), 200


# ============================================
# ENDPOINT: Request Password Reset
# ============================================
@auth_bp.route('/reset-password-request', methods=['POST'])
def reset_password_request():
    """
    Request password reset - sends code to email

    Request body:
    {
        "email": "john@example.com"
    }
    """
    data = request.get_json()

    if 'email' not in data:
        return jsonify({'error': 'Email required'}), 400

    email = data['email'].lower().strip()
    db = get_db()

    user = get_user_by_email(db, email)
    if not user:
        # Don't reveal if email exists or not
        return jsonify({
            'success': True,
            'message': 'If an account exists with this email, a reset code has been sent'
        }), 200

    # Generate reset code
    code = generate_verification_code()
    if not save_verification_code(db, email, code):
        return jsonify({'error': 'Failed to generate reset code'}), 500

    # Send reset email
    email_sent = send_verification_email(email, code, user.name)

    return jsonify({
        'success': True,
        'message': 'Reset code sent to your email',
        'email_sent': email_sent,
        'debug_code': code if not email_sent else None
    }), 200


# ============================================
# ENDPOINT: Reset Password with Code
# ============================================
@auth_bp.route('/reset-password-confirm', methods=['POST'])
def reset_password_confirm():
    """
    Reset password using verification code

    Request body:
    {
        "email": "john@example.com",
        "code": "123456",
        "new_password": "newsecurepassword"
    }
    """
    data = request.get_json()

    required_fields = ['email', 'code', 'new_password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    email = data['email'].lower().strip()
    code = data['code'].strip()
    new_password = data['new_password']

    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    db = get_db()

    # Verify code
    verification = get_verification_code(db, email)
    if not verification:
        return jsonify({'error': 'No reset code found. Please request a new one.'}), 404

    if verification.is_expired():
        delete_verification_code(db, email)
        return jsonify({'error': 'Reset code expired. Please request a new one.'}), 400

    if verification.code != code:
        return jsonify({'error': 'Invalid reset code'}), 400

    # Get user
    user = get_user_by_email(db, email)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Update password
    user.password_hash = hash_password(new_password)

    if not save_user(db, user):
        return jsonify({'error': 'Failed to reset password'}), 500

    # Delete verification code
    delete_verification_code(db, email)

    return jsonify({
        'success': True,
        'message': 'Password reset successful. You can now log in with your new password.'
    }), 200


# ============================================
# ENDPOINT: Get User's Analysis Reports
# ============================================
@auth_bp.route('/my-reports', methods=['GET'])
@require_auth
def get_my_reports():
    """
    Get all analysis reports for the authenticated user
    Requires JWT token in Authorization header
    """
    db = get_db()
    user = get_user_by_email(db, request.user_email)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get all sessions for this user
    sessions = get_user_sessions(db, user.user_id)

    # Build report list with summary information
    reports = []
    for session in sessions:
        report = {
            'session_id': session.session_id,
            'original_filename': session.original_filename,
            'status': session.status,
            'created_at': session.created_at.isoformat() if isinstance(session.created_at, datetime) else session.created_at,
            'has_genetic_results': session.has_genetic_results,
            'has_questionnaire': session.has_questionnaire,
            'has_recommendations': session.has_recommendations,
            'is_complete': session.status == 'complete'
        }
        reports.append(report)

    return jsonify({
        'success': True,
        'total_reports': len(reports),
        'reports': reports
    }), 200
