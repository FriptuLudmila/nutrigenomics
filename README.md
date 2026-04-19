# GenyO — Project Structure

GenyO is a full-stack web application that analyses raw genetic data files and generates personalised nutrition recommendations, supplement advice, and AI-powered meal plans based on a user's genome and lifestyle questionnaire.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 (TypeScript, Tailwind CSS) |
| Backend | Flask (Python) |
| Database | MongoDB |
| AI | Groq API (LLaMA 3.3 70B) |
| Infrastructure | Docker, Docker Compose, Jenkins, Traefik |

---

## Directory Structure

```
nutrigenomics/
├── app/                    # Flask REST API (backend)
│   ├── __init__.py         # App factory, security headers, CORS, blueprint registration
│   ├── config.py           # Environment-based configuration (dev/prod)
│   ├── database.py         # MongoDB connection and helper functions
│   ├── models.py           # Data models and all database operations
│   ├── routes.py           # Core API endpoints (upload, analyse, recommendations, meal plans)
│   ├── auth.py             # Authentication logic (bcrypt, JWT, email verification)
│   ├── auth_routes.py      # Authentication endpoints (register, login, password reset)
│   ├── genetic_parser.py   # SNP parsing engine — analyses 25 nutrigenomics-relevant SNPs
│   ├── encryption.py       # Field-level database encryption (Fernet/AES-128)
│   ├── file_encryption.py  # Genome file encryption and secure deletion
│   ├── ai_meal_planner.py  # Groq API integration for LLM-powered meal plan generation
│   └── limiter.py          # Rate limiting configuration
│
├── frontend/               # Next.js frontend
│   ├── app/                # App Router pages
│   │   ├── landing/        # Public landing page
│   │   ├── app/            # Protected analysis dashboard (4-step flow)
│   │   ├── app/profile/    # User profile and session history
│   │   ├── how-it-works/   # Informational page
│   │   └── reset-password/ # Password reset page (token-based)
│   │
│   ├── components/         # Reusable UI components
│   │   ├── AuthModal.tsx           # Register/login modal with OTP verification
│   │   ├── FileUpload.tsx          # Drag-and-drop genome file upload
│   │   ├── Questionnaire.tsx       # Lifestyle questionnaire form
│   │   ├── RecommendationsReport.tsx # Recommendations display
│   │   ├── MealPlanGenerator.tsx   # AI meal plan interface
│   │   └── NutrientRadarChart.tsx  # Radar chart for nutrient risk scores
│   │
│   └── lib/
│       └── api.ts          # Typed Axios client with automatic JWT injection
│
├── docs/                   # Architecture guides and security documentation
├── uploads/                # Temporary encrypted genome file storage
│
├── Dockerfile              # Backend Docker image (Python 3.11)
├── docker-compose.yml      # Multi-container setup (MongoDB + Backend + Frontend)
├── Jenkinsfile             # CI/CD pipeline (build, push, deploy)
├── run.py                  # Flask development server entry point
└── requirements.txt        # Python dependencies
```

---

## Backend

The backend is a Flask REST API. The five core concerns are described below.

### 1. Authentication (`auth.py`, `auth_routes.py`)

Handles the full user identity lifecycle:

- **Registration** — validates input, stores an unverified user, sends a 6-digit OTP via SMTP, and waits for verification before activating the account.
- **Email verification** — confirms the OTP and issues a JWT token (HS256, 7-day expiry).
- **Login** — verifies bcrypt password hash, rejects unverified accounts, issues a new JWT.
- **Password reset** — generates a `secrets.token_urlsafe(32)` reset token, emails a signed link, and confirms the new password on submission.
- **Route protection** — the `require_auth` decorator validates the JWT on every protected endpoint and injects `request.user_id` and `request.user_email` into the request context.

### 2. Genetic Analysis (`genetic_parser.py`, `routes.py`)

Parses uploaded 23andMe or AncestryDNA files and evaluates **25 SNPs** across five categories:

| Category | SNPs |
|---|---|
| Digestive & Food Tolerance | Lactose (rs4988235), Celiac (rs2187668), Bitter taste (rs1726866), Fat taste (rs1761667) |
| Caffeine & Alcohol | CYP1A2 (rs762551), ALDH2 flush (rs671), ADH1B (rs1229984) |
| Vitamins & Minerals | MTHFR C677T (rs1801133), MTHFR A1298C (rs1801131), B12 absorption (rs602662), B12 utilisation (rs1801394), Vitamin D receptor (rs2228570), Vitamin D transport (rs7041), Vitamin C (rs33972313), Vitamin A/beta-carotene (rs7501331), Iron (rs1799945), Choline (rs7946) |
| Macronutrient Metabolism | Omega-3 (rs174546), Saturated fat (rs5082), APOE fat metabolism (rs7412), Carb/diabetes risk (rs7903146), Obesity/FTO (rs9939609), Exercise response (rs4341) |
| Antioxidant & Detox | SOD2 (rs4880), Glutathione (rs1695) |

Each SNP is scored as `high` (100), `moderate` (60), `low` (20), or `protective` (10). These scores feed the nutrient radar chart.

Sensitive fields (`genotype`, `interpretation`, `recommendation`) are encrypted with Fernet before being written to the database.

### 3. Recommendations Engine (`routes.py`)

