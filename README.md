# ResumeIQ — AI Document Verification & Resume Intelligence Platform

ResumeIQ is a production-ready, full-stack event-driven platform designed to ingest documents (PDF, DOCX, JPG, PNG), perform deterministic quality checking, run two-pass NLP/CV classification, redact sensitive identifiers (PII compliance), and provide detailed Resume ATS scoring, AI authorship probability ratings, and job-description semantic matching.

---

## 🛠️ Architecture & Core Components

1. **API Gateway (FastAPI)**:
   * Lightweight orchestration. Validates uploads, stores them, updates database to `pending`, and immediately returns a unique task ID.
   * Leverages stateless session management stored in Secure Same-Site HTTP-Only cookies.
2. **Distributed Tasks Worker Pool (Celery + Redis)**:
   * Background task queues executing all heavy calculations asynchronously.
   * Auto-fallback: If Redis is unavailable locally, the backend routes tasks to FastAPI's in-memory `BackgroundTasks` thread pool.
3. **Two-Pass AI Classification**:
   * *Pass 1 (Visual)*: OpenCV reads layout attributes (margins, aspect ratio, text densities, lines/grids, profile shapes) to categorize documents.
   * *Pass 2 (Textual)*: Scans parsed OCR text, matching keyword density metrics across 11 standard formats.
   * *Consensus*: Cross-validates findings to yield verified labels and confidence scores.
4. **Compliance PII Redaction Pipeline**:
   * Intercepts extracted text for sensitive identity cards (Aadhaar, PAN, DL, Passport), matching and replacing digits with secure redact labels prior to storage.
5. **Deterministic Quality Engine**:
   * Detects image blur (Laplacian variance), page count, empty pages (pixel variances / text length), rotation tilt, and binary spoofing (magic numbers validation).
   * Generates hashes (SHA-256) to flag exact duplicate file uploads.
6. **Resume Intelligence Parser**:
   * Extracts contact details, skills, education, projects, achievements, and certifications.
   * *Skill Chronology*: Parses experience blocks chronologically, calculating cumulative years of experience per skill based on date ranges.
7. **ATS Score & AI written Detector**:
   * Audits formatting patterns, bullet structures, reading ease (syllable-based Flesch Readability Ease), and verb selections.
   * Calculates Type-Token Lexical Diversity (repetition) and sentence length standard deviation (burstiness) to estimate generative AI assistance percentages.
8. **Semantic Job Matcher**:
   * Matches resume profiles to Job Descriptions using TF-IDF Cosine Similarity and Jaccard intersection matrices, revealing hidden skills gaps.

---

## 📂 Directory Structure

```
doc_verify/
├── backend/                  # FastAPI Gateway & Celery Workers
│   ├── app/
│   │   ├── api/              # Route endpoints (Auth, Documents, Jobs, Admin)
│   │   ├── core/             # Configuration settings, Security, DB session pool
│   │   ├── models/           # SQLAlchemy models (User, Document, ResumeAnalysis)
│   │   ├── schemas/          # Pydantic schemas validating payloads
│   │   ├── services/         # Extraction, Quality checks, Redactions, ATS logic
│   │   └── worker/           # Celery application & asynchronous queue tasks
│   ├── tests/                # Unit test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # React + TypeScript + Tailwind SPA Dashboard
│   ├── src/
│   │   ├── components/       # AuthCard inputs toggle layout
│   │   ├── pages/            # Dashboard, DragUploader, ATS details, JobMatcher, Admin Panel
│   │   ├── services/         # Axios api request instance
│   │   ├── App.tsx           # Route controllers & tab toggles
│   │   └── index.css         # Styling system, glassmorphism, animations
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── docker-compose.yml        # Multi-container orchestration blueprints
└── README.md
```

---

## ⚡ Quick Start

### 🐳 Run Containerized (Docker Compose)
Launch the full containerized environment (PostgreSQL, Redis, Celery, API Gateway, and Vite React frontend):
```bash
docker-compose up --build
```
* **Frontend Dashboard**: Open `http://localhost:5173`
* **API Documentation**: Open `http://localhost:8000/docs`

---

### 💻 Run Locally (Independent Services)
If Redis is not installed, the platform uses in-memory multi-threaded task queues:

#### 1. Setup Backend
1. Install Python packages:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Launch the FastAPI server:
   ```bash
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   * *Note*: DB tables are auto-created in a local `resumeiq.db` SQLite database on startup.

#### 2. Setup Frontend
1. Navigate to the frontend folder and install npm packages:
   ```bash
   cd frontend
   npm install
   ```
2. Start the Vite React development server:
   ```bash
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.

---

## 🧪 Running Automated Tests
Run unit tests verifying magic-byte headers checks, data redactions, Flesch reading ease, and AI detection estimators:
```bash
python -m pytest backend/tests/
```
All 5 tests are fully passed.

---

## 🔒 Security & Data Protection compliance
* Stateless user sessions utilizing temporary JWT tokens stored in HttpOnly, Same-Site cookies, guarding against CSRF and XSS.
* Magic number header byte validation blocks extension spoofing.
* Binary SHA-256 hashing blocks duplicate storage wastes.
* Interactive category override panel in the Admin Panel lets managers correct classification labels, updating models diagnostic statistics in real-time.
