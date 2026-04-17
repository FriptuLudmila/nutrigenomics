# GenyO — Project Structure

GenyO is a full-stack web application that analyses raw genetic data files and generates personalised nutrition recommendations, supplement advice, and AI-powered meal plans based on a user's genome and lifestyle.

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
│   ├── models.py           # Data models (User, Session, GeneticResults, Recommendations)
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
│   │   └── reset-password/ # Password reset page
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

## Backend Overview

The backend is a Flask REST API structured around five concerns:

- **Authentication** (`auth.py`, `auth_routes.py`) — handles user registration, login, email verification via one-time codes, and JWT issuance.
- **Genetic Analysis** (`genetic_parser.py`) — parses uploaded 23andMe or AncestryDNA files and evaluates 25 SNPs across five categories: vitamins and minerals, macronutrient metabolism, digestive tolerance, caffeine and alcohol metabolism, and antioxidant capacity.
- **Recommendations** (`routes.py`) — cross-references genetic results with the user's lifestyle questionnaire to produce ranked, personalised nutrition and supplement advice.
- **AI Meal Planning** (`ai_meal_planner.py`) — sends a structured prompt to the Groq API (LLaMA 3.3 70B) and returns a 1–7 day meal plan tailored to the user's genetic profile.
- **Security** (`encryption.py`, `file_encryption.py`) — encrypts sensitive database fields and genome files at rest; uploaded files are securely deleted after analysis.

---

## Frontend Overview

The frontend is a Next.js 15 application using the App Router. The main user journey is implemented as a four-step flow on a single protected page:

1. Upload a genome file
2. Complete the lifestyle questionnaire
3. View personalised recommendations
4. Generate an AI meal plan (optional)

Authentication state is managed via JWT tokens stored in `localStorage`. All API calls are made through a typed Axios client (`lib/api.ts`) that injects the token automatically.

---

## Database Structure

MongoDB is used with six collections:

| Collection | Contents |
|---|---|
| `users` | Account details (email, name, bcrypt password hash, verified flag) |
| `sessions` | Analysis workflow state and timestamps |
| `genetic_results` | 25 analysed SNPs per session (sensitive fields encrypted) |
| `questionnaires` | User lifestyle answers (activity, diet, allergies, goals) |
| `recommendations` | Generated advice ranked by priority |
| `verification_codes` | 6-digit OTPs for email verification (auto-expire after 15 minutes) |

---

## Infrastructure and Deployment

The application is containerised with Docker and orchestrated via Docker Compose, running three services: MongoDB, the Flask backend, and the Next.js frontend. In production, a Jenkins CI/CD pipeline builds and pushes Docker images, then deploys them behind a Traefik reverse proxy with automatic HTTPS via Let's Encrypt.

---

## End-to-End User Flow

1. Register and verify email via OTP
2. Log in and receive a JWT token
3. Upload a genome file (23andMe or AncestryDNA format)
4. Complete the lifestyle questionnaire
5. Receive personalised recommendations
6. Optionally generate an AI-powered meal plan
7. View or delete past sessions from the profile page