Generates ranked, personalised advice by cross-referencing genetic findings with lifestyle questionnaire answers. Key design constraints:

- **Questionnaire is required.** Recommendations cannot be generated until the questionnaire has been submitted. The endpoint returns `400` if the session has no questionnaire data, preventing recommendations from being produced without lifestyle context.
- **Cache invalidation.** If the questionnaire is resubmitted, any previously cached recommendations are deleted and a session flag is reset, ensuring the next request regenerates them with the latest answers.
- **Personalisation logic.** For each finding the engine checks questionnaire fields — diet type, activity level, caffeine intake, alcohol frequency, supplements, digestive issues, health goals, and allergies — and appends a `personalized_note` when the combination is clinically relevant (e.g. APOE e2/e2 + high-carb diet, MTHFR + folic acid supplement, omega-3 risk + vegan diet).

Output is grouped into: `high_priority`, `moderate_priority`, `general_advice`, `foods_to_increase`, `foods_to_limit`, and `supplements_to_consider`.

### 4. AI Meal Planning (`ai_meal_planner.py`)

Sends a structured prompt to the Groq API (LLaMA 3.3 70B) containing the genetic summary, ranked recommendations, and questionnaire answers. Returns a 1–7 day meal plan with per-meal genetic rationale. The meal plan endpoint always uses the current recommendations, which are guaranteed to be questionnaire-aware (see above).

### 5. Security (`encryption.py`, `file_encryption.py`)

- Uploaded genome files are encrypted with Fernet immediately after saving and the plaintext is deleted. During analysis the file is decrypted to a temporary path in memory, parsed, and the temporary file is securely deleted (3-pass overwrite) in a `finally` block.
- Sensitive database fields are encrypted before storage and decrypted only at the point of use.
- Passwords use bcrypt (12 rounds). JWT tokens expire after 7 days.
- Security headers (HSTS, X-Content-Type-Options, Referrer-Policy) are applied via Flask-Talisman in production.

---

## Frontend

The frontend is a Next.js 15 application using the App Router. All authenticated routes are JWT-gated — the token is stored in `localStorage` and injected automatically by the Axios client in `lib/api.ts`.

### Pages

| Route | Purpose |
|---|---|
| `/landing` | Public landing page with login and register entry points |
| `/app` | Protected four-step analysis dashboard |
| `/app/profile` | User profile editor and past session history |
| `/how-it-works` | Informational page explaining the analysis process |
| `/reset-password` | Token-based password reset form |

### Four-Step Analysis Flow (`/app`)

The main dashboard enforces a strict left-to-right progression:

1. **Upload** — drag-and-drop a 23andMe or AncestryDNA file (`.txt`, `.csv`, or `.zip`). The backend validates file content, encrypts it, and returns a `session_id`.
2. **Questionnaire** — collects activity level, diet type, caffeine and alcohol intake, digestive issues, health goals, supplements, and allergies. Submitting this step invalidates any stale cached recommendations on the backend.
3. **Recommendations** — displays the ranked findings grouped by priority, foods to increase or limit, and supplements to consider, alongside a radar chart of nutrient risk scores.
4. **Meal Plan** — optionally generates a 1–7 day AI meal plan tailored to the user's genetic and lifestyle profile.

### Components

| Component | Purpose |
|---|---|
| `AuthModal.tsx` | Multi-step register/login modal — handles OTP entry and email verification inline |
| `FileUpload.tsx` | Drag-and-drop file input with client-side type validation |
| `Questionnaire.tsx` | Structured lifestyle form matching the backend's questionnaire template |
| `RecommendationsReport.tsx` | Full recommendations display with priority grouping and category labels |
| `MealPlanGenerator.tsx` | Day selector and AI meal plan renderer |
| `NutrientRadarChart.tsx` | Recharts radar visualisation of per-category nutrient risk scores |

---

## Database Structure

MongoDB is used with six collections:

| Collection | Contents |
|---|---|
| `users` | Account details (email, name, bcrypt password hash, verified flag) |
| `sessions` | Workflow state — status, boolean flags for each completed step, timestamps |
| `genetic_results` | 25 analysed SNPs per session with sensitive fields encrypted |
| `questionnaires` | Lifestyle answers; resubmission triggers recommendation cache invalidation |
| `recommendations` | Generated advice; deleted and regenerated whenever questionnaire data changes |
| `verification_codes` | 6-digit OTPs — auto-expire after 15 minutes via MongoDB TTL index |

### Enforced Step Order

The API enforces the following sequence. Earlier steps cannot be skipped:

```
upload → analyze → questionnaire → recommendations → meal plan
```

Each step checks the session's boolean flags (`has_genetic_results`, `has_questionnaire`, `has_recommendations`) before proceeding.

---

## Infrastructure and Deployment

The application runs as three Docker containers orchestrated by Docker Compose: MongoDB, the Flask backend (Gunicorn, port 5000), and the Next.js frontend. In production a Jenkins CI/CD pipeline builds and pushes Docker images, then deploys them behind a Traefik reverse proxy with automatic HTTPS via Let's Encrypt.

Environment variables required: `SECRET_KEY`, `ENCRYPTION_KEY`, `GROQ_API_KEY`, `SMTP_SERVER`, `SMTP_PORT`, `SMTP_EMAIL`, `SMTP_PASSWORD`, `FRONTEND_URL`, `MONGODB_URI`.
