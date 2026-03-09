# Security Setup - Quick Start Guide

## 🔒 5-Minute Security Setup

### Step 1: Generate Encryption Key

```bash
cd nutrigenomics
python app/encryption.py
```

Copy the generated key and add it to your `.env` file:

```bash
ENCRYPTION_KEY=the-key-you-just-generated
```

**⚠️ IMPORTANT:** Save this key securely! Store it in:
- Password manager
- Secure backup location
- Production secrets management system

### Step 2: Set Secure SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Add to `.env`:

```bash
SECRET_KEY=the-generated-secret-key
```

### Step 3: Configure File Permissions (Linux/Mac)

```bash
# Restrict upload folder
chmod 700 uploads/

# Restrict .env file
chmod 600 .env
```

### Step 4: Verify Encryption is Working

Start your server and upload a test file:

```bash
python run.py
```

Check the console output - you should see:
```
[SECURITY] File encrypted: uploads/xxxxx_filename.txt.encrypted
```

### Step 5: Configure MongoDB Security (Production)

Update `.env`:

```bash
# Replace with your MongoDB Atlas or secured instance
MONGODB_URI=mongodb://username:password@host:27017/nutrigenomics?tls=true&authSource=admin
```

---

## ✅ Security Features Enabled

Once setup is complete, you have:

- ✅ **File Encryption** - All uploads automatically encrypted
- ✅ **Auto Cleanup** - Files deleted after analysis
- ✅ **Secure Deletion** - 3-pass overwrite before deletion
- ✅ **Database Encryption** - Genetic findings encrypted
- ✅ **Password Hashing** - bcrypt with 12 rounds
- ✅ **JWT Authentication** - 7-day token expiration

---

## 🔍 Verify Your Security

### Check 1: Files are Encrypted

```bash
ls uploads/
```

You should see files ending in `.encrypted`

### Check 2: Original Files are Deleted

After analysis, there should be NO unencrypted `.txt` or `.csv` files in `uploads/`

### Check 3: Database Contains Encrypted Data

```bash
# Connect to MongoDB
mongosh

use nutrigenomics

# Check genetic results - fields should be encrypted
db.genetic_results.findOne()
```

You should see `genotype_encrypted`, `interpretation_encrypted` fields with encrypted data.

---

## 🚨 Security Incidents

### If Encryption Key is Lost

**DATA LOSS - Encrypted data cannot be recovered!**

Prevention:
1. Back up `ENCRYPTION_KEY` immediately
2. Store in password manager
3. Document key location in runbook

### If Encryption Key is Compromised

1. Generate new key: `python app/encryption.py`
2. Stop the application
3. Update `.env` with new key
4. Re-encrypt all existing data (requires custom migration)
5. Restart application

---

## 📚 More Information

See [security_guide.md](./security_guide.md) for complete documentation.

---

## 🆘 Support

Found a security issue? Report it privately:
- Create a GitHub issue (mark as security)
- Or email: (add security contact)

**DO NOT** publicly disclose security vulnerabilities before they are fixed.
