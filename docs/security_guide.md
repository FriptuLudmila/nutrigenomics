# Security Implementation Guide

## Overview

The Nutrigenomics API implements multiple layers of security to protect sensitive genetic data:

1. **File Encryption** - Uploaded genetic data files are encrypted at rest
2. **Data Encryption** - Genetic findings stored in MongoDB are encrypted
3. **Password Security** - User passwords hashed with bcrypt
4. **JWT Authentication** - Secure token-based authentication
5. **Automatic Cleanup** - Files deleted after analysis
6. **Secure Deletion** - Files overwritten before deletion

---

## 1. File Encryption (NEW ✨)

### What's Protected

All uploaded genetic data files (`.txt`, `.csv`, `.zip`) are **automatically encrypted** when uploaded.

### How It Works

```
User Upload → Save to disk → Encrypt file → Delete original → Store encrypted file
```

**Location:** [app/file_encryption.py](../app/file_encryption.py)

**Algorithm:** AES-128-CBC (Fernet symmetric encryption)

**Key Storage:** Environment variable `ENCRYPTION_KEY`

### Implementation Details

- Files are encrypted **immediately** after upload
- Original unencrypted files are **deleted** automatically
- Encrypted files use `.encrypted` extension
- During analysis, files are **temporarily decrypted** in memory
- After analysis, **all files are securely deleted** (encrypted findings remain in database)

---

## 2. Database Encryption

### Genetic Findings

The following fields are encrypted before storing in MongoDB:

- **Genotype** (e.g., "CT", "AA")
- **Interpretation** text
- **Recommendation** text

**NOT encrypted** (needed for filtering/queries):
- rsid, gene, condition, risk_level

### Implementation

See [app/encryption.py](../app/encryption.py) - `encrypt_genetic_findings()` function

---

## 3. Secure File Deletion

### Why It Matters

Simply deleting a file doesn't remove the data from disk. The data remains until overwritten.

### Our Solution

**Secure deletion** overwrites files with random data **3 times** before deletion.

```python
# From app/file_encryption.py
secure_delete_file(file_path, overwrite_passes=3)
```

This ensures genetic data **cannot be recovered** from the filesystem.

---

## 4. Automatic Cleanup

### After Analysis

Once genetic data is analyzed and stored encrypted in the database:

1. ✅ Encrypted file is deleted
2. ✅ Temporary decrypted file is deleted
3. ✅ Only encrypted findings remain in MongoDB

### On Session Deletion (GDPR)

When a user deletes their data via `DELETE /api/session/<id>`:

1. ✅ All files securely deleted (3-pass overwrite)
2. ✅ All database records deleted
3. ✅ Data is permanently removed

---

## 5. Setup Instructions

### Required Environment Variables

Add these to your `.env` file:

```bash
# Encryption key for genetic data (REQUIRED)
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-encryption-key-here

# JWT secret key (REQUIRED)
SECRET_KEY=your-secret-key-here

# MongoDB connection (REQUIRED)
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=nutrigenomics
```

### Generate Encryption Key

```bash
python app/encryption.py
```

This will generate a new key and test the encryption system.

**CRITICAL:** Save this key securely! Losing it means **you cannot decrypt existing data**.

---

## 6. MongoDB Security Configuration

### Enable TLS/SSL (Recommended for Production)

Update your `.env`:

```bash
# MongoDB with TLS
MONGODB_URI=mongodb://username:password@host:27017/nutrigenomics?tls=true&tlsCAFile=/path/to/ca.pem
```

### Enable Authentication

```bash
# Create admin user in MongoDB
use admin
db.createUser({
  user: "nutrigenomics_admin",
  pwd: "secure_password_here",
  roles: ["readWrite", "dbAdmin"]
})

# Update connection string
MONGODB_URI=mongodb://nutrigenomics_admin:secure_password_here@localhost:27017/nutrigenomics?authSource=admin
```

### Network Security

- **Firewall:** Only allow MongoDB connections from your app server
- **Bind IP:** Configure MongoDB to only listen on localhost if possible

---

## 7. File System Permissions

### Linux/Mac

