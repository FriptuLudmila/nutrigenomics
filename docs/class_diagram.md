# Nutrigenomics Analysis - Class Diagram

## Overview
This document describes the class structure of the Nutrigenomics Analysis application, showing relationships between backend models, services, and frontend components.

---

## Backend Architecture (Python/Flask)

### Data Models Layer (`app/models.py`)

```
┌─────────────────────────────────────────────────────────────────┐
│                          User                                    │
├─────────────────────────────────────────────────────────────────┤
│ - user_id: str                                                   │
│ - email: str                                                     │
│ - password_hash: str                                             │
│ - name: str                                                      │
│ - created_at: datetime                                           │
│ - last_login: Optional[datetime]                                 │
├─────────────────────────────────────────────────────────────────┤
│ + to_dict(): Dict                                                │
│ + from_dict(data: Dict): User                                    │
│ + to_safe_dict(): Dict                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Session                                  │
├─────────────────────────────────────────────────────────────────┤
│ - session_id: str (UUID)                                         │
│ - user_id: str (FK → User)                                       │
│ - filepath: str                                                  │
│ - original_filename: str                                         │
│ - status: str                                                    │
│ - created_at: datetime                                           │
│ - updated_at: datetime                                           │
│ - file_size_bytes: int                                           │
│ - has_genetic_results: bool                                      │
│ - has_questionnaire: bool                                        │
│ - has_recommendations: bool                                      │
├─────────────────────────────────────────────────────────────────┤
│ + create_new(filepath, filename, file_size): Session             │
│ + to_dict(): Dict                                                │
│ + from_dict(data: Dict): Session                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    GeneticResults                                │
├─────────────────────────────────────────────────────────────────┤
│ - session_id: str (FK → Session)                                 │
│ - source: str                                                    │
│ - snp_count: int                                                 │
│ - build: int                                                     │
│ - findings_encrypted: List[Dict]                                 │
│ - summary: Dict                                                  │
│ - analyzed_at: datetime                                          │
├─────────────────────────────────────────────────────────────────┤
│ + create(session_id, file_info, encrypted, summary): Results    │
│ + to_dict(): Dict                                                │
│ + from_dict(data: Dict): GeneticResults                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Questionnaire                                │
├─────────────────────────────────────────────────────────────────┤
│ - session_id: str (FK → Session)                                 │
│ - answers: Dict[str, Any]                                        │
│ - submitted_at: datetime                                         │
│ - age: Optional[int]                                             │
│ - sex: Optional[str]                                             │
│ - activity_level: Optional[str]                                  │
│ - diet_type: Optional[str]                                       │
│ - alcohol_frequency: Optional[str]                               │
│ - caffeine_cups_per_day: Optional[int]                           │
│ - digestive_issues: Optional[List[str]]                          │
│ - health_goals: Optional[List[str]]                              │
│ - current_supplements: Optional[List[str]]                       │
│ - known_allergies: Optional[List[str]]                           │
├─────────────────────────────────────────────────────────────────┤
│ + create(session_id, answers): Questionnaire                     │
│ + to_dict(): Dict                                                │
│ + from_dict(data: Dict): Questionnaire                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Recommendations                               │
├─────────────────────────────────────────────────────────────────┤
│ - session_id: str (FK → Session)                                 │
│ - recommendations: Dict[str, Any]                                │
│ - generated_at: datetime                                         │
├─────────────────────────────────────────────────────────────────┤
│ + create(session_id, recommendations): Recommendations           │
│ + to_dict(): Dict                                                │
│ + from_dict(data: Dict): Recommendations                         │
└─────────────────────────────────────────────────────────────────┘
```

### Genetic Analysis Layer (`app/genetic_parser.py`)

