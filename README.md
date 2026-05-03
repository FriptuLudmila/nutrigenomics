# GenyO — Personalised Nutrigenomics Platform

GenyO is a full-stack web application that analyses raw genetic data files (23andMe, AncestryDNA) and generates personalised nutrition recommendations, supplement advice, and AI-powered meal plans based on a user's genome and lifestyle questionnaire.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 (TypeScript, Tailwind CSS) |
| Backend | Flask 3.1 (Python) |
| Database | MongoDB |
| AI | Groq API (LLaMA 3.3 70B) |
| Infrastructure | Docker, Docker Compose, Jenkins, Traefik |

---

## Directory Structure

```
nutrigenomics/
├── app/                    # Flask REST API (backend)
│   ├── __init__.py         # App factory, CORS, Talisman security headers, blueprint registration
│   ├── config.py           # Environment-based configuration (dev/prod)
│   ├── database.py         # MongoDB connection, index creation, health checks
│   ├── models.py           # Dataclass models (Session, GeneticResults, Questionnaire, Recommendations)
│   ���── routes.py           # Core API endpoints (upload+analyse, recommendations, meal plans)
│   ├── auth.py             # JWT generation/validation, bcrypt hashing, cookie helpers, email sending
│   ├── auth_routes.py      # Auth endpoints (register, verify, login, logout, password reset)
│   ├── genetic_parser.py   # SNP parsing engine — analyses 25 nutrigenomics-relevant variants
│   ├── encryption.py       # Field-level Fernet encryption for sensitive database fields
│   ├── file_encryption.py  # Legacy file encryption utilities (no longer used in main flow)
│   ├── ai_meal_planner.py  # Groq API integration for LLM-powered meal plan generation
│   └── limiter.py          # Flask-Limiter rate limiting configuration
│
├── frontend/               # Next.js frontend
│   ├── app/                # App Router pages
│   │   ├── page.tsx        # Root redirect to /landing
│   │   ├── landing/        # Public landing page with auth modal
│   │   ├── app/            # Protected analysis dashboard (upload → questionnaire → results)
│   │   ├── app/profile/    # User profile editor and past report history
│   │   ├── how-it-works/   # Informational page
│   │   ├── privacy/        # Privacy policy page
│   │   └── reset-password/ # Token-based password reset form
│   │
│   ├── components/         # Reusable UI components
│   │   ├── AuthModal.tsx           # Multi-step register/login modal with OTP verification
│   │   ├── FileUpload.tsx          # Drag-and-drop genome file upload
│   │   ├── Questionnaire.tsx       # Lifestyle questionnaire form
│   │   ├── RecommendationsReport.tsx # Recommendations display with priority grouping
│   │   ├── MealPlanGenerator.tsx   # AI meal plan interface with day selector
│   │   ��── NutrientRadarChart.tsx  # Recharts radar chart for nutrient risk scores
│   │
│   └── lib/
│       └── api.ts          # Typed Axios client with cookie-based auth (withCredentials)
│
├── Dockerfile              # Backend Docker image (Python 3.11)
├── docker-compose.yml      # Multi-container setup (MongoDB + Backend + Frontend)
├── Jenkinsfile             # CI/CD pipeline (build, push, deploy)
├── run.py                  # Flask development server entry point
├── test_api.py             # Manual API test script
└── requirements.txt        # Python dependencies
```

---

## Backend

The backend is a Flask REST API. The core concerns are described below.

### 1. Authentication (`auth.py`, `auth_routes.py`)

Handles the full user identity lifecycle:

- **Registration** (`POST /api/auth/register`) — validates input (name, age, sex, email, password), enforces password complexity (min 10 chars, uppercase, digit, symbol), stores an unverified user with a bcrypt-hashed password, sends a 6-digit OTP via SMTP, and waits for email verification before activating the account.
- **Email verification** (`POST /api/auth/verify`) — confirms the OTP (15-minute expiry), marks the user as verified, and sets an HTTP-only JWT cookie.
- **Login** (`POST /api/auth/login`) — verifies the bcrypt password hash, rejects unverified accounts, and sets an HTTP-only JWT cookie. Accepts a `remember_me` flag to control cookie lifetime (24 hours vs browser session).
- **Logout** (`POST /api/auth/logout`) — clears the auth cookie.
- **Password reset** (`POST /api/auth/reset-password-request`, `POST /api/auth/reset-password-confirm`) — generates a `secrets.token_urlsafe(32)` reset token (30-minute expiry), emails a signed link, and confirms the new password on submission.
- **Route protection** — the `@require_auth` decorator reads the JWT from the `auth_token` HTTP-only cookie, validates it, and injects `request.user_id` and `request.user_email` into the request context.

#### JWT Cookie Security

The JWT is stored as an HTTP-only cookie rather than in localStorage to prevent theft via XSS attacks:

| Attribute | Value | Purpose |
|---|---|---|
| `HttpOnly` | `true` | JavaScript cannot read the cookie |
| `SameSite` | `Lax` | Blocks cross-site POST/PUT/DELETE requests (CSRF protection) |
| `Secure` | `true` in production | Cookie only sent over HTTPS |
| `Max-Age` | 24 hours (remember me) or session | Controls persistence |
| `Path` | `/` | Sent with all requests to the backend |

### 2. Genetic Analysis (`genetic_parser.py`, `routes.py`)

The upload and analysis happen in a single request (`POST /api/upload`). The raw genetic file is read into memory, parsed directly from bytes by the `GeneticParser`, and the raw data is discarded immediately after parsing. The file never touches disk or the database — only the encrypted analysis results are persisted to MongoDB.

The parser evaluates **25 SNPs** across five categories:

| Category | SNPs |
|---|---|
| Digestive & Food Tolerance | Lactose (rs4988235), Celiac (rs2187668), Bitter taste (rs1726866), Fat taste (rs1761667) |
| Caffeine & Alcohol | CYP1A2 (rs762551), ALDH2 flush (rs671), ADH1B (rs1229984) |
| Vitamins & Minerals | MTHFR C677T (rs1801133), MTHFR A1298C (rs1801131), B12 absorption (rs602662), B12 utilisation (rs1801394), Vitamin D receptor (rs2228570), Vitamin D transport (rs7041), Vitamin C (rs33972313), Vitamin A/beta-carotene (rs7501331), Iron (rs1799945), Choline (rs7946) |
| Macronutrient Metabolism | Omega-3 (rs174546), Saturated fat (rs5082), APOE fat metabolism (rs7412), Carb/diabetes risk (rs7903146), Obesity/FTO (rs9939609), Exercise response (rs4341) |
| Antioxidant & Detox | SOD2 (rs4880), Glutathione (rs1695) |

Each SNP is scored as `high` (100), `moderate` (60), `low` (20), or `protective` (10). These scores feed the nutrient radar chart on the frontend.

Sensitive finding fields (`genotype`, `interpretation`, `recommendation`) are encrypted with Fernet (AES-128-CBC) before being written to MongoDB. Non-sensitive fields (`rsid`, `gene`, `condition`, `risk_level`) are stored in plaintext for querying and display.

### 3. Recommendations Engine (`routes.py`)

Generates ranked, personalised advice by cross-referencing genetic findings with lifestyle questionnaire answers (`POST /api/questionnaire`, `GET /api/recommendations/<session_id>`). Key design constraints:

- **Questionnaire is required.** Recommendations cannot be generated until the questionnaire has been submitted. The endpoint returns `400` if the session has no questionnaire data.
- **Cache invalidation.** If the questionnaire is resubmitted, any previously cached recommendations are deleted, ensuring the next request regenerates them with the latest answers.
- **Personalisation logic.** For each finding the engine checks questionnaire fields — diet type, activity level, caffeine intake, alcohol frequency, supplements, digestive issues, health goals, and allergies — and appends a `personalized_note` when the combination is clinically relevant (e.g. APOE e2/e2 + high-carb diet, MTHFR + folic acid supplement, omega-3 risk + vegan diet).