```bash
# Restrict upload folder to app user only
chmod 700 uploads/
chown appuser:appuser uploads/

# Restrict config files
chmod 600 .env
```

### Windows

```powershell
# Restrict upload folder
icacls uploads /inheritance:r /grant:r "%USERNAME%:(OI)(CI)F"

# Restrict .env file
icacls .env /inheritance:r /grant:r "%USERNAME%:R"
```

---

## 8. Production Checklist

### Required

- [x] ✅ Set secure `ENCRYPTION_KEY` in production
- [x] ✅ Set secure `SECRET_KEY` for JWT
- [x] ✅ Enable HTTPS for API endpoints
- [x] ✅ Enable HTTPS for frontend
- [ ] ⚠️ Enable MongoDB authentication
- [ ] ⚠️ Enable MongoDB TLS/SSL
- [ ] ⚠️ Set up file system permissions
- [ ] ⚠️ Configure firewall rules

### Recommended

- [ ] Set up rate limiting on API endpoints
- [ ] Enable audit logging for data access
- [ ] Set up monitoring and alerts
- [ ] Regular security audits
- [ ] Backup encryption keys securely (offline storage)
- [ ] Key rotation policy (annually)

---

## 9. Data Flow Diagram

### Upload & Analysis

```
1. User uploads file
   ↓
2. Save to disk (temporary)
   ↓
3. Encrypt file with Fernet
   ↓
4. Delete original unencrypted file
   ↓
5. Store encrypted file path in database
   ↓
[User requests analysis]
   ↓
6. Decrypt file temporarily
   ↓
7. Parse genetic data
   ↓
8. Encrypt findings (genotypes, interpretations)
   ↓
9. Save encrypted findings to MongoDB
   ↓
10. Securely delete ALL files (encrypted + temp)
    ↓
11. Only encrypted findings remain in database
```

### Data Access

```
User requests recommendations
   ↓
Fetch encrypted findings from MongoDB
   ↓
Decrypt in memory
   ↓
Generate recommendations
   ↓
Return to user
   ↓
Decrypted data never touches disk
```

---

## 10. Security Features Summary

| Feature | Status | Implementation |
|---------|--------|----------------|
| File encryption at rest | ✅ Enabled | AES-128 (Fernet) |
| Database encryption | ✅ Enabled | Selected fields encrypted |
| Password hashing | ✅ Enabled | bcrypt (12 rounds) |
| JWT authentication | ✅ Enabled | 7-day expiration |
| Secure file deletion | ✅ Enabled | 3-pass overwrite |
| Auto cleanup after analysis | ✅ Enabled | Immediate |
| GDPR compliance | ✅ Enabled | DELETE endpoint |
| MongoDB TLS | ⚠️ Manual | Configure in production |
| Rate limiting | ❌ TODO | Future enhancement |
| Audit logging | ❌ TODO | Future enhancement |

---

## 11. Incident Response

### If Encryption Key is Compromised

1. Generate a new encryption key
2. Re-encrypt all existing data with new key
3. Update `ENCRYPTION_KEY` in `.env`
4. Restart application
5. Invalidate all user JWT tokens (force re-login)

### If Database is Breached

- Encrypted data remains protected (requires encryption key)
- File uploads are encrypted (separate key)
- User passwords are hashed (cannot be reversed)

### If File System is Breached

- All uploaded files are encrypted
- Requires `ENCRYPTION_KEY` to decrypt
- Original files are deleted after analysis

---

## 12. Compliance

### GDPR

- ✅ Right to deletion (DELETE endpoint)
- ✅ Data encryption at rest
- ✅ Secure data handling
- ✅ Data minimization (only essential data stored)
- ⚠️ Requires privacy policy and user consent (frontend)

### HIPAA (if applicable)

- ✅ Encryption in transit (HTTPS)
- ✅ Encryption at rest (files + database)
- ✅ Access controls (JWT authentication)
- ⚠️ Requires audit logging
- ⚠️ Requires BAA with cloud providers

---

## 13. Support

For security questions or to report vulnerabilities:

- **GitHub Issues:** (for non-sensitive issues)
- **Email:** (add security contact email)
- **Security Policy:** See SECURITY.md

**DO NOT** publicly disclose security vulnerabilities.