```
┌─────────────────────────────────────────────────────────────────┐
│                      RiskLevel (Enum)                            │
├─────────────────────────────────────────────────────────────────┤
│ LOW = "low"                                                      │
│ MODERATE = "moderate"                                            │
│ HIGH = "high"                                                    │
│ PROTECTIVE = "protective"                                        │
├─────────────────────────────────────────────────────────────────┤
│ + to_score(): int                                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    GeneticVariant                                │
├─────────────────────────────────────────────────────────────────┤
│ - rsid: str                                                      │
│ - gene: str                                                      │
│ - condition: str                                                 │
│ - genotype: Optional[str]                                        │
│ - risk_level: RiskLevel                                          │
│ - interpretation: str                                            │
│ - dietary_recommendation: str                                    │
│ - scientific_source: str                                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    GeneticParser                                 │
├─────────────────────────────────────────────────────────────────┤
│ - filepath: str                                                  │
│ - snps_object: SNPs                                              │
│ - snp_count: int                                                 │
│ - results: List[GeneticVariant]                                  │
│ - NUTRIGENOMICS_SNPS: Dict (25 SNP definitions)                  │
├─────────────────────────────────────────────────────────────────┤
│ + __init__(filepath: str)                                        │
│ + analyze_all(): List[GeneticVariant]                            │
│ + analyze_snp(rsid: str): Optional[GeneticVariant]               │
│ + get_file_info(): Dict                                          │
│ + export_to_dict(): Dict                                         │
│ + get_nutrient_radar_data(): List[Dict]                          │
└─────────────────────────────────────────────────────────────────┘
```

### Security & Encryption Layer (`app/encryption.py`, `app/auth.py`)

```
┌─────────────────────────────────────────────────────────────────┐
│               GeneticDataEncryption                              │
├─────────────────────────────────────────────────────────────────┤
│ - key: bytes                                                     │
│ - cipher: Fernet                                                 │
├─────────────────────────────────────────────────────────────────┤
│ + __init__(key: Optional[str])                                   │
│ + encrypt_data(data: Union[str, Dict, list]): str                │
│ + decrypt_data(encrypted_data: str): Union[Dict, list, str]      │
│ + encrypt_genotype(genotype: str): str                           │
│ + decrypt_genotype(encrypted: str): str                          │
│ + generate_key(): str (static)                                   │
├─────────────────────────────────────────────────────────────────┤
│ Functions:                                                       │
│ + get_encryptor(): GeneticDataEncryption                         │
│ + encrypt_genetic_findings(findings: list): list                 │
│ + decrypt_genetic_findings(encrypted: list): list                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Authentication Module                          │
├─────────────────────────────────────────────────────────────────┤
│ Functions:                                                       │
│ + hash_password(password: str): str                              │
│ + verify_password(password: str, hash: str): bool                │
│ + generate_token(user_id: str, email: str): str                  │
│ + decode_token(token: str): Optional[Dict]                       │
│ + require_auth(f): decorator                                     │
│ + save_user(db, user: User): bool                                │
│ + get_user_by_email(db, email: str): Optional[User]              │
│ + get_user_by_id(db, user_id: str): Optional[User]               │
└─────────────────────────────────────────────────────────────────┘
```

### Database Layer (`app/database.py`)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Database                                  │
├─────────────────────────────────────────────────────────────────┤
│ - client: MongoClient                                            │
│ - db: MongoDatabase                                              │
│ - _connected: bool                                               │
├─────────────────────────────────────────────────────────────────┤
│ + connect(uri: str, db_name: str): bool                          │
│ + disconnect(): void                                             │
│ + is_connected: bool (property)                                  │
│ + sessions: Collection (property)                                │
│ + genetic_results: Collection (property)                         │
│ + questionnaires: Collection (property)                          │
│ + recommendations: Collection (property)                         │
│ + users: Collection (property)                                   │
│ - _create_indexes(): void                                        │
└─────────────────────────────────────────────────────────────────┘
```

### AI Services Layer (`app/ai_meal_planner.py`)

```
┌─────────────────────────────────────────────────────────────────┐
│                   AI Meal Planner Service                        │
├─────────────────────────────────────────────────────────────────┤
│ - client: Groq                                                   │
│ - GROQ_API_KEY: str                                              │
├─────────────────────────────────────────────────────────────────┤
│ + generate_meal_plan(genetic_summary, recommendations,           │
│                      questionnaire, days): Dict                  │
│ + get_fallback_meal_plan(days): Dict                             │
│ - _build_meal_plan_prompt(...): str                              │
└─────────────────────────────────────────────────────────────────┘
```

### API Routes Layer (`app/routes.py`)

```
┌─────────────────────────────────────────────────────────────────┐
│                      API Blueprint                               │
├─────────────────────────────────────────────────────────────────┤
│ Authentication Endpoints:                                        │
│ POST   /api/auth/register                                        │
│ POST   /api/auth/login                                           │
│ GET    /api/auth/me (protected)                                  │
│                                                                  │
│ Analysis Workflow Endpoints:                                     │
│ POST   /api/upload                                               │
│ POST   /api/analyze                                              │
│ POST   /api/questionnaire                                        │
│ GET    /api/recommendations/<session_id>                         │
│                                                                  │
│ AI & Utilities:                                                  │
│ POST   /api/generate-meal-plan                                   │
│ GET    /api/questionnaire/template                               │
│ GET    /api/session/<session_id>                                 │
│ DELETE /api/session/<session_id>                                 │
│ GET    /api/snps                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Helper Functions:                                                │
│ + allowed_file(filename): bool                                   │
│ + generate_personalized_recommendations(findings, quest): Dict   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture (Next.js/React/TypeScript)