Output is grouped into: `high_priority`, `moderate_priority`, `general_advice`, `foods_to_increase`, `foods_to_limit`, and `supplements_to_consider`.

### 4. AI Meal Planning (`ai_meal_planner.py`)

Sends a structured prompt to the Groq API (LLaMA 3.3 70B) containing the genetic summary, ranked recommendations, and questionnaire answers (`POST /api/generate-meal-plan`). Returns a 1-7 day meal plan with per-meal macros and genetic rationale. The meal plan endpoint uses the current recommendations, which are guaranteed to be questionnaire-aware.

### 5. Security

- **In-memory file processing** — uploaded genetic files are parsed entirely in memory and immediately discarded. The raw file is never written to disk or stored in the database.
- **Field-level encryption** — sensitive genetic finding fields (genotype, interpretation, recommendation) are encrypted with Fernet (AES-128-CBC) before storage in MongoDB and decrypted only at the point of use.
- **Password hashing** — bcrypt with automatic salting.
- **JWT in HTTP-only cookies** — prevents token theft via XSS. `SameSite=Lax` provides CSRF protection.
- **Token expiry** — JWT tokens expire after 24 hours.
- **Rate limiting** — all endpoints are rate-limited via Flask-Limiter (e.g. 20 uploads/hour, 5 registrations/hour, 10 logins/minute).
- **Security headers** — HSTS, X-Content-Type-Options, and strict Referrer-Policy are applied via Flask-Talisman in production.
- **CORS** — restricted to the configured frontend origin with `supports_credentials=True` for cookie transport.
- **GDPR compliance** — `DELETE /api/session/<session_id>` permanently removes all data for a session from MongoDB.

---

## Frontend

The frontend is a Next.js 15 application using the App Router with TypeScript and Tailwind CSS. Authentication is handled via HTTP-only cookies — the frontend stores only a `logged_in` flag in localStorage as a UI hint, while actual authentication is validated server-side on every API call. The Axios client in `lib/api.ts` is configured with `withCredentials: true` to send cookies with all cross-origin requests.

### Pages

| Route | Purpose |
|---|---|
| `/landing` | Public landing page with feature overview, login and register entry points |
| `/app` | Protected three-step analysis dashboard (upload, questionnaire, results) |
| `/app/profile` | User profile editor and past report history with view/delete actions |
| `/how-it-works` | Informational page explaining the analysis process |
| `/privacy` | Privacy policy page |
| `/reset-password` | Token-based password reset form (accessed via email link) |

### Analysis Flow (`/app`)

The main dashboard enforces a left-to-right progression:

1. **Upload & Analyse** — drag-and-drop a 23andMe or AncestryDNA file (`.txt`, `.csv`, or `.zip`). The file is uploaded and analysed in a single request — the backend parses the genetic data in memory and returns the analysis results immediately alongside the `session_id`. An "Analysing" spinner is shown during this request.
2. **Questionnaire** — collects age, sex, activity level, diet type, caffeine and alcohol intake, digestive issues, health goals, current supplements, and known allergies. Submitting this step invalidates any stale cached recommendations on the backend.
3. **Recommendations & Meal Plan** — displays the ranked findings grouped by priority, foods to increase or limit, and supplements to consider, alongside a radar chart of nutrient risk scores. An optional AI meal plan (1-7 days) can be generated from this view.

Session state is persisted in `sessionStorage` so the user can resume after a page refresh. If the session data is no longer available on the backend (e.g. after cookie expiry), the user is prompted to re-upload.

### Components

| Component | Purpose |
|---|---|
| `AuthModal.tsx` | Multi-step register/login modal with OTP entry, "remember me" toggle, and password reset link |
| `FileUpload.tsx` | Drag-and-drop file input with client-side extension validation |
| `Questionnaire.tsx` | Structured lifestyle form matching the backend's questionnaire template |
| `RecommendationsReport.tsx` | Full recommendations display with priority grouping and category labels |
| `MealPlanGenerator.tsx` | Day selector and AI meal plan renderer with per-meal macros |
| `NutrientRadarChart.tsx` | Recharts radar visualisation of per-category nutrient risk scores |

