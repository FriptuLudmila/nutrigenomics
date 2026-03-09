"""
Quick Password Reset Script
===========================
Manually reset a user's password in MongoDB
"""

from app.database import get_db
from app.auth import hash_password, get_user_by_email, save_user

def reset_password(email: str, new_password: str):
    """Reset password for a user"""
    db = get_db()

    # Get user
    user = get_user_by_email(db, email)
    if not user:
        print(f"[ERROR] User not found: {email}")
        return False

    # Hash new password
    new_hash = hash_password(new_password)

    # Update user
    user.password_hash = new_hash

    # Save
    if save_user(db, user):
        print(f"[OK] Password reset successful for {email}")
        print(f"    New password: {new_password}")
        return True
    else:
        print(f"[ERROR] Failed to save password")
        return False

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <email> <new_password>")
        print("Example: python reset_password.py user@example.com newpass123")
        sys.exit(1)

    email = sys.argv[1]
    new_password = sys.argv[2]

    print(f"\nResetting password for: {email}")
    print(f"New password: {new_password}")
    print("-" * 50)

    reset_password(email, new_password)