### Page Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      LandingPage                                 │
│                  (app/landing/page.tsx)                          │
├─────────────────────────────────────────────────────────────────┤
│ State:                                                           │
│ - showAuthModal: bool                                            │
├─────────────────────────────────────────────────────────────────┤
│ Sections:                                                        │
│ - Navigation                                                     │
│ - Hero Section                                                   │
│ - Features Section (How It Works)                                │
│ - Benefits Section (What Makes You Unique)                       │
│ - Privacy Section                                                │
│ - CTA Section                                                    │
│ - Footer                                                         │
├─────────────────────────────────────────────────────────────────┤
│ Child Components:                                                │
│ - <AuthModal>                                                    │
│ - <FeatureCard>                                                  │
│ - <BenefitItem>                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     AnalysisPage                                 │
│                   (app/app/page.tsx)                             │
├─────────────────────────────────────────────────────────────────┤
│ State:                                                           │
│ - currentStep: number                                            │
│ - sessionId: string | null                                       │
│ - geneticResults: any | null                                     │
│ - questionnaireData: any | null                                  │
│ - recommendations: any | null                                    │
│ - radarData: any | null                                          │
│ - loading: bool                                                  │
│ - error: string                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                         │
│ + handleFileUpload(file: File): Promise<void>                    │
│ + handleAnalyze(): Promise<void>                                 │
│ + handleQuestionnaireSubmit(data: any): Promise<void>            │
│ + loadRecommendations(): Promise<void>                           │
├─────────────────────────────────────────────────────────────────┤
│ Child Components:                                                │
│ - <FileUpload>                                                   │
│ - <Questionnaire>                                                │
│ - <RecommendationsReport>                                        │
│ - <NutrientRadarChart>                                           │
│ - <MealPlanGenerator>                                            │
└─────────────────────────────────────────────────────────────────┘
```

### Feature Components

```
┌─────────────────────────────────────────────────────────────────┐
│                       AuthModal                                  │
│              (components/AuthModal.tsx)                          │
├─────────────────────────────────────────────────────────────────┤
│ Props:                                                           │
│ - isOpen: bool                                                   │
│ - onClose: () => void                                            │
├─────────────────────────────────────────────────────────────────┤
│ State:                                                           │
│ - mode: 'signin' | 'signup'                                      │
│ - loading: bool                                                  │
│ - error: string                                                  │
│ - formData: { email, password, name }                            │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                         │
│ + handleSubmit(e: FormEvent): Promise<void>                      │
│ + handleChange(e: ChangeEvent): void                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      FileUpload                                  │
│              (components/FileUpload.tsx)                         │
├─────────────────────────────────────────────────────────────────┤
│ Props:                                                           │
│ - onUploadSuccess: (sessionId: string) => void                   │
├─────────────────────────────────────────────────────────────────┤
│ State:                                                           │
│ - file: File | null                                              │
│ - uploading: bool                                                │
│ - error: string                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                         │
│ + handleFileChange(e: ChangeEvent): void                         │
│ + handleUpload(): Promise<void>                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Questionnaire                                 │
│            (components/Questionnaire.tsx)                        │
├─────────────────────────────────────────────────────────────────┤
│ Props:                                                           │
│ - onSubmit: (answers: any) => void                               │
├─────────────────────────────────────────────────────────────────┤
│ State:                                                           │
│ - answers: Record<string, any>                                   │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                         │
│ + handleChange(field: string, value: any): void                  │
│ + handleSubmit(e: FormEvent): void                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 RecommendationsReport                            │
│          (components/RecommendationsReport.tsx)                  │
├─────────────────────────────────────────────────────────────────┤
│ Props:                                                           │
│ - recommendations: any                                           │
│ - geneticSummary: any                                            │
├─────────────────────────────────────────────────────────────────┤
│ Sections:                                                        │
│ - Summary Statistics                                             │
│ - High Priority Recommendations                                  │
│ - Moderate Priority Recommendations                              │
│ - Foods to Increase                                              │
│ - Foods to Limit                                                 │
│ - Supplements to Consider                                        │
│ - General Advice                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 NutrientRadarChart                               │
│           (components/NutrientRadarChart.tsx)                    │
├─────────────────────────────────────────────────────────────────┤
│ Props:                                                           │
│ - data: Array<{nutrient: string, score: number}>                 │
├─────────────────────────────────────────────────────────────────┤
│ Library: Recharts                                                │
│ Chart Type: Radar Chart                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  MealPlanGenerator                               │
│           (components/MealPlanGenerator.tsx)                     │
├─────────────────────────────────────────────────────────────────┤
│ Props:                                                           │
│ - sessionId: string                                              │
├─────────────────────────────────────────────────────────────────┤
│ State:                                                           │
│ - days: number                                                   │
│ - generating: bool                                               │
│ - mealPlan: any | null                                           │
│ - error: string                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                         │
│ + handleGenerate(): Promise<void>                                │
│ + renderMealPlan(): JSX.Element                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Relationships & Data Flow