---

## Database Structure

MongoDB is used with seven collections:

| Collection | Contents |
|---|---|
| `users` | Account details (email, name, age, sex, bcrypt password hash, verified flag, last login) |
| `sessions` | Workflow state — status, file metadata, boolean flags for each completed step, timestamps |
| `genetic_results` | 25 analysed SNPs per session with sensitive fields encrypted (Fernet) |
| `questionnaires` | Lifestyle answers; resubmission triggers recommendation cache invalidation |
| `recommendations` | Generated advice with radar chart data; deleted and regenerated when questionnaire changes |
| `verification_codes` | 6-digit OTPs with 15-minute expiry |
| `reset_tokens` | Password reset tokens with 30-minute expiry |

### Enforced Step Order

The API enforces the following sequence. Earlier steps cannot be skipped:

```
upload+analyse → questionnaire → recommendations → meal plan
```

Each step checks the session's boolean flags (`has_genetic_results`, `has_questionnaire`, `has_recommendations`) before proceeding.

---

## API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Auth | Rate Limit | Purpose |
|---|---|---|---|---|
| POST | `/register` | No | 5/hour | Create account and send OTP |
| POST | `/verify` | No | 10/hour | Verify email with OTP, sets auth cookie |
| POST | `/login` | No | 10/min | Authenticate, sets auth cookie |
| POST | `/logout` | No | - | Clear auth cookie |
| POST | `/resend-code` | No | 3/hour | Resend verification OTP |
| POST | `/reset-password-request` | No | 5/hour | Send password reset email |
| POST | `/reset-password-confirm` | No | 10/hour | Reset password with token |
| GET | `/me` | Yes | - | Get current user profile |
| PUT | `/update-profile` | Yes | - | Update name, age, sex |
| GET | `/my-reports` | Yes | - | List all analysis reports |

### Core (`/api`)

| Method | Endpoint | Auth | Rate Limit | Purpose |
|---|---|---|---|---|
| POST | `/upload` | Yes | 20/hour | Upload and analyse genetic file (in-memory) |
| POST | `/analyze` | Yes | 20/hour | Retrieve cached analysis results |
| POST | `/questionnaire` | Yes | 20/hour | Submit lifestyle questionnaire |
| GET | `/recommendations/<id>` | Yes | 20/hour | Get personalised recommendations |
| POST | `/generate-meal-plan` | Yes | 10/hour | Generate AI meal plan |
| DELETE | `/session/<id>` | Yes | - | Delete all session data (GDPR) |
| GET | `/questionnaire/template` | No | - | Get questionnaire structure |
| GET | `/snps` | No | - | List analysed SNP variants |

---

## Infrastructure and Deployment

The application runs as three Docker containers orchestrated by Docker Compose: MongoDB, the Flask backend (Gunicorn, port 5000), and the Next.js frontend (port 3000). In production a Jenkins CI/CD pipeline builds and pushes Docker images, then deploys them behind a Traefik reverse proxy with automatic HTTPS via Let's Encrypt.

### Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `SECRET_KEY` | Yes | JWT signing key |
| `ENCRYPTION_KEY` | Yes | Fernet key for field-level encryption |
| `GROQ_API_KEY` | Yes | Groq API key for AI meal plans |
| `MONGODB_URI` | No | MongoDB connection string (default: `mongodb://localhost:27017/`) |
| `MONGODB_DB` | No | Database name (default: `nutrigenomics`) |
| `FRONTEND_URL` | No | CORS origin (default: `http://localhost:3000`) |
| `SMTP_SERVER` | No | Email server (default: `smtp.gmail.com`) |
| `SMTP_PORT` | No | Email port (default: `587`) |
| `SMTP_EMAIL` | Yes | Sender email address |
| `SMTP_PASSWORD` | Yes | Sender email app password |

### Local Development

```bash
# Backend
pip install -r requirements.txt
python run.py

# Frontend
cd frontend
npm install
npm run dev
```

The backend runs on `http://localhost:5000` and the frontend on `http://localhost:3000`.
