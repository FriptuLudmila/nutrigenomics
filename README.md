# Nutrigenomics — Personalized Dietary Recommendations from Genetic Data

A full-stack web application that analyzes raw genetic data files (23andMe, AncestryDNA) across 25 clinically-relevant SNPs and generates personalized nutrition recommendations, supplement advice, and AI-powered meal plans based on a user's unique genome and lifestyle.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [How It Works — End-to-End Flow](#how-it-works--end-to-end-flow)
3. [Database Design](#database-design)
4. [Authentication & Security](#authentication--security)
5. [Encryption](#encryption)
6. [Genetic Analysis — 25 SNPs](#genetic-analysis--25-snps)
7. [Recommendation Engine](#recommendation-engine)
8. [AI Meal Planner](#ai-meal-planner)
9. [Frontend](#frontend)
10. [API Reference](#api-reference)
11. [Environment Variables](#environment-variables)
12. [Setup & Running Locally](#setup--running-locally)
13. [What Is Missing / Should Be Implemented](#what-is-missing--should-be-implemented)

---

## Project Structure

```
nutrigenomics/
├── app/                        # Flask backend (Python)
│   ├── __init__.py             # App factory, CORS, blueprint registration
│   ├── config.py               # Environment-based configuration
│   ├── database.py             # MongoDB connection and helpers
│   ├── models.py               # Dataclasses + DB read/write functions
│   ├── routes.py               # Core analysis API endpoints
│   ├── auth.py                 # Auth logic: hashing, JWT, email, verification
│   ├── auth_routes.py          # Auth endpoints (register, login, reset, etc.)
│   ├── genetic_parser.py       # SNP parser + nutrigenomics analysis engine
│   ├── encryption.py           # Encrypt/decrypt genetic findings stored in DB
│   ├── file_encryption.py      # Encrypt/decrypt genome files on disk
│   └── ai_meal_planner.py      # Groq API integration for meal plan generation
├── frontend/                   # Next.js 14 frontend (TypeScript)
│   ├── app/
│   │   ├── page.tsx            # Root landing page
│   │   ├── layout.tsx          # Root layout with fonts and metadata
│   │   ├── app/page.tsx        # Protected main analysis page (4-step flow)
│   │   └── app/profile/page.tsx # User profile and past session history
│   ├── components/
│   │   ├── AuthModal.tsx       # Multi-step register/login modal
│   │   ├── FileUpload.tsx      # Drag-and-drop genome file upload
│   │   ├── Questionnaire.tsx   # Lifestyle questionnaire form
│   │   ├── RecommendationsReport.tsx  # Full report display
│   │   ├── MealPlanGenerator.tsx      # AI meal plan UI
│   │   └── NutrientRadarChart.tsx     # Radar chart visualization
│   └── lib/
│       └── api.ts              # Axios-based typed API client
├── docs/                       # Implementation guides and diagrams
├── uploads/                    # Temporary encrypted genome file storage
├── run.py                      # Flask dev server entry point
├── reset_password.py           # CLI script for direct password reset
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── SETUP_GUIDE.md              # Step-by-step setup instructions
```

---

## How It Works — End-to-End Flow

### Step 1: Register / Login
- User registers with name, age, sex, email, and password
- A 6-digit verification code is emailed (15-minute expiry)
- On successful verification, a JWT token is issued and stored in `localStorage`

### Step 2: Upload Genome File
- User uploads a `.txt`, `.csv`, or `.zip` file from 23andMe or AncestryDNA (max 50 MB)
- File is saved temporarily, then encrypted with Fernet (AES-128) and stored as `.encrypted`
- The original plaintext file is securely deleted (3-pass overwrite)
- A `session_id` is returned and used for all subsequent steps

### Step 3: Genetic Analysis
- The encrypted file is temporarily decrypted into memory
- The `snps` library parses the raw genetic data
- 25 nutrigenomics-relevant SNPs are looked up and interpreted
- Sensitive fields (genotype, interpretation, recommendation) are encrypted before DB storage
- The decrypted file copy is immediately deleted; only encrypted data remains in MongoDB

### Step 4: Lifestyle Questionnaire
- User answers questions about activity level, diet type, allergies, health goals, supplements, etc.
- Answers are stored in the `questionnaires` collection and used to personalize recommendations

### Step 5: Recommendations
- Genetic findings (decrypted from DB) are cross-referenced with questionnaire answers
- Recommendations are generated in categories: high priority, moderate priority, general advice, foods to increase/limit, supplements to consider
- A nutrient radar chart is built from the risk scores of the 25 SNPs

### Step 6: AI Meal Plan (Optional)
- User requests a 1–7 day meal plan
- The system sends genetic findings + questionnaire answers to Groq's Llama 3.3 70B model
- A structured JSON meal plan is returned with breakfast, lunch, dinner, snacks, macros, and genetic notes

---

## Database Design

**Database:** MongoDB
**DB Name:** `nutrigenomics` (configurable via env var)

### Collection: `users`

| Field | Type | Description |
|---|---|---|
| `user_id` | string (UUID) | Unique user identifier |
| `email` | string | Unique, lowercased |
| `password_hash` | string | bcrypt hash (12 rounds) |
| `name` | string | Display name (min 2 chars) |
| `age` | int | 18–120 |
| `sex` | string | `male` / `female` / `other` |
| `email_verified` | bool | Must be `true` to log in |
| `created_at` | datetime | UTC timestamp |
| `last_login` | datetime | Updated on each login |

**Indexes:** `email` (unique), `user_id` (unique)

---

### Collection: `sessions`

| Field | Type | Description |
|---|---|---|
| `session_id` | string (UUID) | Unique session identifier |
| `user_id` | string / null | Linked user (optional) |
| `filepath` | string | Path to encrypted genome file |
| `original_filename` | string | Original upload name |
| `status` | string | `uploaded` → `analyzed` → `questionnaire_completed` → `complete` |
| `file_size_bytes` | int | Upload size |
| `has_genetic_results` | bool | Analysis done |
| `has_questionnaire` | bool | Questionnaire submitted |
| `has_recommendations` | bool | Recommendations generated |
| `created_at` | datetime | UTC |
| `updated_at` | datetime | UTC |

**Indexes:** `session_id` (unique), `user_id`, `created_at`

---

### Collection: `genetic_results`

| Field | Type | Description |
|---|---|---|
| `session_id` | string | Links to session |
| `source` | string | `23andMe`, `AncestryDNA`, `Unknown` |
| `snp_count` | int | Total SNPs in uploaded file |
| `build` | int | Reference genome build (37 or 38) |
| `findings_encrypted` | array | 25 findings, with sensitive fields encrypted |
| `summary` | object | Counts of high/moderate/low/protective risk findings |
| `analyzed_at` | datetime | UTC |

Each finding inside `findings_encrypted`:

```json
{
  "rsid": "rs4988235",
  "gene": "LCT/MCM6",
  "condition": "Lactose Intolerance",
  "risk_level": "high",
  "genotype_encrypted": "...",
  "interpretation_encrypted": "...",
  "recommendation_encrypted": "..."
}
```

**What is stored in plain text:** `rsid`, `gene`, `condition`, `risk_level` (needed for querying/aggregation)
**What is encrypted:** `genotype`, `interpretation`, `recommendation` (sensitive personal data)

**Indexes:** `session_id` (unique)

---

### Collection: `questionnaires`

Stores the full answers object from the lifestyle questionnaire:

```json
{
  "session_id": "...",
  "answers": {
    "age": 30,
    "sex": "female",
    "activity_level": "moderate",
    "diet_type": "vegetarian",
    "alcohol_frequency": "never",
    "caffeine_cups_per_day": 1,
    "digestive_issues": ["bloating"],
    "health_goals": ["energy", "weight_loss"],
    "current_supplements": ["vitamin_d"],
    "known_allergies": ["nuts"]
  },
  "submitted_at": "..."
}
```

**Indexes:** `session_id` (unique)

---

### Collection: `recommendations`

Stores generated recommendations per session:

```json
{
  "session_id": "...",
  "recommendations": {
    "high_priority": [ { "category": "...", "genetic_basis": "...", "recommendation": "..." } ],
    "moderate_priority": [ ... ],
    "general_advice": [ ... ],
    "foods_to_increase": ["leafy greens", "lactose-free milk"],
    "foods_to_limit": ["regular dairy"],
    "supplements_to_consider": ["Methylfolate (L-5-MTHF)"]
  },
  "generated_at": "..."
}
```

**Indexes:** `session_id` (unique)

---

### Collection: `verification_codes`

```json
{
  "email": "user@example.com",
  "code": "847291",
  "created_at": "...",
  "expires_at": "..."
}
```

**TTL Index:** on `expires_at` — MongoDB auto-deletes expired codes.
Used for both email verification (registration) and password reset.

---

## Authentication & Security

### Registration Flow

1. User submits `name`, `age`, `sex`, `email`, `password` (min 6 chars)
2. Input validation runs (email format, age 18–120, sex enum)
3. Password is hashed with **bcrypt** (12 salt rounds)
4. 6-digit verification code is generated and emailed (SMTP)
5. User is saved with `email_verified: false`
6. User enters the code; backend validates it against the DB (15-minute window)
7. `email_verified` is set to `true`
8. A **JWT token** (HS256, 7-day expiry) is returned

### Login Flow

1. User submits `email` + `password`
2. Backend verifies `email_verified: true` (unverified accounts cannot log in)
3. `bcrypt` compares submitted password against stored hash
4. On success: `last_login` updated, JWT token returned
5. Token stored in `localStorage` as `auth_token`
6. All protected routes use `Authorization: Bearer <token>` header

### Password Reset Flow

1. `POST /api/auth/reset-password-request` — sends 6-digit code to email
2. `POST /api/auth/reset-password-confirm` — validates code and updates password hash
3. CLI alternative: `python reset_password.py <email> <new_password>` (direct DB update)

### JWT Details

- **Algorithm:** HS256
- **Payload:** `{ user_id, email, exp, iat }`
- **Expiry:** 7 days
- **Secret:** `SECRET_KEY` environment variable

### Implemented Security Measures

- Passwords hashed with bcrypt (12 rounds)
- Email verification required before any login
- JWT expiration enforced
- File encryption on disk (Fernet/AES-128)
- Genetic data fields encrypted in MongoDB
- Secure file deletion (3-pass overwrite before `os.remove`)
- Verification codes expire in 15 minutes (TTL index)
- CORS open (configurable in `app/__init__.py`)
- Input validation on all registration fields

---

## Encryption

### File Encryption (`file_encryption.py`)

**Algorithm:** Fernet (wraps AES-128-CBC + HMAC-SHA256)
**Key:** `ENCRYPTION_KEY` environment variable (base64-encoded 32-byte Fernet key)

**Lifecycle:**
```
Upload → Save to disk → Encrypt → Delete original (3-pass overwrite)
                ↓
          Analysis requested
                ↓
       Decrypt to temp file → Parse → Delete temp file
                ↓
       Store encrypted findings in MongoDB → Delete encrypted file from disk
```

After analysis, the genome file is completely gone from disk. Only structured findings remain in MongoDB, themselves encrypted.

**Key functions:**
- `encrypt_and_replace(filepath)` — encrypts and securely deletes original
- `decrypt_file(filepath)` — returns path to temporary decrypted copy
- `secure_delete_file(filepath, passes=3)` — overwrites with random bytes before deleting
- `cleanup_session_files(filepath)` — removes all files related to a session

### Database Encryption (`encryption.py`)

**Algorithm:** Fernet symmetric encryption
**Key:** Same `ENCRYPTION_KEY` environment variable

**Encrypted fields per genetic finding:**
- `genotype` (e.g. `"CT"`) → `genotype_encrypted`
- `interpretation` (text explanation) → `interpretation_encrypted`
- `recommendation` (dietary advice) → `recommendation_encrypted`

**Plain (queryable) fields:** `rsid`, `gene`, `condition`, `risk_level`

> **Critical:** If `ENCRYPTION_KEY` is lost or changed, all stored genetic data becomes permanently unrecoverable. Back up this key securely.

To generate a key: `python app/encryption.py`

---

## Genetic Analysis — 25 SNPs

The engine uses the [`snps`](https://pypi.org/project/snps/) library to parse raw 23andMe/AncestryDNA files and looks up 25 specific rsIDs.

### Category 1: Digestive & Food Tolerance

| rsID | Gene | Condition |
|---|---|---|
| rs4988235 | LCT/MCM6 | Lactose Intolerance |
| rs2187668 | HLA-DQ2.5 | Celiac Disease Risk |
| rs1726866 | TAS2R38 | Bitter Taste Perception |
| rs1761667 | CD36 | Fat Taste Sensitivity |

### Category 2: Caffeine & Alcohol

| rsID | Gene | Condition |
|---|---|---|
| rs762551 | CYP1A2 | Caffeine Metabolism Speed |
| rs671 | ALDH2 | Alcohol Flush Reaction |
| rs1229984 | ADH1B | Alcohol Metabolism Speed |

### Category 3: Vitamins & Minerals

| rsID | Gene | Condition |
|---|---|---|
| rs1801133 | MTHFR | Folate Metabolism (C677T) |
| rs1801131 | MTHFR | Folate Metabolism (A1298C) |
| rs602662 | FUT2 | Vitamin B12 Absorption |
| rs1801394 | MTRR | B12 Utilization |
| rs2228570 | VDR | Vitamin D Receptor |
| rs7041 | GC | Vitamin D Transport |
| rs33972313 | SLC23A1 | Vitamin C Absorption |
| rs1799945 | HFE | Iron Absorption (H63D) |

### Category 4: Macronutrient Metabolism

| rsID | Gene | Condition |
|---|---|---|
| rs174546 | FADS1 | Omega-3/6 Fatty Acid Conversion |
| rs5082 | APOA2 | Saturated Fat Sensitivity |
| rs7903146 | TCF7L2 | Carbohydrate Metabolism / Diabetes Risk |
| rs9939609 | FTO | Obesity Risk / Satiety |
| rs4341 | ACE | Exercise Response / Muscle Type |
| rs7412 | APOE | Fat Metabolism (APOE e2/e3/e4) |

### Category 5: Antioxidant & Detox

| rsID | Gene | Condition |
|---|---|---|
| rs4880 | SOD2 | Antioxidant Capacity |
| rs1695 | GSTP1 | Glutathione Detoxification |
| rs7501331 | BCMO1 | Beta-Carotene → Vitamin A Conversion |
| rs7946 | PEMT | Choline Requirements |

### Risk Levels

Each finding is assigned one of:

| Level | Score | Meaning |
|---|---|---|
| `low` | 20 | No significant concern |
| `moderate` | 60 | Some attention recommended |
| `high` | 100 | Significant dietary action needed |
| `protective` | 10 | Genotype is advantageous |

---

## Recommendation Engine

The recommendation engine in `routes.py → generate_personalized_recommendations()` takes:
- `findings` — decrypted list of 25 genetic findings
- `questionnaire_answers` — user's lifestyle data

It cross-references each finding's genotype against the questionnaire (e.g., if a user has high lactose intolerance risk AND reports digestive issues, the recommendation is strengthened). Output structure:

```json
{
  "high_priority": [ { "category": "...", "genetic_basis": "...", "recommendation": "...", "personalized_note": "..." } ],
  "moderate_priority": [ ... ],
  "general_advice": [ ... ],
  "foods_to_increase": [ "..." ],
  "foods_to_limit": [ "..." ],
  "supplements_to_consider": [ "..." ]
}
```

Duplicate recommendations are deduplicated before returning.

---

## AI Meal Planner

**Provider:** [Groq](https://groq.com) — Llama 3.3 70B model
**Key:** `GROQ_API_KEY` environment variable

### How It Works

1. Retrieve session's genetic findings and questionnaire answers from DB
2. Build a structured prompt containing:
   - User profile (diet type, activity, allergies, health goals)
   - Top high-priority genetic concerns
   - Foods to prioritize and minimize
3. Request JSON-formatted meal plan from Groq
4. Return day-by-day plan with meals, ingredients, macros, and genetic notes

### Output Structure

```json
{
  "days": [
    {
      "day": 1,
      "genetic_note": "High MTHFR risk — meals rich in methylfolate",
      "meals": {
        "breakfast": { "name": "...", "description": "...", "ingredients": [...], "macros": { "protein_g": 25, "carbs_g": 30, "fats_g": 10 } },
        "lunch": { ... },
        "dinner": { ... },
        "snacks": [ { "name": "...", "description": "...", "macros": { ... } } ]
      }
    }
  ]
}
```

If the Groq API is unavailable, a static fallback with general tips is returned (`fallback: true`).

---

## Frontend

**Framework:** Next.js 14 (App Router) with TypeScript and Tailwind CSS

### Pages

| Route | Description |
|---|---|
| `/` | Public landing page with login/register CTA |
| `/app` | Protected 4-step analysis flow (upload → analyze → questionnaire → results) |
| `/app/profile` | User profile, edit details, view past sessions |

### 4-Step Analysis Flow (`/app`)

1. **Upload** — `FileUpload.tsx` — drag-and-drop genome file
2. **Analyzing** — loading spinner while backend processes file
3. **Questionnaire** — `Questionnaire.tsx` — lifestyle form
4. **Results** — `RecommendationsReport.tsx` + `NutrientRadarChart.tsx` + `MealPlanGenerator.tsx`

### API Client (`lib/api.ts`)

Axios instance with:
- Base URL from `NEXT_PUBLIC_API_URL` env var (default `http://localhost:5000`)
- Automatic JWT injection from `localStorage` for protected requests

---

## API Reference

### Auth Endpoints (`/api/auth`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/register` | No | Create account, send verification email |
| POST | `/verify` | No | Verify email with 6-digit code |
| POST | `/resend-code` | No | Resend verification code |
| POST | `/login` | No | Login, returns JWT |
| GET | `/me` | JWT | Get current user profile |
| PUT | `/update-profile` | JWT | Update name/age/sex |
| POST | `/reset-password-request` | No | Send password reset code |
| POST | `/reset-password-confirm` | No | Reset password with code |
| GET | `/my-reports` | JWT | List all analysis sessions |

### Analysis Endpoints (`/api`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/upload` | Optional | Upload genome file |
| POST | `/analyze` | No | Analyze uploaded file |
| GET | `/questionnaire/template` | No | Get questionnaire schema |
| POST | `/questionnaire` | No | Submit questionnaire answers |
| GET | `/recommendations/<id>` | No | Get recommendations |
| GET | `/session/<id>` | No | Check session status |
| DELETE | `/session/<id>` | No | Delete all session data (GDPR) |
| POST | `/generate-meal-plan` | No | Generate AI meal plan |
| GET | `/snps` | No | List all 25 analyzed SNPs |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# Flask
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here   # Used for JWT signing — keep secret!

# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=nutrigenomics

# Encryption — CRITICAL: back this up, losing it makes DB data unrecoverable
ENCRYPTION_KEY=your-fernet-key-here   # Generate: python app/encryption.py

# Groq (AI meal planner)
GROQ_API_KEY=your-groq-api-key-here

# SMTP (email verification)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password        # Use Gmail App Password, not account password
```

---

## Setup & Running Locally

### Backend

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and fill environment variables
cp .env.example .env

# 4. Generate encryption key (copy output into .env ENCRYPTION_KEY)
python app/encryption.py

# 5. Start MongoDB (must be running locally or provide MONGODB_URI)

# 6. Run Flask server
python run.py
# API available at http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local  # Set NEXT_PUBLIC_API_URL=http://localhost:5000
npm run dev
# Frontend available at http://localhost:3000
```

---

## What Is Missing / Should Be Implemented

### High Priority (Blockers for Production)

| Feature | Status | Notes |
|---|---|---|
| Rate limiting on auth endpoints | Missing | Brute-force attacks on login/register are possible |
| Session ownership validation | Missing | Any user can access any session by guessing a UUID |
| HTTPS enforcement | Missing | All traffic currently plain HTTP |
| Security headers (CSP, HSTS, X-Frame-Options) | Missing | No HTTP security headers set |
| Encryption key backup & rotation mechanism | Missing | Key loss = permanent data loss |
| Remove debug print statements from auth | Present | Login failures print the user's email to server logs |
| Remove `debug_code` from production API responses | Present | Verification codes exposed in API responses when SMTP fails |

### Medium Priority (UX & Completeness)

| Feature | Status | Notes |
|---|---|---|
| Frontend password reset UI | Missing | API is implemented, no UI exists |
| PDF export of recommendations report | Missing | Print button exists but no proper print stylesheet |
| Meal plan caching in DB | Missing | Each request re-generates a new meal plan via API |
| User profile edit functionality | Incomplete | Profile page exists but edit is minimal |
| Past session history with full report | Incomplete | Sessions are listed in `/my-reports` but not viewable in full |
| CSRF protection | Missing | No CSRF tokens on state-changing requests |
| File upload progress indicator | Missing | Large files show no progress |

### Lower Priority (Polish & Scalability)

| Feature | Status | Notes |
|---|---|---|
| Support for raw VCF files | Missing | Only 23andMe/AncestryDNA tab-separated format supported |
| Extended SNP database (>25 SNPs) | Missing | SNPs are hardcoded — no admin interface to add more |
| Admin dashboard | Missing | No way to view users, sessions, or system health |
| Audit logging | Missing | No record of who accessed what data |
| Automatic session cleanup | Missing | Old sessions accumulate indefinitely in DB |
| Two-factor authentication | Missing | Only email verification at registration |
| Offline / PWA support | Missing | Requires active backend connection |
| Pagination for API responses | Missing | `/my-reports` returns all sessions at once |
| Input sanitization | Incomplete | Some endpoints lack sanitization beyond type checks |
| Genetic interaction modeling | Missing | Recommendations treat SNPs independently — no interaction effects |
| Questionnaire follow-up logic | Missing | No branching questions based on previous answers |

---

## Architecture Decisions & Notes

- **Why MongoDB?** Flexible schema for varied genetic findings; supports nested documents naturally; TTL indexes handle code expiry automatically
- **Why Fernet for encryption?** Simple, authenticated encryption with no configuration footguns; suitable for at-rest data encryption
- **Why Groq?** Fast inference for LLaMA models with a free tier; suitable for structured JSON generation
- **Why snps library?** Handles multiple genome file formats (23andMe v3/v4/v5, AncestryDNA) and reference build normalization automatically
- **File deletion policy:** Genome files are deleted from disk immediately after analysis — the DB stores only structured, encrypted findings. This is by design for GDPR compliance and privacy.

---

*This is for educational and informational purposes only. Genetic risk information does not constitute medical advice. Always consult a qualified healthcare professional before making dietary or health decisions.*