### Entity Relationships

```
User (1) ──────< (n) Session
                       │
                       ├──── (1:1) GeneticResults
                       │
                       ├──── (1:1) Questionnaire
                       │
                       └──── (1:1) Recommendations
```

### Application Flow

```
1. User Authentication
   LandingPage → AuthModal → POST /api/auth/login → JWT Token → localStorage

2. File Upload
   FileUpload → POST /api/upload → Session created → session_id returned

3. Genetic Analysis
   AnalysisPage → POST /api/analyze → GeneticParser.analyze_all()
   → encrypt_genetic_findings() → GeneticResults saved

4. Questionnaire
   Questionnaire → POST /api/questionnaire → Questionnaire saved

5. Recommendations
   AnalysisPage → GET /api/recommendations/<session_id>
   → generate_personalized_recommendations() → Recommendations saved
   → NutrientRadarChart rendered

6. AI Meal Plan
   MealPlanGenerator → POST /api/generate-meal-plan
   → Groq API (Llama 3.3 70B) → Meal plan returned
```

### Security Flow

```
Authentication:
User credentials → hash_password() → MongoDB → JWT token → Frontend

Protected Routes:
Request with JWT → @require_auth decorator → decode_token()
→ Verify → Add user_id to request context → Execute route

Data Encryption:
Genetic findings → encrypt_genetic_findings() → Fernet encryption
→ MongoDB → decrypt_genetic_findings() → Display to user
```

---

## Key Design Patterns

1. **Repository Pattern**: Database operations abstracted in `models.py`
2. **Service Layer**: Business logic in `genetic_parser.py`, `ai_meal_planner.py`
3. **Singleton Pattern**: Global database instance, encryption instance
4. **Decorator Pattern**: `@require_auth` for protected routes
5. **Factory Pattern**: `Session.create_new()`, `User.create()`
6. **Strategy Pattern**: Different encryption/decryption strategies
7. **Component Composition**: React components composed in pages

---

## Technology Stack

**Backend:**
- Flask (API server)
- MongoDB (database)
- PyMongo (database driver)
- bcrypt (password hashing)
- PyJWT (authentication)
- Cryptography/Fernet (data encryption)
- Groq API (AI meal planning)
- snps library (genetic file parsing)

**Frontend:**
- Next.js 15 (React framework)
- TypeScript (type safety)
- Tailwind CSS (styling)
- Recharts (data visualization)
- Axios (HTTP client)
- Lucide React (icons)

**Infrastructure:**
- MongoDB (NoSQL database)
- File system (genetic data storage)
