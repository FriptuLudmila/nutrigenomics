# Email-Verified Authentication Setup Guide

## Overview

Your Nutrigenomics application now has a complete email-verified authentication system. Users must:
1. Register with name, age, sex, email, and password
2. Receive a 6-digit verification code via email
3. Verify their email before accessing the app
4. Sign in with email and password

## Features Implemented

### Backend (Python/Flask)
- ✅ Updated User model with `age`, `sex`, and `email_verified` fields
- ✅ Created `VerificationCode` model for temporary codes
- ✅ Email sending functionality via SMTP
- ✅ Authentication API endpoints:
  - `POST /api/auth/register` - Register and send verification code
  - `POST /api/auth/verify` - Verify email with code
  - `POST /api/auth/resend-code` - Resend verification code
  - `POST /api/auth/login` - Sign in
  - `GET /api/auth/me` - Get current user (protected)
- ✅ JWT token generation and validation
- ✅ Password hashing with bcrypt

### Frontend (Next.js/React)
- ✅ Multi-step authentication modal:
  - Sign in form
  - Sign up form (name, age, sex, email, password)
  - Email verification form (6-digit code)
- ✅ Form validation
- ✅ Error and success messages
- ✅ Resend code functionality
- ✅ JWT token storage in localStorage

## Setup Instructions

### 1. Install Required Python Packages

The email functionality requires no additional packages beyond what you already have:
- `smtplib` (built-in)
- `email` (built-in)

### 2. Configure Email Settings

#### Option A: Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the generated 16-character password

3. **Update your `.env` file**:
```bash
# Email settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
```

#### Option B: Other Email Providers

**Outlook/Hotmail:**
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_EMAIL=your-email@outlook.com
SMTP_PASSWORD=your-password
```

**Custom SMTP Server:**
```bash
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_EMAIL=your-email@domain.com
SMTP_PASSWORD=your-password
```

### 3. Development Mode (No Email Required)

If you don't configure SMTP credentials, the system will:
- Print the verification code to the console
- Return the code in the API response as `debug_code`
- Display the code in the frontend success message

This is perfect for development and testing!

### 4. Update Secret Key

Make sure to set a secure secret key in `.env`:
```bash
SECRET_KEY=your-very-secure-random-secret-key-here
```

Generate a secure key with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## API Endpoints Documentation

### POST /api/auth/register
Register a new user and send verification code.

**Request:**
```json
{
  "name": "John Doe",
  "age": 30,
  "sex": "male",
  "email": "john@example.com",
  "password": "secure123"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Verification code sent to your email",
  "email": "john@example.com",
  "email_sent": true,
  "debug_code": null
}
```

**Response (Development - No Email):**
```json
{
  "success": true,
  "message": "Verification code sent to your email",
  "email": "john@example.com",
  "email_sent": false,
  "debug_code": "123456"
}
```

### POST /api/auth/verify
Verify email with the 6-digit code.

**Request:**
```json
{
  "email": "john@example.com",
  "code": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email verified successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "uuid-here",
    "email": "john@example.com",
    "name": "John Doe",
    "age": 30,
    "sex": "male",
    "email_verified": true,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### POST /api/auth/resend-code
Resend verification code if it expired.

**Request:**
```json
{
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Verification code sent",
  "email_sent": true,
  "debug_code": null
}
```

### POST /api/auth/login
Sign in with email and password.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "secure123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "uuid-here",
    "email": "john@example.com",
    "name": "John Doe",
    "age": 30,
    "sex": "male",
    "email_verified": true,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### GET /api/auth/me
Get current authenticated user (requires JWT token).

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "success": true,
  "user": {
    "user_id": "uuid-here",
    "email": "john@example.com",
    "name": "John Doe",
    "age": 30,
    "sex": "male",
    "email_verified": true,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

## User Flow

### Registration Flow
1. User clicks "Analyze My Data" or "Sign In" on landing page
2. Modal opens, user clicks "Sign up"
3. User fills: name, age, sex, email, password
4. User clicks "Create Account"
5. Backend sends 6-digit code to email
6. Modal switches to verification screen
7. User enters 6-digit code
8. User clicks "Verify"
9. Backend validates code and marks email as verified
10. User receives JWT token
11. User is redirected to `/app`

### Login Flow
1. User clicks "Sign In"
2. Modal opens with sign in form
3. User enters email and password
4. User clicks "Sign In"
5. Backend validates credentials and email_verified flag
6. User receives JWT token
7. User is redirected to `/app`

## Security Features

- ✅ Passwords hashed with bcrypt (salt rounds: 12)
- ✅ JWT tokens expire after 7 days
- ✅ Verification codes expire after 15 minutes
- ✅ Email verification required before login
- ✅ Protected routes with `@require_auth` decorator
- ✅ Email normalization (lowercase, trimmed)
- ✅ Input validation (age 18-120, password min 6 chars)

## Database Collections

### users
```javascript
{
  user_id: "uuid",
  email: "user@example.com",
  password_hash: "bcrypt-hash",
  name: "John Doe",
  age: 30,
  sex: "male",
  email_verified: true,
  created_at: ISODate("2024-01-01T00:00:00Z"),
  last_login: ISODate("2024-01-01T00:00:00Z")
}
```

### verification_codes
```javascript
{
  email: "user@example.com",
  code: "123456",
  created_at: ISODate("2024-01-01T00:00:00Z"),
  expires_at: ISODate("2024-01-01T00:15:00Z")
}
```

## Testing

### Test Without Email (Development Mode)

1. Start the backend:
```bash
python run.py
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Go to http://localhost:3000
4. Click "Analyze My Data" or "Get Started"
5. Click "Sign up"
6. Fill in the form
7. Check the console/terminal - you'll see the verification code printed
8. Enter the code shown in the success message

### Test With Email (Production Mode)

1. Configure SMTP settings in `.env`
2. Restart the backend
3. Register with a real email
4. Check your email inbox for the verification code
5. Enter the code to complete registration

## Troubleshooting

### Verification code not received
- Check spam/junk folder
- Verify SMTP credentials in `.env`
- Check backend console for error messages
- Use "Resend Code" button

### "Email already registered" error
- The email is already in the database
- Try signing in instead
- Or use a different email

### "Please verify your email first" error
- The account exists but email is not verified
- Request a new verification code at registration
- Or delete the user from MongoDB and re-register

### JWT token expired
- Tokens expire after 7 days
- User needs to sign in again
- Consider implementing refresh tokens for longer sessions

## Next Steps

### Recommended Enhancements
1. **Password Reset Flow** - Allow users to reset forgotten passwords
2. **Email Change Flow** - Allow users to change email with re-verification
3. **Refresh Tokens** - Implement refresh tokens for automatic session renewal
4. **Account Deletion** - Add GDPR-compliant account deletion
5. **Rate Limiting** - Prevent brute force and code spam
6. **Session Management** - Link sessions to users for multi-device support

### Production Checklist
- [ ] Use environment-specific SMTP credentials
- [ ] Set secure SECRET_KEY (not the default)
- [ ] Enable HTTPS for frontend and backend
- [ ] Set up email delivery monitoring
- [ ] Implement rate limiting on auth endpoints
- [ ] Add logging for security events
- [ ] Set up monitoring and alerts
