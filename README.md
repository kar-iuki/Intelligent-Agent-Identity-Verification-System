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

## Verified-agent file retention

Identity images and selfies are retained for three business days after the latest
successful verification decision (including manual approval). Business days are
Monday–Friday in Africa/Nairobi; public holidays are not excluded. For example,
verification on Friday at 14:00 expires on Wednesday at 14:00.

The backend checks expiry at startup and every 15 minutes, including superseded
uploads. It deletes storage objects and clears their file references, preserving
document rows, decisions, scores, and audit history. Failed storage removals are
retried on the next run. Pending, review, and rejected cases are not purged by this
policy. No database migration is required. Existing verified cases also follow
this policy when the updated backend starts. Keep the backend running to execute
cleanup; signed admin image links cannot outlive the audit window.

The admin dashboard opens on the agent directory, followed by recent activity.
**Last 3 business days** shows verified agents whose audit window is still open,
with verification timestamps and audit deadlines.

## Health Checks

| Service | Endpoint |
|---|---|
| Backend | `GET /health` |
| AI Service | `GET /health` |

## Optional passkey authentication

Passkeys supplement password and Google login. The Vue client uses
`@simplewebauthn/browser`; Express verifies credentials with
`@simplewebauthn/server`. Node 22 or newer is required. No biometric data is
stored. Existing authentication and recovery methods remain available.

### Supabase and environment setup

1. In **Supabase → SQL Editor**, run the entire [database/passkeys.sql](database/passkeys.sql)
   file after the existing schema. It adds the user handle, passkeys, expiring
   challenges, shared rate-limit storage, and restricted SQL functions. It is
   safe to rerun. Do not rerun `schema.sql` on an existing installation.
2. Keep the Email provider enabled under **Authentication → Providers**. After
   verifying a passkey, the backend generates and consumes a server-only
   magic-link token to obtain a normal Supabase session; no email is sent.
   The account must have a confirmed email. Keep existing Google settings.
   No Supabase JWT secret or new frontend service-role key is needed.
3. Add these values to `backend/.env` for local development:

   ```dotenv
   WEBAUTHN_RP_ID=localhost
   WEBAUTHN_RP_NAME=Agent Identity Verification
   WEBAUTHN_ORIGINS=http://localhost:5173
   TRUST_PROXY=loopback
   ```

   For deployment, set the RP ID to your stable domain (no scheme, port, or path),
   and origins to the exact HTTPS frontend origins, comma-separated, without
   trailing slashes. Origins must belong to that RP domain. Set `FRONTEND_URL`
   consistently for CORS. HTTPS is required except on localhost; HTTP LAN IPs
   do not work. Changing an ngrok hostname or RP domain requires new passkeys.
   If using a remote reverse proxy, configure `TRUST_PROXY` with its actual
   trusted IPs/CIDRs and prevent direct access that could bypass it.
4. Install dependencies with `npm install --prefix backend` and
   `npm install --prefix frontend`, then restart both services.

The migration grants access only to the backend service role, not anonymous or
authenticated browser clients. Keep `SUPABASE_SERVICE_ROLE_KEY` server-side.
All passkey endpoints use the existing `/api/auth` prefix. Authenticated changes
require explicit Bearer tokens and an allowed Origin (no ambient auth cookies).
Challenges expire after five minutes and are consumed atomically even on
verification failure. Rate limiting allows 60 passkey requests per IP per five
minutes across backend instances. Counter updates use compare-and-swap; removal
is serialized per user and checks actual Supabase password/OAuth recovery methods.
There is no existing reauthentication or user-preferences framework in this app;
removal follows existing authenticated-action conventions, and prompt preferences
are browser-local. No new one-time-code login UI is introduced.

The popup waits for the results/workspace screen rather than interrupting identity
forms. Skip permanently dismisses by default; change
`MAX_SKIPS_BEFORE_PERMANENT_DISMISS` in `frontend/src/utils/passkeyStorage.js`
to permit reminders. Local flags are hints only and survive sign-out. A duplicate
registration confirms availability without inventing an unknown credential ID.
Manage Passkeys remains available after dismissal; incapable browsers see only
the existing list without management actions. Styling follows the existing light
theme; the app has no theme switcher or i18n framework.

### Verification

```sh
npm run test:passkeys --prefix backend
npm run test:passkeys --prefix frontend
npx --prefix frontend playwright install chromium
npm run test:passkeys:e2e --prefix frontend
npm run build --prefix frontend
```

Backend tests include actual migration execution in embedded PostgreSQL. Browser
tests use a Chromium virtual authenticator and real WebAuthn signature verification,
with isolated storage and a stubbed Supabase session boundary. Conditional autofill
tests simulate selecting the dropdown item because CDP cannot select native autofill
UI. After deploying, verify a real password login → passkey setup → sign-out →
passkey login against your Supabase project, plus native autofill and phone/QR
handoff on your target devices. These live integrations are not certified by the
isolated tests.
