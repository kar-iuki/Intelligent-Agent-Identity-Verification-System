# Intelligent Agent Identity Verification System

A web-based KYC verification platform that allows organisations to register independent agents, verify their identities through an AI-powered pipeline, and control platform access based on verification outcomes.

## Architecture

```
frontend/     → Vue.js (Vite)          — port 5173
backend/      → Node.js (Express)      — port 3000
ai-service/   → Python (Flask)         — port 5000
database/     → Supabase (PostgreSQL)
```

## Prerequisites

- [Node.js](https://nodejs.org/) v18 or later
- [Python](https://www.python.org/) 3.10 or later
- A [Supabase](https://supabase.com/) project

## Database Setup

1. Create a new project at [supabase.com](https://supabase.com/).
2. Open **SQL Editor** in the Supabase dashboard.
3. Paste and run the contents of [`database/schema.sql`](database/schema.sql).
4. Copy your project URL and API keys from **Settings → API**.

## Backend Setup

```bash
cd backend
cp .env.example .env        # then fill in your Supabase credentials
npm install
npm run dev
```

Verify: `GET http://localhost:3000/health` → `{ "status": "ok" }`

### Environment Variables

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anonymous (public) key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (server-side only) |
| `AI_SERVICE_URL` | URL of the Python AI service |
| `PORT` | Express server port (default: 3000) |
| `JWT_SECRET` | Secret for signing JWT tokens |

## AI Service Setup

```bash
cd ai-service
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

cp .env.example .env
pip install -r requirements.txt
python app.py
```

Verify: `GET http://localhost:5000/health` → `{ "status": "ok" }`

> **Note:** Full AI dependencies (InsightFace, EasyOCR, etc.) are large and may require additional system libraries.

### InsightFace / ArcFace (face matching)

```bash
pip install insightface onnxruntime
```

- On first run, the `buffalo_l` model downloads to `~/.insightface/models/buffalo_l` (internet required).
- On Linux you may also need build tools: `sudo apt-get install cmake build-essential`.
- On Windows, install a recent Visual C++ redistributable if native wheels fail to load.
- If model download or initialisation fails, `POST /api/face/verify` returns **503** with a clear error instead of crashing the service.

### Silent-Face-Anti-Spoofing (liveness detection)

The Silent-Face model lives under `ai-service/silent_face/` with pretrained weights in
`silent_face/resources/anti_spoof_models/`.

```bash
# CPU-only PyTorch (recommended for local development without a GPU)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install timm easydict
```

- Pretrained `.pth` weights must exist in `ai-service/silent_face/resources/anti_spoof_models/` before the service starts.
- Weights are included from the [Silent-Face-Anti-Spoofing](https://github.com/minivision-ai/Silent-Face-Anti-Spoofing) repository.
- All torch inference is forced to **CPU** when CUDA is unavailable.
- If weights are missing or the model fails to load, `POST /api/liveness/detect` returns **503**.
- Prefer OpenCV 4.x (`opencv-python>=4.8,<5`) for full Caffe face-detector support. On OpenCV 5 the service falls back to a center-crop bbox so liveness still runs.

### Environment Variables

| Variable | Description |
|---|---|
| `FLASK_PORT` | Flask server port (default: 5000) |
| `FLASK_ENV` | `development` or `production` |

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

The Vite dev server proxies `/api` requests to the backend at `http://localhost:3000`.

## Running All Services

Start each service in a separate terminal:

```bash
# Terminal 1 — Backend
cd backend && npm run dev

# Terminal 2 — AI Service
cd ai-service && venv\Scripts\activate && python app.py

# Terminal 3 — Frontend
cd frontend && npm run dev
```

## Project Structure

```
intelligent-agent-verification/
├── frontend/                  # Vue.js application
│   ├── src/
│   │   ├── views/             # Page components
│   │   ├── components/        # Reusable UI components
│   │   ├── router/            # Vue Router configuration
│   │   ├── services/          # Axios API calls
│   │   └── stores/            # State management
│   └── vite.config.js
│
├── backend/                   # Node.js Express application
│   ├── src/
│   │   ├── routes/            # API route definitions
│   │   ├── controllers/       # Route handler logic
│   │   ├── middleware/        # Auth, role checking, validation
│   │   ├── services/          # Business logic and external calls
│   │   └── utils/             # Helper functions, Supabase client
│   ├── .env.example
│   └── server.js
│
├── ai-service/                # Python Flask AI service
│   ├── app.py                 # Flask application entry point
│   ├── routes/                # API route definitions
│   ├── services/              # OpenCV, EasyOCR, InsightFace, SilentFace
│   ├── models/                # Saved SVM model (added later)
│   ├── requirements.txt
│   └── .env.example
│
├── database/
│   └── schema.sql             # PostgreSQL schema for Supabase
│
└── README.md
```

## Database Tables

| Table | Purpose |
|---|---|
| `users` | User accounts with role (agent / admin) |
| `agents` | Agent profile linked to a user |
| `documents` | Uploaded identity documents |
| `verification_requests` | KYC verification requests |
| `verification_scores` | Six pipeline scores per request |
| `kyc_decisions` | SVM classifier outcome |
| `access_control_records` | Access grant/deny per decision |
| `audit_logs` | Action audit trail |

## Health Checks

| Service | Endpoint |
|---|---|
| Backend | `GET /health` |
| AI Service | `GET /health` |
