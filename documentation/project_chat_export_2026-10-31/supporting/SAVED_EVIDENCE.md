# Saved evidence and configuration descriptions

These are retained source records, not new test runs. The top-level ml/reports folder describes the original v2 experiment; experiments/v3 and models/artifact_manifest.json identify the v3 comparison and installed bundle. Failed commands and later retests are preserved where present.


---

## README.md

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
   The current hosted frontend configuration is in
   [`backend/.env.hosted.example`](backend/.env.hosted.example). Copy those four
   settings into the **hosted backend's environment settings**, replacing the
   old localhost values, then redeploy/restart the backend. Sign in using email
   or Google on the hosted site and register a new passkey there. A localhost
   passkey cannot be moved to the hosted domain.

   If `WEBAUTHN_ORIGINS` is omitted, the backend uses `FRONTEND_URL`. If
   `WEBAUTHN_RP_ID` is also omitted, it infers the RP ID only when all configured
   origins have the same hostname. Explicit WebAuthn settings always take
   precedence; stale localhost values must be replaced or removed. Request
   headers never expand the trusted origins.
   If using a remote reverse proxy, configure `TRUST_PROXY` with its actual
   trusted IPs/CIDRs and prevent direct access that could bypass it.
4. Install dependencies with `npm install --prefix backend` and
   `npm install --prefix frontend`, then restart both services.

Document file selection is available before the first submitted verification.
After any saved verification attempt (including a quality failure), document
recapture requires the camera for ID front/back, passports, and driving licences.
The server returns this requirement on registration status and rejects missing
or upload source metadata on retries. Camera source metadata is a workflow
restriction, not cryptographic proof of live capture; it does not guarantee that
a modified client or a photographed forgery will be detected.

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



---

## frontend/COLORS.md

# Verity colour system

`src/theme.css` owns the UI palette and the light/dark equivalents. Import it
before component and workspace styles. Use the same roles in new components:

| Role | Use |
| --- | --- |
| `--brand`, `--brand-paper`, `--brand-sage` | Deep teal, ivory and sage brand artwork |
| `--action`, `--action-hover`, `--on-brand` | Primary controls |
| `--ink`, `--muted`, `--link` | Text and navigation |
| `--surface`, `--surface-muted`, `--canvas`, `--line` | Panels, page backgrounds and borders |
| `--success`, `--success-bg`, `--success-border` | Verified, passed, completed |
| `--warning`, `--warning-bg`, `--warning-border` | Pending, review, caution |
| `--danger`, `--danger-bg`, `--danger-border` | Failed, rejected, blocked, errors |
| `--info`, `--info-bg`, `--info-border` | Guidance and informational checks |
| `--focus`, `--focus-ring` | Keyboard focus and focused inputs |

Use the foreground/background/border trio together. Use `--success-solid` or
`--danger-solid` with `--on-brand` for filled decision buttons; status text
colours become lighter in dark mode and must not be used as white-text fills.

Keep status text or icons alongside colour. Score bars show an assessment as
well as their number and colour. Model-chart intensity describes a share, not
a verification decision. Brand illustrations and camera overlays retain their
own artwork colours; the public landing page intentionally stays ivory.



---

## documentation/deployment_checks_2026-10-27.json

```json
[
  {
    "body": "HTML received",
    "status": 200,
    "url": "https://intelligent-agent-identity-verifica.vercel.app"
  },
  {
    "body": "{\"status\":\"ok\"}",
    "status": 200,
    "url": "https://verity-backend-gvbs.onrender.com/health"
  },
  {
    "body": "{\"status\":\"ok\"}\n",
    "status": 200,
    "url": "https://verity-ai.greenpond-207a4102.southafricanorth.azurecontainerapps.io/health"
  },
  {
    "url": "https://verity-ai.greenpond-207a4102.southafricanorth.azurecontainerapps.io/api/svm/status",
    "error": "Response status code does not indicate success: 401 (Unauthorized)."
  }
]

```


---

## ai-service/ml/reports/ablation_comparison.json

```json
{
  "status": "V3 comparison to saved v2 identity model is not a controlled feature ablation.",
  "prior_controlled_ablation": "legacy_v2/reports/ablation_comparison.json"
}
```


---

## ai-service/ml/reports/benchmark_measurements.json

```json
{
  "generated_by": "ml/measure_benchmarks.py",
  "seed": 42,
  "lfw_faceMatchScore": {
    "genuine": {
      "n": 500,
      "mean": 64.8173,
      "std": 16.474,
      "p05": 36.9966,
      "p25": 60.81,
      "median": 68.287,
      "p75": 73.742,
      "p95": 81.9216
    },
    "impostor": {
      "n": 500,
      "mean": 2.2927,
      "std": 3.5656,
      "p05": 0.0,
      "p25": 0.0,
      "median": 0.0,
      "p75": 3.4939,
      "p95": 9.4883
    }
  },
  "lfw_faces_detected_rate": 0.993,
  "nuaa_livenessScore": {
    "photo_attack": {
      "n": 600,
      "mean": 0.02,
      "std": 0.0752,
      "p05": 0.0,
      "p25": 0.0,
      "median": 0.0,
      "p75": 0.0016,
      "p95": 0.1126
    },
    "real": {
      "n": 600,
      "mean": 0.9689,
      "std": 0.0704,
      "p05": 0.8524,
      "p25": 0.9741,
      "median": 0.9944,
      "p75": 0.9988,
      "p95": 0.9998
    }
  },
  "midv_image_quality": {
    "blurScore": {
      "clutter": {
        "n": 100,
        "mean": 67.8334,
        "std": 76.5728,
        "p05": 13.246,
        "p25": 24.8973,
        "median": 44.6589,
        "p75": 78.8192,
        "p95": 170.6026
      },
      "hand": {
        "n": 100,
        "mean": 48.8205,
        "std": 47.2975,
        "p05": 10.3354,
        "p25": 22.2487,
        "median": 34.8282,
        "p75": 61.9094,
        "p95": 118.7709
      },
      "keyboard": {
        "n": 100,
        "mean": 69.4914,
        "std": 55.8344,
        "p05": 13.3642,
        "p25": 32.2652,
        "median": 55.681,
        "p75": 85.7352,
        "p95": 169.4581
      },
      "partial": {
        "n": 100,
        "mean": 47.066,
        "std": 69.1011,
        "p05": 6.2751,
        "p25": 12.6388,
        "median": 25.3193,
        "p75": 48.3705,
        "p95": 153.0757
      },
      "table": {
        "n": 100,
        "mean": 58.0719,
        "std": 51.5951,
        "p05": 10.7984,
        "p25": 26.6417,
        "median": 44.3977,
        "p75": 74.3027,
        "p95": 130.1304
      }
    },
    "brightnessScore": {
      "clutter": {
        "n": 100,
        "mean": 180.2123,
        "std": 41.3346,
        "p05": 101.9843,
        "p25": 165.9997,
        "median": 190.5894,
        "p75": 207.3692,
        "p95": 230.0326
      },
      "hand": {
        "n": 100,
        "mean": 169.4006,
        "std": 41.5128,
        "p05": 67.0872,
        "p25": 159.6868,
        "median": 178.1146,
        "p75": 193.5266,
        "p95": 221.2489
      },
      "keyboard": {
        "n": 100,
        "mean": 169.1825,
        "std": 59.4054,
        "p05": 75.3974,
        "p25": 121.991,
        "median": 181.758,
        "p75": 218.3731,
        "p95": 244.5237
      },
      "partial": {
        "n": 100,
        "mean": 143.689,
        "std": 46.1593,
        "p05": 50.4693,
        "p25": 117.4385,
        "median": 151.8936,
        "p75": 178.5741,
        "p95": 204.3674
      },
      "table": {
        "n": 100,
        "mean": 196.0157,
        "std": 19.5882,
        "p05": 168.883,
        "p25": 180.3534,
        "median": 194.6019,
        "p75": 212.0294,
        "p95": 227.866
      }
    },
    "contrastScore": {
      "clutter": {
        "n": 100,
        "mean": 41.3186,
        "std": 11.5511,
        "p05": 22.546,
        "p25": 33.0354,
        "median": 40.1811,
        "p75": 47.5603,
        "p95": 62.2248
      },
      "hand": {
        "n": 100,
        "mean": 41.6231,
        "std": 11.9714,
        "p05": 24.4431,
        "p25": 32.8177,
        "median": 41.9163,
        "p75": 48.6409,
        "p95": 59.958
      },
      "keyboard": {
        "n": 100,
        "mean": 53.3095,
        "std": 25.7094,
        "p05": 24.9864,
        "p25": 34.6322,
        "median": 42.2887,
        "p75": 77.0041,
        "p95": 96.2933
      },
      "partial": {
        "n": 100,
        "mean": 44.3334,
        "std": 16.9412,
        "p05": 18.9699,
        "p25": 29.2037,
        "median": 44.1636,
        "p75": 56.5668,
        "p95": 69.7261
      },
      "table": {
        "n": 100,
        "mean": 35.6632,
        "std": 7.7654,
        "p05": 23.2637,
        "p25": 29.4536,
        "median": 34.8729,
        "p75": 42.4386,
        "p95": 48.042
      }
    }
  },
  "midv_document_found_rate": 0.968,
  "midv_ocrConfidenceScore": {
    "clutter": {
      "n": 96,
      "mean": 0.4491,
      "std": 0.3382,
      "p05": 0.0,
      "p25": 0.1077,
      "median": 0.4612,
      "p75": 0.7615,
      "p95": 0.9535
    },
    "hand": {
      "n": 96,
      "mean": 0.5738,
      "std": 0.304,
      "p05": 0.0,
      "p25": 0.3378,
      "median": 0.6501,
      "p75": 0.8338,
      "p95": 0.975
    },
    "keyboard": {
      "n": 96,
      "mean": 0.4729,
      "std": 0.3251,
      "p05": 0.0,
      "p25": 0.1749,
      "median": 0.5096,
      "p75": 0.7716,
      "p95": 0.9479
    },
    "partial": {
      "n": 96,
      "mean": 0.1712,
      "std": 0.2826,
      "p05": 0.0,
      "p25": 0.0,
      "median": 0.0,
      "p75": 0.2817,
      "p95": 0.8243
    },
    "table": {
      "n": 96,
      "mean": 0.5925,
      "std": 0.3437,
      "p05": 0.0,
      "p25": 0.2941,
      "median": 0.6967,
      "p75": 0.8865,
      "p95": 0.9865
    }
  }
}
```


---

## ai-service/ml/reports/distribution_overlap_diagnostics.json

```json
{
  "face_match_score": {
    "class_statistics": {
      "Manual Review": {
        "mean": 57.83835575914686,
        "std": 18.193719540206796,
        "min": 1.938215720308864,
        "max": 100.0,
        "p05": 26.6671540173671,
        "p95": 87.92481403470687
      },
      "Rejected": {
        "mean": 43.89285400011859,
        "std": 29.323834914396162,
        "min": 0.0,
        "max": 100.0,
        "p05": 0.11994482109892589,
        "p95": 85.22584176625611
      },
      "Verified": {
        "mean": 62.589893184884325,
        "std": 16.897905873331414,
        "min": 0.0,
        "max": 100.0,
        "p05": 33.47271206385084,
        "p95": 89.52739759777651
      }
    },
    "pairwise_overlap": {
      "Manual Review / Rejected": {
        "central_90_percent_intersection": [
          26.6671540173671,
          85.22584176625611
        ]
      },
      "Manual Review / Verified": {
        "central_90_percent_intersection": [
          33.47271206385084,
          87.92481403470687
        ]
      },
      "Rejected / Verified": {
        "central_90_percent_intersection": [
          33.47271206385084,
          85.22584176625611
        ]
      }
    }
  },
  "liveness_score": {
    "class_statistics": {
      "Manual Review": {
        "mean": 0.8316755801364405,
        "std": 0.1739654604884198,
        "min": 0.0452616506825088,
        "max": 1.0,
        "p05": 0.4717186071201131,
        "p95": 1.0
      },
      "Rejected": {
        "mean": 0.6435712842924375,
        "std": 0.3838566834984276,
        "min": 0.0,
        "max": 1.0,
        "p05": 0.021468486510034857,
        "p95": 1.0
      },
      "Verified": {
        "mean": 0.9296648469784186,
        "std": 0.05191349205280589,
        "min": 0.682100431736264,
        "max": 1.0,
        "p05": 0.8335447420767303,
        "p95": 1.0
      }
    },
    "pairwise_overlap": {
      "Manual Review / Rejected": {
        "central_90_percent_intersection": [
          0.4717186071201131,
          1.0
        ]
      },
      "Manual Review / Verified": {
        "central_90_percent_intersection": [
          0.8335447420767303,
          1.0
        ]
      },
      "Rejected / Verified": {
        "central_90_percent_intersection": [
          0.8335447420767303,
          1.0
        ]
      }
    }
  },
  "ocr_confidence_score": {
    "class_statistics": {
      "Manual Review": {
        "mean": 0.6128544236372814,
        "std": 0.19305216968166172,
        "min": 0.0,
        "max": 1.0,
        "p05": 0.2798931927032636,
        "p95": 0.9088542753463081
      },
      "Rejected": {
        "mean": 0.617498361014954,
        "std": 0.24158528226546264,
        "min": 0.0,
        "max": 1.0,
        "p05": 0.12923461129420696,
        "p95": 0.9260706474298562
      },
      "Verified": {
        "mean": 0.6664410620373166,
        "std": 0.18308394583660337,
        "min": 0.0,
        "max": 1.0,
        "p05": 0.33037845748371064,
        "p95": 0.9344249410550466
      }
    },
    "pairwise_overlap": {
      "Manual Review / Rejected": {
        "central_90_percent_intersection": [
          0.2798931927032636,
          0.9088542753463081
        ]
      },
      "Manual Review / Verified": {
        "central_90_percent_intersection": [
          0.33037845748371064,
          0.9088542753463081
        ]
      },
      "Rejected / Verified": {
        "central_90_percent_intersection": [
          0.33037845748371064,
          0.9260706474298562
        ]
      }
    }
  },
  "blur_score": {
    "class_statistics": {
      "Manual Review": {
        "mean": 51.29568828765505,
        "std": 59.1389531347241,
        "min": 1.1371209788343406,
        "max": 914.096845375202,
        "p05": 6.661987350223745,
        "p95": 157.2473613166803
      },
      "Rejected": {
        "mean": 58.812040868633716,
        "std": 57.897742466813305,
        "min": 0.8096894608999268,
        "max": 756.7545071300684,
        "p05": 9.467323372125714,
        "p95": 170.13525516668025
      },
      "Verified": {
        "mean": 58.11825593337682,
        "std": 59.50219604041992,
        "min": 0.8644553509968256,
        "max": 683.0512964407212,
        "p05": 9.212657070392483,
        "p95": 162.38145464714182
      }
    },
    "pairwise_overlap": {
      "Manual Review / Rejected": {
        "central_90_percent_intersection": [
          9.467323372125714,
          157.2473613166803
        ]
      },
      "Manual Review / Verified": {
        "central_90_percent_intersection": [
          9.212657070392483,
          157.2473613166803
        ]
      },
      "Rejected / Verified": {
        "central_90_percent_intersection": [
          9.467323372125714,
          162.38145464714182
        ]
      }
    }
  },
  "brightness_score": {
    "class_statistics": {
      "Manual Review": {
        "mean": 165.51966295399774,
        "std": 47.07980846607897,
        "min": 0.0,
        "max": 255.0,
        "p05": 86.46235825465759,
        "p95": 247.2265192360963
      },
      "Rejected": {
        "mean": 170.50608274616098,
        "std": 45.767068983394054,
        "min": 13.3146243763849,
        "max": 255.0,
        "p05": 92.1748764679527,
        "p95": 246.42747699653324
      },
      "Verified": {
        "mean": 170.9498424098091,
        "std": 45.42635568851169,
        "min": 0.0,
        "max": 255.0,
        "p05": 92.7247000436596,
        "p95": 249.5783775780228
      }
    },
    "pairwise_overlap": {
      "Manual Review / Rejected": {
        "central_90_percent_intersection": [
          92.1748764679527,
          246.42747699653324
        ]
      },
      "Manual Review / Verified": {
        "central_90_percent_intersection": [
          92.7247000436596,
          247.2265192360963
        ]
      },
      "Rejected / Verified": {
        "central_90_percent_intersection": [
          92.7247000436596,
          246.42747699653324
        ]
      }
    }
  },
  "contrast_score": {
    "class_statistics": {
      "Manual Review": {
        "mean": 41.28147211803449,
        "std": 16.95262328294958,
        "min": 0.0,
        "max": 94.1512595718099,
        "p05": 13.002952784939337,
        "p95": 68.58238235824975
      },
      "Rejected": {
        "mean": 43.240834967479685,
        "std": 17.404792615607935,
        "min": 0.0,
        "max": 99.58361140757783,
        "p05": 15.031357210908125,
        "p95": 72.82741228693935
      },
      "Verified": {
        "mean": 42.91209297663243,
        "std": 17.086101361527568,
        "min": 0.0,
        "max": 103.75139422074238,
        "p05": 14.144044680890604,
        "p95": 70.7809707879629
      }
    },
    "pairwise_overlap": {
      "Manual Review / Rejected": {
        "central_90_percent_intersection": [
          15.031357210908125,
          68.58238235824975
        ]
      },
      "Manual Review / Verified": {
        "central_90_percent_intersection": [
          14.144044680890604,
          68.58238235824975
        ]
      },
      "Rejected / Verified": {
        "central_90_percent_intersection": [
          15.031357210908125,
          70.7809707879629
        ]
      }
    }
  }
}
```


---

## ai-service/ml/reports/evaluation_report.json

```json
{
  "accuracy": 0.758,
  "macro_f1": 0.6540822748664862,
  "weighted_f1": 0.7319794977084515,
  "per_class": {
    "verified": {
      "label": "Verified",
      "precision": 0.7854442344045368,
      "recall": 0.9233333333333333,
      "f1-score": 0.8488253319713994,
      "support": 900.0,
      "f1": 0.8488253319713994
    },
    "review": {
      "label": "Manual Review",
      "precision": 0.6307692307692307,
      "recall": 0.2733333333333333,
      "f1-score": 0.3813953488372093,
      "support": 300.0,
      "f1": 0.3813953488372093
    },
    "rejected": {
      "label": "Rejected",
      "precision": 0.717948717948718,
      "recall": 0.7466666666666667,
      "f1-score": 0.7320261437908496,
      "support": 300.0,
      "f1": 0.7320261437908496
    }
  },
  "classification_report": {
    "Verified": {
      "precision": 0.7854442344045368,
      "recall": 0.9233333333333333,
      "f1-score": 0.8488253319713994,
      "support": 900.0
    },
    "Manual Review": {
      "precision": 0.6307692307692307,
      "recall": 0.2733333333333333,
      "f1-score": 0.3813953488372093,
      "support": 300.0
    },
    "Rejected": {
      "precision": 0.717948717948718,
      "recall": 0.7466666666666667,
      "f1-score": 0.7320261437908496,
      "support": 300.0
    },
    "accuracy": 0.758,
    "macro avg": {
      "precision": 0.7113873943741619,
      "recall": 0.6477777777777778,
      "f1-score": 0.6540822748664862,
      "support": 1500.0
    },
    "weighted avg": {
      "precision": 0.7410101303863119,
      "recall": 0.758,
      "f1-score": 0.7319794977084515,
      "support": 1500.0
    }
  },
  "confusion_matrix": [
    [
      831,
      15,
      54
    ],
    [
      184,
      82,
      34
    ],
    [
      43,
      33,
      224
    ]
  ],
  "confusion_matrix_labels": [
    "Verified",
    "Manual Review",
    "Rejected"
  ],
  "errors": {
    "Verified -> Manual Review": 15,
    "Verified -> Rejected": 54,
    "Manual Review -> Verified": 184,
    "Manual Review -> Rejected": 34,
    "Rejected -> Verified": 43,
    "Rejected -> Manual Review": 33
  },
  "probability_calibration": {
    "log_loss": 0.6595962364683127,
    "multiclass_brier_sum": 0.37311037217127374,
    "brier_definition": "Mean sum of squared errors over 3 classes, range [0,2].",
    "classwise_ece_10_bins": {
      "Verified": 0.027292012128580328,
      "Manual Review": 0.03490072766360113,
      "Rejected": 0.027867448838878903
    },
    "reliability_bins": {
      "Verified": [
        {
          "lower": 0.1,
          "n": 373,
          "mean_probability": 0.13237116444796376,
          "observed_fraction": 0.10723860589812333
        },
        {
          "lower": 0.2,
          "n": 7,
          "mean_probability": 0.20760503259207722,
          "observed_fraction": 0.5714285714285714
        },
        {
          "lower": 0.30000000000000004,
          "n": 43,
          "mean_probability": 0.35341652559394704,
          "observed_fraction": 0.4883720930232558
        },
        {
          "lower": 0.4,
          "n": 40,
          "mean_probability": 0.4782964632889346,
          "observed_fraction": 0.425
        },
        {
          "lower": 0.5,
          "n": 108,
          "mean_probability": 0.5284413222641441,
          "observed_fraction": 0.5833333333333334
        },
        {
          "lower": 0.7000000000000001,
          "n": 84,
          "mean_probability": 0.787173026559391,
          "observed_fraction": 0.7023809523809523
        },
        {
          "lower": 0.8,
          "n": 845,
          "mean_probability": 0.8141645092018396,
          "observed_fraction": 0.8236686390532545
        }
      ],
      "Manual Review": [
        {
          "lower": 0.0,
          "n": 61,
          "mean_probability": 0.0357925064006868,
          "observed_fraction": 0.14754098360655737
        },
        {
          "lower": 0.1,
          "n": 1182,
          "mean_probability": 0.155726175795514,
          "observed_fraction": 0.13959390862944163
        },
        {
          "lower": 0.4,
          "n": 189,
          "mean_probability": 0.4585079170299655,
          "observed_fraction": 0.3968253968253968
        },
        {
          "lower": 0.5,
          "n": 68,
          "mean_probability": 0.5322338488693743,
          "observed_fraction": 0.75
        }
      ],
      "Rejected": [
        {
          "lower": 0.0,
          "n": 1057,
          "mean_probability": 0.0308819242369394,
          "observed_fraction": 0.03784295175023652
        },
        {
          "lower": 0.1,
          "n": 2,
          "mean_probability": 0.19476056556105362,
          "observed_fraction": 0.5
        },
        {
          "lower": 0.2,
          "n": 52,
          "mean_probability": 0.2546563429071712,
          "observed_fraction": 0.21153846153846154
        },
        {
          "lower": 0.30000000000000004,
          "n": 77,
          "mean_probability": 0.35024706267981576,
          "observed_fraction": 0.3116883116883117
        },
        {
          "lower": 0.5,
          "n": 14,
          "mean_probability": 0.5812119706488134,
          "observed_fraction": 0.14285714285714285
        },
        {
          "lower": 0.6000000000000001,
          "n": 33,
          "mean_probability": 0.6315711216998618,
          "observed_fraction": 0.42424242424242425
        },
        {
          "lower": 0.7000000000000001,
          "n": 265,
          "mean_probability": 0.7258757734143855,
          "observed_fraction": 0.7849056603773585
        }
      ]
    }
  },
  "best_params": {
    "C": 10,
    "gamma": "scale"
  },
  "cv_macro_f1": 0.6727661071732829,
  "cv_folds": 5,
  "cv_scoring": "f1_macro",
  "candidate_count": 24,
  "model_version": "3.0.0",
  "training_timestamp": "2026-10-02T19:52:30+00:00",
  "training_date": "2026-10-02T19:52:30+00:00",
  "random_seed": 42,
  "dataset_size": 10000,
  "total_records": 10000,
  "split_sizes": {
    "train": 7000,
    "validation": 1500,
    "test": 1500
  },
  "class_distribution": {
    "Verified": 6000,
    "Manual Review": 2000,
    "Rejected": 2000
  },
  "per_split_class_distributions": {
    "train": {
      "Verified": 4200,
      "Rejected": 1400,
      "Manual Review": 1400
    },
    "validation": {
      "Verified": 900,
      "Manual Review": 300,
      "Rejected": 300
    },
    "test": {
      "Verified": 900,
      "Manual Review": 300,
      "Rejected": 300
    }
  },
  "features": [
    "face_match_score",
    "liveness_score",
    "ocr_confidence_score",
    "blur_score",
    "brightness_score",
    "contrast_score"
  ],
  "feature_bounds": [
    [
      0,
      100
    ],
    [
      0,
      1
    ],
    [
      0,
      1
    ],
    [
      0,
      null
    ],
    [
      0,
      255
    ],
    [
      0,
      127.5
    ]
  ],
  "kernel": "rbf",
  "feature_generation_parameters": {
    "configuration": {
      "seed": 42,
      "class_counts": {
        "Verified": 6000,
        "Manual Review": 2000,
        "Rejected": 2000
      },
      "provenance": "Benchmark moments are computed from existing local measured CSVs. Scenario mixtures, borderline distributions, quality shifts and measurement variation are modelling assumptions, not benchmark results or real fraud prevalence.",
      "face_borderline": [
        45,
        16
      ],
      "face_difficult_impostor": [
        32,
        18
      ],
      "live_borderline": [
        0.65,
        0.17
      ],
      "live_difficult_attack": [
        0.43,
        0.24
      ],
      "ocr_borderline": [
        0.53,
        0.19
      ],
      "ocr_mismatch": [
        0.22,
        0.17
      ],
      "clear_ocr_quantile": 0.5,
      "poor_quality_shift": [
        -0.65,
        -20,
        -7
      ],
      "quality_observation_noise": [
        0.12,
        4,
        2
      ],
      "face_measurement_sd": 3,
      "live_measurement_sd": 0.025,
      "ocr_measurement_sd": 0.04,
      "ocr_quality_penalty": 0.16,
      "quality_logblur_reference": 3.4,
      "quality_contrast_reference": 25,
      "scenarios": {
        "Verified": [
          [
            "consistent_genuine",
            0.7,
            "genuine",
            "real",
            "clear",
            false
          ],
          [
            "genuine_reading_variation",
            0.2,
            "genuine",
            "real",
            "borderline",
            false
          ],
          [
            "genuine_face_variation",
            0.1,
            "borderline",
            "real",
            "clear",
            false
          ]
        ],
        "Manual Review": [
          [
            "uncertain_face",
            0.2,
            "borderline",
            "real",
            "clear",
            false
          ],
          [
            "uncertain_document",
            0.2,
            "genuine",
            "real",
            "borderline",
            false
          ],
          [
            "uncertain_presentation",
            0.2,
            "genuine",
            "borderline",
            "clear",
            false
          ],
          [
            "recapture_needed",
            0.25,
            "genuine",
            "real",
            "clear",
            true
          ],
          [
            "multiple_uncertainties",
            0.15,
            "borderline",
            "borderline",
            "borderline",
            false
          ]
        ],
        "Rejected": [
          [
            "identity_mismatch",
            0.25,
            "impostor",
            "real",
            "clear",
            false
          ],
          [
            "photo_attack",
            0.25,
            "genuine",
            "attack",
            "clear",
            false
          ],
          [
            "document_mismatch",
            0.2,
            "genuine",
            "real",
            "mismatch",
            false
          ],
          [
            "difficult_identity_mismatch",
            0.15,
            "difficult_impostor",
            "real",
            "clear",
            false
          ],
          [
            "difficult_presentation_attack",
            0.15,
            "genuine",
            "difficult_attack",
            "clear",
            false
          ]
        ]
      }
    },
    "measured_sources": {
      "lfw_face_match": {
        "rows": 1000,
        "sha256": "ed82a85dfb6ab74ab338c1d396eb3cb66439a7a10784c12449f408ed5db9f86c"
      },
      "nuaa_liveness": {
        "rows": 1200,
        "sha256": "bbecefd0c98140ec54a8c230c1c4abf1fc57c9faf129056a4d3957e066787e5f"
      },
      "midv_image_quality": {
        "rows": 500,
        "sha256": "c39f918cdc086f0bb02dd4f8406f049121788c03487379a38f025e1e28250326"
      },
      "midv_ocr": {
        "rows": 480,
        "sha256": "5b13defefbef0ddf92df071b0c933e04a1e2ae81cff4542269cdd184da2c25f1"
      }
    },
    "measured_parameters": {
      "face": {
        "genuine": [
          64.81733419999999,
          16.47402134717157
        ],
        "impostor": [
          2.2927294000000003,
          3.5656385254627487
        ]
      },
      "liveness": {
        "photo_attack": [
          0.0199725,
          0.07516618512376493
        ],
        "real": [
          0.9689096666666668,
          0.07043918443874983
        ]
      },
      "ocr_clear_conditional": [
        0.76895625,
        0.1489445240948629
      ],
      "ocr_all": [
        0.45190208333333337,
        0.35222573712218497
      ],
      "quality_transformed_mean": [
        3.7200620127901636,
        171.70002240000002,
        43.2495346
      ],
      "quality_transformed_covariance": [
        [
          0.7211578661338847,
          11.38622734783699,
          0.4879691908211453
        ],
        [
          11.38622734783699,
          2172.433061105429,
          -275.16620785919343
        ],
        [
          0.4879691908211453,
          -275.16620785919343,
          288.27221128831945
        ]
      ]
    },
    "scenario_counts": {
      "consistent_genuine": 4263,
      "genuine_reading_variation": 1169,
      "genuine_face_variation": 568,
      "uncertain_face": 387,
      "uncertain_document": 445,
      "uncertain_presentation": 381,
      "recapture_needed": 500,
      "multiple_uncertainties": 287,
      "identity_mismatch": 516,
      "photo_attack": 486,
      "document_mismatch": 378,
      "difficult_identity_mismatch": 315,
      "difficult_presentation_attack": 305
    },
    "caveat": "Truncated normals approximate benchmark moments; resulting moments differ after truncation. Joint KYC labels and cross-modality dependencies are assumptions. No benchmark is a joint KYC ground-truth dataset."
  },
  "library_versions": {
    "scikit-learn": "1.9.0",
    "numpy": "2.5.3",
    "scipy": "1.18.1",
    "pandas": "3.0.6",
    "joblib": "1.6.0",
    "matplotlib": "3.11.2",
    "flask": "3.1.3"
  },
  "python_version": "3.13.3",
  "svm_parameters": {
    "kernel": "rbf",
    "class_weight": "balanced",
    "random_state": 42,
    "C": 10,
    "gamma": "scale",
    "architecture": "raw_native_sigmoid"
  },
  "scaler_parameters": {
    "clip": true,
    "copy": true,
    "feature_range": [
      0,
      1
    ]
  },
  "scaler_training_min": [
    0.0,
    0.0,
    0.0,
    0.8096894608999268,
    0.0,
    0.0
  ],
  "scaler_training_max": [
    100.0,
    1.0,
    1.0,
    756.7545071300684,
    255.0,
    103.75139422074238
  ],
  "scaler_samples_seen": 7000,
  "svm_permutation_importance": [
    {
      "feature": "face_match_score",
      "importance": 0.11044218744418285,
      "std": 0.0059948739786623234
    },
    {
      "feature": "liveness_score",
      "importance": 0.2013802958956386,
      "std": 0.008477352561759405
    },
    {
      "feature": "ocr_confidence_score",
      "importance": 0.049801803680355784,
      "std": 0.00758782838611898
    },
    {
      "feature": "blur_score",
      "importance": 0.0038308071117566012,
      "std": 0.0033569902461075035
    },
    {
      "feature": "brightness_score",
      "importance": -0.0003592163421191286,
      "std": 0.00392406430600547
    },
    {
      "feature": "contrast_score",
      "importance": -0.0034394830448940873,
      "std": 0.0036047996188125465
    }
  ],
  "decision_tree_feature_importance": [
    {
      "feature": "face_match_score",
      "importance": 0.4110041169906758
    },
    {
      "feature": "liveness_score",
      "importance": 0.5888252060676145
    },
    {
      "feature": "ocr_confidence_score",
      "importance": 0.0
    },
    {
      "feature": "blur_score",
      "importance": 0.0
    },
    {
      "feature": "brightness_score",
      "importance": 0.0001706769417097141
    },
    {
      "feature": "contrast_score",
      "importance": 0.0
    }
  ],
  "decision_tree": {
    "accuracy": 0.7566666666666667,
    "macro_f1": 0.6484692669061625,
    "weighted_f1": 0.7268337215269828,
    "per_class": {
      "verified": {
        "label": "Verified",
        "precision": 0.7436548223350253,
        "recall": 0.9766666666666667,
        "f1-score": 0.8443804034582133,
        "support": 900.0,
        "f1": 0.8443804034582133
      },
      "review": {
        "label": "Manual Review",
        "precision": 0.6231884057971014,
        "recall": 0.2866666666666667,
        "f1-score": 0.3926940639269406,
        "support": 300.0,
        "f1": 0.3926940639269406
      },
      "rejected": {
        "label": "Rejected",
        "precision": 0.9444444444444444,
        "recall": 0.5666666666666667,
        "f1-score": 0.7083333333333334,
        "support": 300.0,
        "f1": 0.7083333333333334
      }
    },
    "classification_report": {
      "Verified": {
        "precision": 0.7436548223350253,
        "recall": 0.9766666666666667,
        "f1-score": 0.8443804034582133,
        "support": 900.0
      },
      "Manual Review": {
        "precision": 0.6231884057971014,
        "recall": 0.2866666666666667,
        "f1-score": 0.3926940639269406,
        "support": 300.0
      },
      "Rejected": {
        "precision": 0.9444444444444444,
        "recall": 0.5666666666666667,
        "f1-score": 0.7083333333333334,
        "support": 300.0
      },
      "accuracy": 0.7566666666666667,
      "macro avg": {
        "precision": 0.7704292241921905,
        "recall": 0.61,
        "f1-score": 0.6484692669061625,
        "support": 1500.0
      },
      "weighted avg": {
        "precision": 0.7597194634493244,
        "recall": 0.7566666666666667,
        "f1-score": 0.7268337215269828,
        "support": 1500.0
      }
    },
    "confusion_matrix": [
      [
        879,
        17,
        4
      ],
      [
        208,
        86,
        6
      ],
      [
        95,
        35,
        170
      ]
    ],
    "confusion_matrix_labels": [
      "Verified",
      "Manual Review",
      "Rejected"
    ],
    "errors": {
      "Verified -> Manual Review": 17,
      "Verified -> Rejected": 4,
      "Manual Review -> Verified": 208,
      "Manual Review -> Rejected": 6,
      "Rejected -> Verified": 95,
      "Rejected -> Manual Review": 35
    },
    "probability_calibration": {
      "log_loss": 0.7898361054224619,
      "multiclass_brier_sum": 0.4611110051199686,
      "brier_definition": "Mean sum of squared errors over 3 classes, range [0,2].",
      "classwise_ece_10_bins": {
        "Verified": 0.2053727324212735,
        "Manual Review": 0.1434534504280226,
        "Rejected": 0.06593906338228817
      },
      "reliability_bins": {
        "Verified": [
          {
            "lower": 0.0,
            "n": 318,
            "mean_probability": 0.020403125115870252,
            "observed_fraction": 0.0660377358490566
          },
          {
            "lower": 0.4,
            "n": 1182,
            "mean_probability": 0.4953068592057893,
            "observed_fraction": 0.7436548223350253
          }
        ],
        "Manual Review": [
          {
            "lower": 0.0,
            "n": 171,
            "mean_probability": 0.01895028652680166,
            "observed_fraction": 0.017543859649122806
          },
          {
            "lower": 0.1,
            "n": 9,
            "mean_probability": 0.1458333333333333,
            "observed_fraction": 0.3333333333333333
          },
          {
            "lower": 0.30000000000000004,
            "n": 1182,
            "mean_probability": 0.3451263537905948,
            "observed_fraction": 0.17597292724196278
          },
          {
            "lower": 0.5,
            "n": 1,
            "mean_probability": 0.5714285714285715,
            "observed_fraction": 0.0
          },
          {
            "lower": 0.7000000000000001,
            "n": 137,
            "mean_probability": 0.7207401306134249,
            "observed_fraction": 0.6277372262773723
          }
        ],
        "Rejected": [
          {
            "lower": 0.1,
            "n": 1182,
            "mean_probability": 0.15956678700359914,
            "observed_fraction": 0.08037225042301184
          },
          {
            "lower": 0.2,
            "n": 137,
            "mean_probability": 0.24265760970541023,
            "observed_fraction": 0.24817518248175183
          },
          {
            "lower": 0.4,
            "n": 1,
            "mean_probability": 0.4285714285714286,
            "observed_fraction": 1.0
          },
          {
            "lower": 0.8,
            "n": 9,
            "mean_probability": 0.8541666666666663,
            "observed_fraction": 0.6666666666666666
          },
          {
            "lower": 0.9,
            "n": 171,
            "mean_probability": 0.9724316771543315,
            "observed_fraction": 0.9590643274853801
          }
        ]
      }
    }
  },
  "identity_only_model": {
    "accuracy": 0.7486666666666667,
    "macro_f1": 0.664889976691769,
    "weighted_f1": 0.7338079355948933,
    "per_class": {
      "verified": {
        "label": "Verified",
        "precision": 0.7938247011952191,
        "recall": 0.8855555555555555,
        "f1-score": 0.8371848739495799,
        "support": 900.0,
        "f1": 0.8371848739495799
      },
      "review": {
        "label": "Manual Review",
        "precision": 0.533678756476684,
        "recall": 0.3433333333333333,
        "f1-score": 0.4178498985801217,
        "support": 300.0,
        "f1": 0.4178498985801217
      },
      "rejected": {
        "label": "Rejected",
        "precision": 0.735973597359736,
        "recall": 0.7433333333333333,
        "f1-score": 0.7396351575456053,
        "support": 300.0,
        "f1": 0.7396351575456053
      }
    },
    "classification_report": {
      "Verified": {
        "precision": 0.7938247011952191,
        "recall": 0.8855555555555555,
        "f1-score": 0.8371848739495799,
        "support": 900.0
      },
      "Manual Review": {
        "precision": 0.533678756476684,
        "recall": 0.3433333333333333,
        "f1-score": 0.4178498985801217,
        "support": 300.0
      },
      "Rejected": {
        "precision": 0.735973597359736,
        "recall": 0.7433333333333333,
        "f1-score": 0.7396351575456053,
        "support": 300.0
      },
      "accuracy": 0.7486666666666667,
      "macro avg": {
        "precision": 0.6878256850105463,
        "recall": 0.6574074074074074,
        "f1-score": 0.664889976691769,
        "support": 1500.0
      },
      "weighted avg": {
        "precision": 0.7302252914844154,
        "recall": 0.7486666666666667,
        "f1-score": 0.7338079355948933,
        "support": 1500.0
      }
    },
    "confusion_matrix": [
      [
        797,
        51,
        52
      ],
      [
        169,
        103,
        28
      ],
      [
        38,
        39,
        223
      ]
    ],
    "confusion_matrix_labels": [
      "Verified",
      "Manual Review",
      "Rejected"
    ],
    "errors": {
      "Verified -> Manual Review": 51,
      "Verified -> Rejected": 52,
      "Manual Review -> Verified": 169,
      "Manual Review -> Rejected": 28,
      "Rejected -> Verified": 38,
      "Rejected -> Manual Review": 39
    },
    "probability_calibration": {
      "log_loss": 0.6678011098622052,
      "multiclass_brier_sum": 0.3771314753056631,
      "brier_definition": "Mean sum of squared errors over 3 classes, range [0,2].",
      "classwise_ece_10_bins": {
        "Verified": 0.04416404410508559,
        "Manual Review": 0.03426952825048753,
        "Rejected": 0.019801733195630652
      },
      "reliability_bins": {
        "Verified": [
          {
            "lower": 0.1,
            "n": 387,
            "mean_probability": 0.13088064593403737,
            "observed_fraction": 0.11369509043927649
          },
          {
            "lower": 0.2,
            "n": 1,
            "mean_probability": 0.20360268677754298,
            "observed_fraction": 1.0
          },
          {
            "lower": 0.30000000000000004,
            "n": 34,
            "mean_probability": 0.35533405865873896,
            "observed_fraction": 0.4117647058823529
          },
          {
            "lower": 0.4,
            "n": 91,
            "mean_probability": 0.4570978157458643,
            "observed_fraction": 0.6043956043956044
          },
          {
            "lower": 0.5,
            "n": 8,
            "mean_probability": 0.5300316591260148,
            "observed_fraction": 0.75
          },
          {
            "lower": 0.7000000000000001,
            "n": 525,
            "mean_probability": 0.7945248599773965,
            "observed_fraction": 0.7523809523809524
          },
          {
            "lower": 0.8,
            "n": 454,
            "mean_probability": 0.8048660355064335,
            "observed_fraction": 0.8480176211453745
          }
        ],
        "Manual Review": [
          {
            "lower": 0.0,
            "n": 36,
            "mean_probability": 0.025608890631163613,
            "observed_fraction": 0.25
          },
          {
            "lower": 0.1,
            "n": 1254,
            "mean_probability": 0.15941765249372997,
            "observed_fraction": 0.14513556618819776
          },
          {
            "lower": 0.4,
            "n": 58,
            "mean_probability": 0.4844282254518758,
            "observed_fraction": 0.25862068965517243
          },
          {
            "lower": 0.5,
            "n": 149,
            "mean_probability": 0.5360859142390768,
            "observed_fraction": 0.610738255033557
          },
          {
            "lower": 0.6000000000000001,
            "n": 3,
            "mean_probability": 0.6011865477568533,
            "observed_fraction": 1.0
          }
        ],
        "Rejected": [
          {
            "lower": 0.0,
            "n": 1068,
            "mean_probability": 0.0414336659928485,
            "observed_fraction": 0.03838951310861423
          },
          {
            "lower": 0.2,
            "n": 38,
            "mean_probability": 0.26979978756067996,
            "observed_fraction": 0.2631578947368421
          },
          {
            "lower": 0.30000000000000004,
            "n": 91,
            "mean_probability": 0.3337719204316382,
            "observed_fraction": 0.2857142857142857
          },
          {
            "lower": 0.5,
            "n": 12,
            "mean_probability": 0.5847293690419866,
            "observed_fraction": 0.08333333333333333
          },
          {
            "lower": 0.6000000000000001,
            "n": 136,
            "mean_probability": 0.6846155410688669,
            "observed_fraction": 0.7941176470588235
          },
          {
            "lower": 0.7000000000000001,
            "n": 155,
            "mean_probability": 0.7295692323654134,
            "observed_fraction": 0.7354838709677419
          }
        ]
      }
    }
  },
  "ablation_comparison": {
    "status": "V3 comparison to saved v2 identity model is not a controlled feature ablation.",
    "prior_controlled_ablation": "legacy_v2/reports/ablation_comparison.json"
  },
  "duplicate_diagnostics": {
    "combined_rows": 11500,
    "exact_duplicate_vectors": 0,
    "near_duplicate_pairs": 0,
    "definition": "All differences <= face .1, live .001, OCR .001, log1p(blur) .01, brightness .1, contrast .1"
  },
  "leakage_diagnostics": {
    "training_only_cv": true,
    "calibration_selection_disjoint": true,
    "retired_test_used": false,
    "fresh_test_after_selection_freeze": true,
    "test_used_for_release_gate_not_tuning": true
  },
  "limitations": [
    "Fresh synthetic draw from the SAME assumptions; not independent real-world validation.",
    "Previously observed v2 results motivated the hypotheses; original test was retired.",
    "Calibration and selection are disjoint but small (750 each); searching policies can overfit selection.",
    "Isotonic calibration may overfit small calibration samples; temperature can preserve poor decision rankings.",
    "Latent review and genuine scenarios can share observed distributions; missing evidence remains irreducible.",
    "Decision-policy preferences do not change calibrated probability values.",
    "Quality transform and calibrators are static; no online learning."
  ],
  "split_note": "Test metrics use a new independent 1500-row draw. Original 1500 test rows are retired, not training data.",
  "training_records": 7000,
  "calibration_records": 750,
  "selection_records": 750,
  "fresh_test_records": 1500,
  "cv_source": "legacy_v2/reports/full_svm_grid_search.csv (same training rows)",
  "decision_policy": {
    "name": "probability",
    "review_multiplier": 1.0,
    "verified_threshold": 0.0,
    "verified_margin": 0.0
  },
  "experiment_report": "experiments/v3/improvement_report.json",
  "incumbent_fresh_comparison": {
    "accuracy": 0.7573333333333333,
    "macro_f1": 0.6519090558220101,
    "weighted_f1": 0.7303911011792407,
    "per_class": {
      "verified": {
        "label": "Verified",
        "precision": 0.783427495291902,
        "recall": 0.9244444444444444,
        "f1-score": 0.8481141692150866,
        "support": 900.0,
        "f1": 0.8481141692150866
      },
      "review": {
        "label": "Manual Review",
        "precision": 0.6349206349206349,
        "recall": 0.26666666666666666,
        "f1-score": 0.3755868544600939,
        "support": 300.0,
        "f1": 0.3755868544600939
      },
      "rejected": {
        "label": "Rejected",
        "precision": 0.717948717948718,
        "recall": 0.7466666666666667,
        "f1-score": 0.7320261437908496,
        "support": 300.0,
        "f1": 0.7320261437908496
      }
    },
    "classification_report": {
      "Verified": {
        "precision": 0.783427495291902,
        "recall": 0.9244444444444444,
        "f1-score": 0.8481141692150866,
        "support": 900.0
      },
      "Manual Review": {
        "precision": 0.6349206349206349,
        "recall": 0.26666666666666666,
        "f1-score": 0.3755868544600939,
        "support": 300.0
      },
      "Rejected": {
        "precision": 0.717948717948718,
        "recall": 0.7466666666666667,
        "f1-score": 0.7320261437908496,
        "support": 300.0
      },
      "accuracy": 0.7573333333333333,
      "macro avg": {
        "precision": 0.712098949387085,
        "recall": 0.6459259259259259,
        "f1-score": 0.6519090558220101,
        "support": 1500.0
      },
      "weighted avg": {
        "precision": 0.7406303677490118,
        "recall": 0.7573333333333333,
        "f1-score": 0.7303911011792407,
        "support": 1500.0
      }
    },
    "confusion_matrix": [
      [
        832,
        14,
        54
      ],
      [
        186,
        80,
        34
      ],
      [
        44,
        32,
        224
      ]
    ],
    "confusion_matrix_labels": [
      "Verified",
      "Manual Review",
      "Rejected"
    ],
    "errors": {
      "Verified -> Manual Review": 14,
      "Verified -> Rejected": 54,
      "Manual Review -> Verified": 186,
      "Manual Review -> Rejected": 34,
      "Rejected -> Verified": 44,
      "Rejected -> Manual Review": 32
    },
    "probability_calibration": {
      "log_loss": 0.6601228273209566,
      "multiclass_brier_sum": 0.3736585942269165,
      "brier_definition": "Mean sum of squared errors over 3 classes, range [0,2].",
      "classwise_ece_10_bins": {
        "Verified": 0.04605818648384579,
        "Manual Review": 0.02893870957084166,
        "Rejected": 0.019946703332966546
      },
      "reliability_bins": {
        "Verified": [
          {
            "lower": 0.1,
            "n": 369,
            "mean_probability": 0.14132392213762937,
            "observed_fraction": 0.10569105691056911
          },
          {
            "lower": 0.2,
            "n": 11,
            "mean_probability": 0.2103873415597252,
            "observed_fraction": 0.45454545454545453
          },
          {
            "lower": 0.30000000000000004,
            "n": 40,
            "mean_probability": 0.357584644738419,
            "observed_fraction": 0.475
          },
          {
            "lower": 0.4,
            "n": 43,
            "mean_probability": 0.4737237904038272,
            "observed_fraction": 0.4418604651162791
          },
          {
            "lower": 0.5,
            "n": 108,
            "mean_probability": 0.5269908688230553,
            "observed_fraction": 0.5833333333333334
          },
          {
            "lower": 0.7000000000000001,
            "n": 386,
            "mean_probability": 0.7916884332766136,
            "observed_fraction": 0.7512953367875648
          },
          {
            "lower": 0.8,
            "n": 543,
            "mean_probability": 0.8093746692367777,
            "observed_fraction": 0.856353591160221
          }
        ],
        "Manual Review": [
          {
            "lower": 0.0,
            "n": 61,
            "mean_probability": 0.03802574596337551,
            "observed_fraction": 0.14754098360655737
          },
          {
            "lower": 0.1,
            "n": 1182,
            "mean_probability": 0.15826554121632916,
            "observed_fraction": 0.13959390862944163
          },
          {
            "lower": 0.4,
            "n": 212,
            "mean_probability": 0.454823152123988,
            "observed_fraction": 0.4339622641509434
          },
          {
            "lower": 0.5,
            "n": 45,
            "mean_probability": 0.5281054023990693,
            "observed_fraction": 0.7555555555555555
          }
        ],
        "Rejected": [
          {
            "lower": 0.0,
            "n": 1057,
            "mean_probability": 0.03839666848607127,
            "observed_fraction": 0.03784295175023652
          },
          {
            "lower": 0.2,
            "n": 50,
            "mean_probability": 0.2586822335309646,
            "observed_fraction": 0.22
          },
          {
            "lower": 0.30000000000000004,
            "n": 81,
            "mean_probability": 0.3516948252568875,
            "observed_fraction": 0.30864197530864196
          },
          {
            "lower": 0.5,
            "n": 20,
            "mean_probability": 0.5799132479848949,
            "observed_fraction": 0.15
          },
          {
            "lower": 0.6000000000000001,
            "n": 149,
            "mean_probability": 0.6843161439217018,
            "observed_fraction": 0.738255033557047
          },
          {
            "lower": 0.7000000000000001,
            "n": 143,
            "mean_probability": 0.7253271022940417,
            "observed_fraction": 0.7762237762237763
          }
        ]
      }
    }
  },
  "protocol": {
    "version": "3.0.0",
    "seed": 42,
    "fresh_test_seed": 2684470948,
    "dataset_sha256": "d6dbe75aa5d765e4b3d92112e2825dde608f75d3ddf98ad265c735e632855cb0",
    "generator_config_sha256": "a308e701ebd9cf2242dc61826f445d208d8365cd9797e715d92c5ae2d3a00570",
    "generator_source_sha256": "b6b2f1281ed8fc339ceed5e5b5dfe9fb966763b1efd5ef7d9ba1fa5053f067d2",
    "architectures": [
      "raw_native",
      "power_native",
      "raw_ovr",
      "power_ovr"
    ],
    "grid_C": [
      0.1,
      1,
      10,
      100
    ],
    "grid_gamma": [
      0.001,
      0.01,
      0.1,
      1,
      "scale",
      "auto"
    ],
    "calibrations": [
      "sigmoid",
      "isotonic",
      "temperature"
    ],
    "cv": "5-fold training-only macro F1; accuracy also recorded",
    "partitions": {
      "train": 7000,
      "calibration": 750,
      "selection": 750,
      "retired_test": 1500,
      "new_test": 1500
    },
    "selection": "Maximum selection accuracy with macro F1, Manual Review recall and both false-verification counts no worse than raw-native-sigmoid baseline; tie macro F1 then log loss.",
    "release_gate": "Strictly higher fresh accuracy, macro F1 not lower, neither false-verification count higher than saved v2 on same fresh rows. Failure retains v2; no retries.",
    "no_online_learning": true,
    "label_generator_changed": false,
    "fresh_test_generated_after_freeze": true
  }
}
```


---

## ai-service/ml/reports/FILE_INDEX.md

> Current v3 experiment files and results: [v3 summary](../experiments/v3/SUMMARY.md). The entries below include the earlier v2 artifacts; v2 snapshots are preserved under `ml/legacy_v2`.

# Experiment file index

Includes generated outputs, source files, benchmark inputs and preserved historical artifacts.

- [ai-service/ml/audit.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/audit.py>)
- [ai-service/ml/data/benchmarks/lfw_face_match.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/data/benchmarks/lfw_face_match.csv>)
- [ai-service/ml/data/benchmarks/midv_image_quality.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/data/benchmarks/midv_image_quality.csv>)
- [ai-service/ml/data/benchmarks/midv_ocr.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/data/benchmarks/midv_ocr.csv>)
- [ai-service/ml/data/benchmarks/nuaa_liveness.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/data/benchmarks/nuaa_liveness.csv>)
- [ai-service/ml/data/kyc_synthetic_dataset_10000.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/data/kyc_synthetic_dataset_10000.csv>)
- [ai-service/ml/data/kyc_synthetic_dataset_10000.metadata.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/data/kyc_synthetic_dataset_10000.metadata.json>)
- [ai-service/ml/data/synthetic_verification_dataset.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/data/synthetic_verification_dataset.csv>)
- [ai-service/ml/evaluation.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/evaluation.py>)
- [ai-service/ml/generate_dataset.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/generate_dataset.py>)
- [ai-service/ml/generation_config.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/generation_config.json>)
- [ai-service/ml/legacy_v1/evaluation_report.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/legacy_v1/evaluation_report.json>)
- [ai-service/ml/legacy_v1/generate_dataset.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/legacy_v1/generate_dataset.py>)
- [ai-service/ml/legacy_v1/models/model_version.txt](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/legacy_v1/models/model_version.txt>)
- [ai-service/ml/legacy_v1/models/scaler.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/legacy_v1/models/scaler.pkl>)
- [ai-service/ml/legacy_v1/models/svm_kyc_model.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/legacy_v1/models/svm_kyc_model.pkl>)
- [ai-service/ml/legacy_v1/train_model.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/legacy_v1/train_model.py>)
- [ai-service/ml/measure_benchmarks.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/measure_benchmarks.py>)
- [ai-service/ml/models/artifact_manifest.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/models/artifact_manifest.json>)
- [ai-service/ml/models/decision_tree_calibrated.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/models/decision_tree_calibrated.pkl>)
- [ai-service/ml/models/decision_tree_model.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/models/decision_tree_model.pkl>)
- [ai-service/ml/models/identity_only_scaler.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/models/identity_only_scaler.pkl>)
- [ai-service/ml/models/identity_only_svm.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/models/identity_only_svm.pkl>)
- [ai-service/ml/models/model_version.txt](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/models/model_version.txt>)
- [ai-service/ml/models/scaler.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/models/scaler.pkl>)
- [ai-service/ml/models/svm_kyc_model.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/models/svm_kyc_model.pkl>)
- [ai-service/ml/README.md](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/README.md>)
- [ai-service/ml/reporting.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reporting.py>)
- [ai-service/ml/reports/ablation_comparison.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/ablation_comparison.json>)
- [ai-service/ml/reports/benchmark_measurements.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/benchmark_measurements.json>)
- [ai-service/ml/reports/correlation_matrix.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/correlation_matrix.png>)
- [ai-service/ml/reports/decision_tree_calibration.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/decision_tree_calibration.png>)
- [ai-service/ml/reports/decision_tree_confusion_matrix.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/decision_tree_confusion_matrix.png>)
- [ai-service/ml/reports/decision_tree_feature_importance.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/decision_tree_feature_importance.csv>)
- [ai-service/ml/reports/decision_tree_feature_importance.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/decision_tree_feature_importance.png>)
- [ai-service/ml/reports/decision_tree_grid_search.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/decision_tree_grid_search.csv>)
- [ai-service/ml/reports/descriptive_statistics_by_class.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/descriptive_statistics_by_class.csv>)
- [ai-service/ml/reports/distribution_blur_score.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/distribution_blur_score.png>)
- [ai-service/ml/reports/distribution_brightness_score.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/distribution_brightness_score.png>)
- [ai-service/ml/reports/distribution_contrast_score.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/distribution_contrast_score.png>)
- [ai-service/ml/reports/distribution_face_match_score.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/distribution_face_match_score.png>)
- [ai-service/ml/reports/distribution_liveness_score.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/distribution_liveness_score.png>)
- [ai-service/ml/reports/distribution_ocr_confidence_score.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/distribution_ocr_confidence_score.png>)
- [ai-service/ml/reports/distribution_overlap_diagnostics.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/distribution_overlap_diagnostics.json>)
- [ai-service/ml/reports/evaluation_report.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/evaluation_report.json>)
- [ai-service/ml/reports/feature_correlations.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/feature_correlations.csv>)
- [ai-service/ml/reports/FILE_INDEX.md](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/FILE_INDEX.md>)
- [ai-service/ml/reports/frozen_experiment_protocol.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/frozen_experiment_protocol.json>)
- [ai-service/ml/reports/full_svm_calibration.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/full_svm_calibration.png>)
- [ai-service/ml/reports/full_svm_confusion_matrix.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/full_svm_confusion_matrix.png>)
- [ai-service/ml/reports/full_svm_grid_search.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/full_svm_grid_search.csv>)
- [ai-service/ml/reports/identity_only_svm_calibration.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/identity_only_svm_calibration.png>)
- [ai-service/ml/reports/identity_only_svm_confusion_matrix.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/identity_only_svm_confusion_matrix.png>)
- [ai-service/ml/reports/identity_svm_grid_search.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/identity_svm_grid_search.csv>)
- [ai-service/ml/reports/legacy_methodology_audit.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/legacy_methodology_audit.json>)
- [ai-service/ml/reports/split_manifest.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/split_manifest.csv>)
- [ai-service/ml/reports/svm_permutation_importance.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/svm_permutation_importance.csv>)
- [ai-service/ml/reports/svm_permutation_importance.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/svm_permutation_importance.png>)
- [ai-service/ml/reports/TECHNICAL_SUMMARY.md](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/TECHNICAL_SUMMARY.md>)
- [ai-service/ml/reports/verification_checks.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/reports/verification_checks.json>)
- [ai-service/ml/requirements-experiment.lock.txt](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/requirements-experiment.lock.txt>)
- [ai-service/ml/requirements-ml.txt](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/requirements-ml.txt>)
- [ai-service/ml/schema.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/schema.py>)
- [ai-service/ml/train_model.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/train_model.py>)
- [ai-service/notebooks/01_distribution_analysis.ipynb](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/notebooks/01_distribution_analysis.ipynb>)
- [ai-service/notebooks/02_model_training.ipynb](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/notebooks/02_model_training.ipynb>)
- [ai-service/notebooks/03_kyc_experiment_results.ipynb](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/notebooks/03_kyc_experiment_results.ipynb>)
- [ai-service/routes/svmRoutes.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/routes/svmRoutes.py>)
- [ai-service/services/svmService.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/services/svmService.py>)
- [ai-service/tests/test_kyc_experiment.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/tests/test_kyc_experiment.py>)
- [ai-service/tests/test_svm.py](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/tests/test_svm.py>)
- [backend/src/services/accessControlService.js](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/backend/src/services/accessControlService.js>)
- [backend/src/services/verificationService.js](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/backend/src/services/verificationService.js>)
- [backend/tests/kycDecision.test.js](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/backend/tests/kycDecision.test.js>)
- [frontend/src/views/AdminModelEvaluation.vue](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/frontend/src/views/AdminModelEvaluation.vue>)



---

## ai-service/ml/reports/frozen_experiment_protocol.json

```json
{
  "version": "2.0.0",
  "seed": 42,
  "dataset_sha256": "d6dbe75aa5d765e4b3d92112e2825dde608f75d3ddf98ad265c735e632855cb0",
  "full_selection": {
    "best_params": {
      "C": 10,
      "gamma": "scale"
    },
    "cv_macro_f1": 0.6727661071732829,
    "cv_folds": 5,
    "cv_scoring": "f1_macro",
    "candidate_count": 24
  },
  "identity_selection": {
    "best_params": {
      "C": 100,
      "gamma": "auto"
    },
    "cv_macro_f1": 0.675051351254578,
    "cv_folds": 5,
    "cv_scoring": "f1_macro",
    "candidate_count": 24
  },
  "tree_selection": {
    "max_depth": 3,
    "min_samples_leaf": 5
  },
  "calibration": "Sigmoid on validation only, frozen train-only estimators",
  "test_policy": "All generation, hyperparameters, calibration and 6-feature deployment fixed before final test evaluation",
  "frozen_at": "2026-10-02T19:12:47.937094+00:00"
}
```


---

## ai-service/ml/reports/legacy_methodology_audit.json

```json
{
  "records": 4000,
  "counts": {
    "0": 2400,
    "2": 800,
    "1": 800
  },
  "exact_duplicates": 0,
  "conflicting_vectors": 0,
  "train_test_duplicate_vectors": 0,
  "near_duplicate_pairs_within_point005_fixed_range_each_feature": 0,
  "single_feature_tree_training_cv_macro_f1": {
    "faceMatchScore": 0.9586258147244016,
    "livenessScore": 0.9681412188691224,
    "ocrConfidenceScore": 0.9572678335404797,
    "blurScore": 0.9485490021348486,
    "brightnessScore": 0.9551737955634525,
    "contrastScore": 0.9300400950490424
  },
  "findings": [
    "Labels assigned before independent class-specific clipped distributions.",
    "All six feature ranges nearly isolate classes; quality is an artificial class proxy.",
    "Small noise does not remove multivariate separation; old report accuracy=1.",
    "Training script fits scaler on training only, but hard-codes notebook hyperparameters.",
    "Notebook scales all training rows before GridSearchCV: CV-fold preprocessing leakage.",
    "No evidence of direct target column or final test rows passed to model fit in inspected code.",
    "No automatic duplicate or contamination checks; historical test reuse cannot be proven absent.",
    "Benchmark score files exist but old generator does not derive its parameters from them."
  ]
}
```


---

## ai-service/ml/reports/TECHNICAL_SUMMARY.md

# KYC v3 improvement experiment

Production promotion: **True**. Passed predeclared release gate: accuracy increased, macro F1 and both false-verification counts did not worsen.

Both rows below were evaluated on the SAME fresh 1,500 synthetic cases. The original v2 74.33% result used a different test set and must not be used as the before value here.

| Model | Accuracy | Macro F1 | Weighted F1 | Rejected → Verified | Manual Review → Verified |
|---|---:|---:|---:|---:|---:|
| Saved v2 incumbent | 75.733% | 0.651909 | 0.730391 | 44 | 186 |
| Selected v3 candidate | 75.800% | 0.654082 | 0.731979 | 43 | 184 |

Accuracy difference: **0.067 percentage points**.
Paired bootstrap 95% interval: [-0.0013333333333333333, 0.0033333333333333335] (accuracy fraction).
Macro F1 difference: 0.002173; paired interval: [-0.0010511307847866746, 0.006854749742914959].

## Selected model and policy

Candidate: **raw_native_sigmoid**.
Training-only hyperparameters: `{'C': 10, 'gamma': 'scale'}`; CV macro F1: 0.672766.
Policy: probability; review multiplier 1.0; verification threshold 0.0; verification margin 0.0.
All six input features and the generator assumptions were retained. Quality transforms, where selected, are learned inside training folds. Probabilities are unchanged by the decision policy.

| Selection metrics | Accuracy | Macro F1 | Review recall | Rejected → Verified | Review → Verified |
|---|---:|---:|---:|---:|---:|
| Comparable baseline | 0.757333 | 0.659895 | 0.300000 | 29 | 92 |
| Selected candidate | 0.757333 | 0.659895 | 0.300000 | 29 | 92 |

## Fresh per-class results

| Model | Class | Precision | Recall | F1 |
|---|---|---:|---:|---:|
| v2 | Verified | 0.783427 | 0.924444 | 0.848114 |
| v2 | Manual Review | 0.634921 | 0.266667 | 0.375587 |
| v2 | Rejected | 0.717949 | 0.746667 | 0.732026 |
| v3 | Verified | 0.785444 | 0.923333 | 0.848825 |
| v3 | Manual Review | 0.630769 | 0.273333 | 0.381395 |
| v3 | Rejected | 0.717949 | 0.746667 | 0.732026 |

## incumbent confusion matrix

Actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[832, 14, 54]
[186, 80, 34]
[44, 32, 224]
```

## candidate confusion matrix

Actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[831, 15, 54]
[184, 82, 34]
[43, 33, 224]
```

## Probability quality

| Model | Log loss | Multiclass Brier |
|---|---:|---:|
| incumbent | 0.660123 | 0.373659 |
| candidate | 0.659596 | 0.373110 |

## What was compared

Four SVM variants (raw/power quality × native/explicit one-vs-rest), three calibration methods (sigmoid/isotonic/temperature), and native versus validation-selected review policies. Three new 24-point five-fold searches were run; the prior raw-native CV winner was reused with provenance. All policy/calibration variants are in `validation_candidates.csv`.

## Isolation and autonomy

Original train=7,000; calibration=750; selection=750. Original test=1,500 retired. Fresh evaluation=1,500, generated only after selection freeze. Exact and near-duplicate checks cover all 11,500 rows. The test is used once for reported evaluation and a predeclared release acceptance check, not candidate tuning. Training checkpoints allow recovery from implementation errors; completed experiments are not silently rerun. No online learning exists.

## Permutation importance

| Feature | Macro F1 decrease | Repeat SD |
|---|---:|---:|
| liveness_score | 0.201380 | 0.008477 |
| face_match_score | 0.110442 | 0.005995 |
| ocr_confidence_score | 0.049802 | 0.007588 |
| blur_score | 0.003831 | 0.003357 |
| brightness_score | -0.000359 | 0.003924 |
| contrast_score | -0.003439 | 0.003605 |

## Limitations

- Fresh synthetic draw from the SAME assumptions; not independent real-world validation.
- Previously observed v2 results motivated the hypotheses; original test was retired.
- Calibration and selection are disjoint but small (750 each); searching policies can overfit selection.
- Isotonic calibration may overfit small calibration samples; temperature can preserve poor decision rankings.
- Latent review and genuine scenarios can share observed distributions; missing evidence remains irreducible.
- Decision-policy preferences do not change calibrated probability values.
- Quality transform and calibrators are static; no online learning.
- The original data contains observationally identical components with different assumed adjudication outcomes. Their minimum population error contribution is 8%; other overlap can add more.
- Accuracy improvements do not by themselves establish acceptable false-approval rates. Examine the exact counts above.
- Local integration and API checks do not constitute remote Hugging Face deployment or live database validation.

## Files

- [baseline_calibration_diagnostic.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/baseline_calibration_diagnostic.json>)
- [candidate_calibration.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_calibration.png>)
- [candidate_confusion_matrix.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_confusion_matrix.png>)
- [candidate_model.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_model.pkl>)
- [candidate_scaler.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_scaler.pkl>)
- [comparison.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/comparison.png>)
- [development_split_manifest.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/development_split_manifest.csv>)
- [fresh_evaluation_1500.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/fresh_evaluation_1500.csv>)
- [fresh_evaluation_metadata.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/fresh_evaluation_metadata.json>)
- [identifiability_diagnostic.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/identifiability_diagnostic.json>)
- [improvement_report.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/improvement_report.json>)
- [incumbent_calibration.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/incumbent_calibration.png>)
- [incumbent_confusion_matrix.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/incumbent_confusion_matrix.png>)
- [power_native_grid.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_native_grid.csv>)
- [power_native_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_native_training.pkl>)
- [power_ovr_grid.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_ovr_grid.csv>)
- [power_ovr_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_ovr_training.pkl>)
- [protocol.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/protocol.json>)
- [raw_native_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/raw_native_training.pkl>)
- [raw_ovr_grid.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/raw_ovr_grid.csv>)
- [raw_ovr_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/raw_ovr_training.pkl>)
- [README.md](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/README.md>)
- [selection_frozen.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/selection_frozen.json>)
- [svm_permutation_importance.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/svm_permutation_importance.csv>)
- [svm_permutation_importance.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/svm_permutation_importance.png>)
- [validation_candidates.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/validation_candidates.csv>)

- [Runner](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/improve_model.py>)
- [Saved-policy implementation](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/decision_model.py>)



---

## ai-service/ml/reports/verification_checks.json

```json
{
  "status": "passed",
  "python_api_tests": 5,
  "python_experiment_tests": 2,
  "node_contract_tests": 2,
  "checks": [
    "Actual serialized SVM/scaler reload prediction and probability parity",
    "Canonical and legacy API inputs and class mapping",
    "Probability mapping with deliberately reordered classes_",
    "Missing/non-numeric/boolean/non-finite/huge/out-of-range/unknown/duplicate-alias inputs rejected",
    "Unavailable model returns 503",
    "Dataset regeneration matches saved 10000 rows",
    "Split manifest reproduces exactly and saved scaler fits only 7000 training rows",
    "Node incomplete inputs fail before network/fallback",
    "Node preserves decision enums and svm_model basis"
  ],
  "not_executed": [
    "Remote Hugging Face deployment",
    "Live Supabase writes",
    "Full image-processing service integration"
  ],
  "visual_review": [
    "Full SVM confusion matrix",
    "SVM permutation importance",
    "Blur distribution"
  ]
}
```


---

## ai-service/ml/experiments/v3/baseline_calibration_diagnostic.json

```json
{
  "native": {
    "accuracy": 0.712,
    "macro_f1": 0.6411516073841619,
    "rejected_to_verified": 21,
    "review_to_verified": 81,
    "review_recall": 0.37333333333333335
  },
  "sigmoid": {
    "accuracy": 0.7573333333333333,
    "macro_f1": 0.6598946388372183,
    "rejected_to_verified": 29,
    "review_to_verified": 92,
    "review_recall": 0.3
  },
  "isotonic": {
    "accuracy": 0.7573333333333333,
    "macro_f1": 0.6590397908642379,
    "rejected_to_verified": 37,
    "review_to_verified": 98,
    "review_recall": 0.29333333333333333
  },
  "temperature": {
    "accuracy": 0.7133333333333334,
    "macro_f1": 0.6420644361352198,
    "rejected_to_verified": 21,
    "review_to_verified": 81,
    "review_recall": 0.37333333333333335
  }
}
```


---

## ai-service/ml/experiments/v3/fresh_evaluation_metadata.json

```json
{
  "configuration": {
    "seed": 2684470948,
    "class_counts": {
      "Verified": 900,
      "Manual Review": 300,
      "Rejected": 300
    },
    "provenance": "Benchmark moments are computed from existing local measured CSVs. Scenario mixtures, borderline distributions, quality shifts and measurement variation are modelling assumptions, not benchmark results or real fraud prevalence.",
    "face_borderline": [
      45,
      16
    ],
    "face_difficult_impostor": [
      32,
      18
    ],
    "live_borderline": [
      0.65,
      0.17
    ],
    "live_difficult_attack": [
      0.43,
      0.24
    ],
    "ocr_borderline": [
      0.53,
      0.19
    ],
    "ocr_mismatch": [
      0.22,
      0.17
    ],
    "clear_ocr_quantile": 0.5,
    "poor_quality_shift": [
      -0.65,
      -20,
      -7
    ],
    "quality_observation_noise": [
      0.12,
      4,
      2
    ],
    "face_measurement_sd": 3,
    "live_measurement_sd": 0.025,
    "ocr_measurement_sd": 0.04,
    "ocr_quality_penalty": 0.16,
    "quality_logblur_reference": 3.4,
    "quality_contrast_reference": 25,
    "scenarios": {
      "Verified": [
        [
          "consistent_genuine",
          0.7,
          "genuine",
          "real",
          "clear",
          false
        ],
        [
          "genuine_reading_variation",
          0.2,
          "genuine",
          "real",
          "borderline",
          false
        ],
        [
          "genuine_face_variation",
          0.1,
          "borderline",
          "real",
          "clear",
          false
        ]
      ],
      "Manual Review": [
        [
          "uncertain_face",
          0.2,
          "borderline",
          "real",
          "clear",
          false
        ],
        [
          "uncertain_document",
          0.2,
          "genuine",
          "real",
          "borderline",
          false
        ],
        [
          "uncertain_presentation",
          0.2,
          "genuine",
          "borderline",
          "clear",
          false
        ],
        [
          "recapture_needed",
          0.25,
          "genuine",
          "real",
          "clear",
          true
        ],
        [
          "multiple_uncertainties",
          0.15,
          "borderline",
          "borderline",
          "borderline",
          false
        ]
      ],
      "Rejected": [
        [
          "identity_mismatch",
          0.25,
          "impostor",
          "real",
          "clear",
          false
        ],
        [
          "photo_attack",
          0.25,
          "genuine",
          "attack",
          "clear",
          false
        ],
        [
          "document_mismatch",
          0.2,
          "genuine",
          "real",
          "mismatch",
          false
        ],
        [
          "difficult_identity_mismatch",
          0.15,
          "difficult_impostor",
          "real",
          "clear",
          false
        ],
        [
          "difficult_presentation_attack",
          0.15,
          "genuine",
          "difficult_attack",
          "clear",
          false
        ]
      ]
    }
  },
  "measured_sources": {
    "lfw_face_match": {
      "rows": 1000,
      "sha256": "ed82a85dfb6ab74ab338c1d396eb3cb66439a7a10784c12449f408ed5db9f86c"
    },
    "nuaa_liveness": {
      "rows": 1200,
      "sha256": "bbecefd0c98140ec54a8c230c1c4abf1fc57c9faf129056a4d3957e066787e5f"
    },
    "midv_image_quality": {
      "rows": 500,
      "sha256": "c39f918cdc086f0bb02dd4f8406f049121788c03487379a38f025e1e28250326"
    },
    "midv_ocr": {
      "rows": 480,
      "sha256": "5b13defefbef0ddf92df071b0c933e04a1e2ae81cff4542269cdd184da2c25f1"
    }
  },
  "measured_parameters": {
    "face": {
      "genuine": [
        64.81733419999999,
        16.47402134717157
      ],
      "impostor": [
        2.2927294000000003,
        3.5656385254627487
      ]
    },
    "liveness": {
      "photo_attack": [
        0.0199725,
        0.07516618512376493
      ],
      "real": [
        0.9689096666666668,
        0.07043918443874983
      ]
    },
    "ocr_clear_conditional": [
      0.76895625,
      0.1489445240948629
    ],
    "ocr_all": [
      0.45190208333333337,
      0.35222573712218497
    ],
    "quality_transformed_mean": [
      3.7200620127901636,
      171.70002240000002,
      43.2495346
    ],
    "quality_transformed_covariance": [
      [
        0.7211578661338847,
        11.38622734783699,
        0.4879691908211453
      ],
      [
        11.38622734783699,
        2172.433061105429,
        -275.16620785919343
      ],
      [
        0.4879691908211453,
        -275.16620785919343,
        288.27221128831945
      ]
    ]
  },
  "scenario_counts": {
    "consistent_genuine": 660,
    "genuine_reading_variation": 164,
    "genuine_face_variation": 76,
    "uncertain_face": 51,
    "uncertain_document": 55,
    "uncertain_presentation": 49,
    "recapture_needed": 91,
    "multiple_uncertainties": 54,
    "identity_mismatch": 75,
    "photo_attack": 73,
    "document_mismatch": 63,
    "difficult_identity_mismatch": 42,
    "difficult_presentation_attack": 47
  },
  "caveat": "Truncated normals approximate benchmark moments; resulting moments differ after truncation. Joint KYC labels and cross-modality dependencies are assumptions. No benchmark is a joint KYC ground-truth dataset."
}
```


---

## ai-service/ml/experiments/v3/identifiability_diagnostic.json

```json
{
  "shared_components": [
    {
      "observable_component": [
        "genuine",
        "real",
        "borderline",
        false
      ],
      "class_probability_masses": {
        "Verified": 0.12,
        "Manual Review": 0.04000000000000001
      },
      "unavoidable_error_mass": 0.04000000000000001
    },
    {
      "observable_component": [
        "borderline",
        "real",
        "clear",
        false
      ],
      "class_probability_masses": {
        "Verified": 0.06,
        "Manual Review": 0.04000000000000001
      },
      "unavoidable_error_mass": 0.04000000000000001
    }
  ],
  "minimum_population_error_from_identical_components": 0.08000000000000002,
  "maximum_expected_accuracy_bound_from_identical_components": 0.9199999999999999,
  "interpretation": "An upper bound under the configured mixture distribution, not an attainable target or a bound on every finite test realization. Other overlapping components can lower achievable performance further."
}
```


---

## ai-service/ml/experiments/v3/improvement_report.json

```json
{
  "training_timestamp": "2026-10-02T19:52:30+00:00",
  "protocol": {
    "version": "3.0.0",
    "seed": 42,
    "fresh_test_seed": 2684470948,
    "dataset_sha256": "d6dbe75aa5d765e4b3d92112e2825dde608f75d3ddf98ad265c735e632855cb0",
    "generator_config_sha256": "a308e701ebd9cf2242dc61826f445d208d8365cd9797e715d92c5ae2d3a00570",
    "generator_source_sha256": "b6b2f1281ed8fc339ceed5e5b5dfe9fb966763b1efd5ef7d9ba1fa5053f067d2",
    "architectures": [
      "raw_native",
      "power_native",
      "raw_ovr",
      "power_ovr"
    ],
    "grid_C": [
      0.1,
      1,
      10,
      100
    ],
    "grid_gamma": [
      0.001,
      0.01,
      0.1,
      1,
      "scale",
      "auto"
    ],
    "calibrations": [
      "sigmoid",
      "isotonic",
      "temperature"
    ],
    "cv": "5-fold training-only macro F1; accuracy also recorded",
    "partitions": {
      "train": 7000,
      "calibration": 750,
      "selection": 750,
      "retired_test": 1500,
      "new_test": 1500
    },
    "selection": "Maximum selection accuracy with macro F1, Manual Review recall and both false-verification counts no worse than raw-native-sigmoid baseline; tie macro F1 then log loss.",
    "release_gate": "Strictly higher fresh accuracy, macro F1 not lower, neither false-verification count higher than saved v2 on same fresh rows. Failure retains v2; no retries.",
    "no_online_learning": true,
    "label_generator_changed": false,
    "fresh_test_generated_after_freeze": true
  },
  "selected_validation": {
    "candidate": "raw_native_sigmoid",
    "policy": "probability",
    "review_multiplier": 1.0,
    "verified_threshold": 0.0,
    "verified_margin": 0.0,
    "log_loss": 0.703824505781107,
    "accuracy": 0.7573333333333333,
    "macro_f1": 0.6598946388372183,
    "rejected_to_verified": 29,
    "review_to_verified": 92,
    "review_recall": 0.3,
    "eligible": true
  },
  "baseline_validation": {
    "candidate": "raw_native_sigmoid",
    "policy": "probability",
    "review_multiplier": 1.0,
    "verified_threshold": 0.0,
    "verified_margin": 0.0,
    "log_loss": 0.703824505781107,
    "accuracy": 0.7573333333333333,
    "macro_f1": 0.6598946388372183,
    "rejected_to_verified": 29,
    "review_to_verified": 92,
    "review_recall": 0.3
  },
  "selected_training": {
    "best_params": {
      "C": 10,
      "gamma": "scale"
    },
    "cv_macro_f1": 0.6727661071732829,
    "cv_source": "legacy_v2/reports/full_svm_grid_search.csv (same training rows)"
  },
  "calibration_comparisons_on_selection": [
    {
      "candidate": "raw_native_sigmoid",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.703824505781107,
      "accuracy": 0.7573333333333333,
      "macro_f1": 0.6598946388372183,
      "rejected_to_verified": 29,
      "review_to_verified": 92,
      "review_recall": 0.3,
      "eligible": true
    },
    {
      "candidate": "power_ovr_sigmoid",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.6344870828515324,
      "accuracy": 0.7693333333333333,
      "macro_f1": 0.6682672441506302,
      "rejected_to_verified": 39,
      "review_to_verified": 99,
      "review_recall": 0.28,
      "eligible": false
    },
    {
      "candidate": "raw_ovr_sigmoid",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.6375032364611486,
      "accuracy": 0.768,
      "macro_f1": 0.6662635637245465,
      "rejected_to_verified": 38,
      "review_to_verified": 100,
      "review_recall": 0.2733333333333333,
      "eligible": false
    },
    {
      "candidate": "power_ovr_isotonic",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.7631168526626273,
      "accuracy": 0.7653333333333333,
      "macro_f1": 0.655968733184174,
      "rejected_to_verified": 37,
      "review_to_verified": 101,
      "review_recall": 0.24666666666666667,
      "eligible": false
    },
    {
      "candidate": "power_native_sigmoid",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.7003841622072647,
      "accuracy": 0.7613333333333333,
      "macro_f1": 0.6709234102832778,
      "rejected_to_verified": 32,
      "review_to_verified": 91,
      "review_recall": 0.31333333333333335,
      "eligible": false
    },
    {
      "candidate": "raw_ovr_isotonic",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.6870897878019456,
      "accuracy": 0.7613333333333333,
      "macro_f1": 0.655253915797216,
      "rejected_to_verified": 36,
      "review_to_verified": 99,
      "review_recall": 0.25333333333333335,
      "eligible": false
    },
    {
      "candidate": "power_native_isotonic",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.8828513714517578,
      "accuracy": 0.7586666666666667,
      "macro_f1": 0.6662670296195476,
      "rejected_to_verified": 36,
      "review_to_verified": 95,
      "review_recall": 0.3,
      "eligible": false
    },
    {
      "candidate": "raw_native_isotonic",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.6870850919352057,
      "accuracy": 0.7573333333333333,
      "macro_f1": 0.6590397908642379,
      "rejected_to_verified": 37,
      "review_to_verified": 98,
      "review_recall": 0.29333333333333333,
      "eligible": false
    },
    {
      "candidate": "power_ovr_temperature",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.6865418694312816,
      "accuracy": 0.7213333333333334,
      "macro_f1": 0.6538330692129174,
      "rejected_to_verified": 29,
      "review_to_verified": 82,
      "review_recall": 0.37333333333333335,
      "eligible": false
    },
    {
      "candidate": "raw_ovr_temperature",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.6979839328086113,
      "accuracy": 0.7133333333333334,
      "macro_f1": 0.6442904666628403,
      "rejected_to_verified": 27,
      "review_to_verified": 83,
      "review_recall": 0.37333333333333335,
      "eligible": false
    },
    {
      "candidate": "raw_native_temperature",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.7573714533964337,
      "accuracy": 0.7133333333333334,
      "macro_f1": 0.6420644361352198,
      "rejected_to_verified": 21,
      "review_to_verified": 81,
      "review_recall": 0.37333333333333335,
      "eligible": false
    },
    {
      "candidate": "power_native_temperature",
      "policy": "probability",
      "review_multiplier": 1.0,
      "verified_threshold": 0.0,
      "verified_margin": 0.0,
      "log_loss": 0.7590081203204171,
      "accuracy": 0.7106666666666667,
      "macro_f1": 0.6509347792840893,
      "rejected_to_verified": 24,
      "review_to_verified": 76,
      "review_recall": 0.4066666666666667,
      "eligible": false
    }
  ],
  "candidate": {
    "accuracy": 0.758,
    "macro_f1": 0.6540822748664862,
    "weighted_f1": 0.7319794977084515,
    "per_class": {
      "verified": {
        "label": "Verified",
        "precision": 0.7854442344045368,
        "recall": 0.9233333333333333,
        "f1-score": 0.8488253319713994,
        "support": 900.0,
        "f1": 0.8488253319713994
      },
      "review": {
        "label": "Manual Review",
        "precision": 0.6307692307692307,
        "recall": 0.2733333333333333,
        "f1-score": 0.3813953488372093,
        "support": 300.0,
        "f1": 0.3813953488372093
      },
      "rejected": {
        "label": "Rejected",
        "precision": 0.717948717948718,
        "recall": 0.7466666666666667,
        "f1-score": 0.7320261437908496,
        "support": 300.0,
        "f1": 0.7320261437908496
      }
    },
    "classification_report": {
      "Verified": {
        "precision": 0.7854442344045368,
        "recall": 0.9233333333333333,
        "f1-score": 0.8488253319713994,
        "support": 900.0
      },
      "Manual Review": {
        "precision": 0.6307692307692307,
        "recall": 0.2733333333333333,
        "f1-score": 0.3813953488372093,
        "support": 300.0
      },
      "Rejected": {
        "precision": 0.717948717948718,
        "recall": 0.7466666666666667,
        "f1-score": 0.7320261437908496,
        "support": 300.0
      },
      "accuracy": 0.758,
      "macro avg": {
        "precision": 0.7113873943741619,
        "recall": 0.6477777777777778,
        "f1-score": 0.6540822748664862,
        "support": 1500.0
      },
      "weighted avg": {
        "precision": 0.7410101303863119,
        "recall": 0.758,
        "f1-score": 0.7319794977084515,
        "support": 1500.0
      }
    },
    "confusion_matrix": [
      [
        831,
        15,
        54
      ],
      [
        184,
        82,
        34
      ],
      [
        43,
        33,
        224
      ]
    ],
    "confusion_matrix_labels": [
      "Verified",
      "Manual Review",
      "Rejected"
    ],
    "errors": {
      "Verified -> Manual Review": 15,
      "Verified -> Rejected": 54,
      "Manual Review -> Verified": 184,
      "Manual Review -> Rejected": 34,
      "Rejected -> Verified": 43,
      "Rejected -> Manual Review": 33
    },
    "probability_calibration": {
      "log_loss": 0.6595962364683127,
      "multiclass_brier_sum": 0.37311037217127374,
      "brier_definition": "Mean sum of squared errors over 3 classes, range [0,2].",
      "classwise_ece_10_bins": {
        "Verified": 0.027292012128580328,
        "Manual Review": 0.03490072766360113,
        "Rejected": 0.027867448838878903
      },
      "reliability_bins": {
        "Verified": [
          {
            "lower": 0.1,
            "n": 373,
            "mean_probability": 0.13237116444796376,
            "observed_fraction": 0.10723860589812333
          },
          {
            "lower": 0.2,
            "n": 7,
            "mean_probability": 0.20760503259207722,
            "observed_fraction": 0.5714285714285714
          },
          {
            "lower": 0.30000000000000004,
            "n": 43,
            "mean_probability": 0.35341652559394704,
            "observed_fraction": 0.4883720930232558
          },
          {
            "lower": 0.4,
            "n": 40,
            "mean_probability": 0.4782964632889346,
            "observed_fraction": 0.425
          },
          {
            "lower": 0.5,
            "n": 108,
            "mean_probability": 0.5284413222641441,
            "observed_fraction": 0.5833333333333334
          },
          {
            "lower": 0.7000000000000001,
            "n": 84,
            "mean_probability": 0.787173026559391,
            "observed_fraction": 0.7023809523809523
          },
          {
            "lower": 0.8,
            "n": 845,
            "mean_probability": 0.8141645092018396,
            "observed_fraction": 0.8236686390532545
          }
        ],
        "Manual Review": [
          {
            "lower": 0.0,
            "n": 61,
            "mean_probability": 0.0357925064006868,
            "observed_fraction": 0.14754098360655737
          },
          {
            "lower": 0.1,
            "n": 1182,
            "mean_probability": 0.155726175795514,
            "observed_fraction": 0.13959390862944163
          },
          {
            "lower": 0.4,
            "n": 189,
            "mean_probability": 0.4585079170299655,
            "observed_fraction": 0.3968253968253968
          },
          {
            "lower": 0.5,
            "n": 68,
            "mean_probability": 0.5322338488693743,
            "observed_fraction": 0.75
          }
        ],
        "Rejected": [
          {
            "lower": 0.0,
            "n": 1057,
            "mean_probability": 0.0308819242369394,
            "observed_fraction": 0.03784295175023652
          },
          {
            "lower": 0.1,
            "n": 2,
            "mean_probability": 0.19476056556105362,
            "observed_fraction": 0.5
          },
          {
            "lower": 0.2,
            "n": 52,
            "mean_probability": 0.2546563429071712,
            "observed_fraction": 0.21153846153846154
          },
          {
            "lower": 0.30000000000000004,
            "n": 77,
            "mean_probability": 0.35024706267981576,
            "observed_fraction": 0.3116883116883117
          },
          {
            "lower": 0.5,
            "n": 14,
            "mean_probability": 0.5812119706488134,
            "observed_fraction": 0.14285714285714285
          },
          {
            "lower": 0.6000000000000001,
            "n": 33,
            "mean_probability": 0.6315711216998618,
            "observed_fraction": 0.42424242424242425
          },
          {
            "lower": 0.7000000000000001,
            "n": 265,
            "mean_probability": 0.7258757734143855,
            "observed_fraction": 0.7849056603773585
          }
        ]
      }
    }
  },
  "incumbent": {
    "accuracy": 0.7573333333333333,
    "macro_f1": 0.6519090558220101,
    "weighted_f1": 0.7303911011792407,
    "per_class": {
      "verified": {
        "label": "Verified",
        "precision": 0.783427495291902,
        "recall": 0.9244444444444444,
        "f1-score": 0.8481141692150866,
        "support": 900.0,
        "f1": 0.8481141692150866
      },
      "review": {
        "label": "Manual Review",
        "precision": 0.6349206349206349,
        "recall": 0.26666666666666666,
        "f1-score": 0.3755868544600939,
        "support": 300.0,
        "f1": 0.3755868544600939
      },
      "rejected": {
        "label": "Rejected",
        "precision": 0.717948717948718,
        "recall": 0.7466666666666667,
        "f1-score": 0.7320261437908496,
        "support": 300.0,
        "f1": 0.7320261437908496
      }
    },
    "classification_report": {
      "Verified": {
        "precision": 0.783427495291902,
        "recall": 0.9244444444444444,
        "f1-score": 0.8481141692150866,
        "support": 900.0
      },
      "Manual Review": {
        "precision": 0.6349206349206349,
        "recall": 0.26666666666666666,
        "f1-score": 0.3755868544600939,
        "support": 300.0
      },
      "Rejected": {
        "precision": 0.717948717948718,
        "recall": 0.7466666666666667,
        "f1-score": 0.7320261437908496,
        "support": 300.0
      },
      "accuracy": 0.7573333333333333,
      "macro avg": {
        "precision": 0.712098949387085,
        "recall": 0.6459259259259259,
        "f1-score": 0.6519090558220101,
        "support": 1500.0
      },
      "weighted avg": {
        "precision": 0.7406303677490118,
        "recall": 0.7573333333333333,
        "f1-score": 0.7303911011792407,
        "support": 1500.0
      }
    },
    "confusion_matrix": [
      [
        832,
        14,
        54
      ],
      [
        186,
        80,
        34
      ],
      [
        44,
        32,
        224
      ]
    ],
    "confusion_matrix_labels": [
      "Verified",
      "Manual Review",
      "Rejected"
    ],
    "errors": {
      "Verified -> Manual Review": 14,
      "Verified -> Rejected": 54,
      "Manual Review -> Verified": 186,
      "Manual Review -> Rejected": 34,
      "Rejected -> Verified": 44,
      "Rejected -> Manual Review": 32
    },
    "probability_calibration": {
      "log_loss": 0.6601228273209566,
      "multiclass_brier_sum": 0.3736585942269165,
      "brier_definition": "Mean sum of squared errors over 3 classes, range [0,2].",
      "classwise_ece_10_bins": {
        "Verified": 0.04605818648384579,
        "Manual Review": 0.02893870957084166,
        "Rejected": 0.019946703332966546
      },
      "reliability_bins": {
        "Verified": [
          {
            "lower": 0.1,
            "n": 369,
            "mean_probability": 0.14132392213762937,
            "observed_fraction": 0.10569105691056911
          },
          {
            "lower": 0.2,
            "n": 11,
            "mean_probability": 0.2103873415597252,
            "observed_fraction": 0.45454545454545453
          },
          {
            "lower": 0.30000000000000004,
            "n": 40,
            "mean_probability": 0.357584644738419,
            "observed_fraction": 0.475
          },
          {
            "lower": 0.4,
            "n": 43,
            "mean_probability": 0.4737237904038272,
            "observed_fraction": 0.4418604651162791
          },
          {
            "lower": 0.5,
            "n": 108,
            "mean_probability": 0.5269908688230553,
            "observed_fraction": 0.5833333333333334
          },
          {
            "lower": 0.7000000000000001,
            "n": 386,
            "mean_probability": 0.7916884332766136,
            "observed_fraction": 0.7512953367875648
          },
          {
            "lower": 0.8,
            "n": 543,
            "mean_probability": 0.8093746692367777,
            "observed_fraction": 0.856353591160221
          }
        ],
        "Manual Review": [
          {
            "lower": 0.0,
            "n": 61,
            "mean_probability": 0.03802574596337551,
            "observed_fraction": 0.14754098360655737
          },
          {
            "lower": 0.1,
            "n": 1182,
            "mean_probability": 0.15826554121632916,
            "observed_fraction": 0.13959390862944163
          },
          {
            "lower": 0.4,
            "n": 212,
            "mean_probability": 0.454823152123988,
            "observed_fraction": 0.4339622641509434
          },
          {
            "lower": 0.5,
            "n": 45,
            "mean_probability": 0.5281054023990693,
            "observed_fraction": 0.7555555555555555
          }
        ],
        "Rejected": [
          {
            "lower": 0.0,
            "n": 1057,
            "mean_probability": 0.03839666848607127,
            "observed_fraction": 0.03784295175023652
          },
          {
            "lower": 0.2,
            "n": 50,
            "mean_probability": 0.2586822335309646,
            "observed_fraction": 0.22
          },
          {
            "lower": 0.30000000000000004,
            "n": 81,
            "mean_probability": 0.3516948252568875,
            "observed_fraction": 0.30864197530864196
          },
          {
            "lower": 0.5,
            "n": 20,
            "mean_probability": 0.5799132479848949,
            "observed_fraction": 0.15
          },
          {
            "lower": 0.6000000000000001,
            "n": 149,
            "mean_probability": 0.6843161439217018,
            "observed_fraction": 0.738255033557047
          },
          {
            "lower": 0.7000000000000001,
            "n": 143,
            "mean_probability": 0.7253271022940417,
            "observed_fraction": 0.7762237762237763
          }
        ]
      }
    }
  },
  "reference_models": {
    "decision_tree": {
      "accuracy": 0.7566666666666667,
      "macro_f1": 0.6484692669061625,
      "weighted_f1": 0.7268337215269828,
      "per_class": {
        "verified": {
          "label": "Verified",
          "precision": 0.7436548223350253,
          "recall": 0.9766666666666667,
          "f1-score": 0.8443804034582133,
          "support": 900.0,
          "f1": 0.8443804034582133
        },
        "review": {
          "label": "Manual Review",
          "precision": 0.6231884057971014,
          "recall": 0.2866666666666667,
          "f1-score": 0.3926940639269406,
          "support": 300.0,
          "f1": 0.3926940639269406
        },
        "rejected": {
          "label": "Rejected",
          "precision": 0.9444444444444444,
          "recall": 0.5666666666666667,
          "f1-score": 0.7083333333333334,
          "support": 300.0,
          "f1": 0.7083333333333334
        }
      },
      "classification_report": {
        "Verified": {
          "precision": 0.7436548223350253,
          "recall": 0.9766666666666667,
          "f1-score": 0.8443804034582133,
          "support": 900.0
        },
        "Manual Review": {
          "precision": 0.6231884057971014,
          "recall": 0.2866666666666667,
          "f1-score": 0.3926940639269406,
          "support": 300.0
        },
        "Rejected": {
          "precision": 0.9444444444444444,
          "recall": 0.5666666666666667,
          "f1-score": 0.7083333333333334,
          "support": 300.0
        },
        "accuracy": 0.7566666666666667,
        "macro avg": {
          "precision": 0.7704292241921905,
          "recall": 0.61,
          "f1-score": 0.6484692669061625,
          "support": 1500.0
        },
        "weighted avg": {
          "precision": 0.7597194634493244,
          "recall": 0.7566666666666667,
          "f1-score": 0.7268337215269828,
          "support": 1500.0
        }
      },
      "confusion_matrix": [
        [
          879,
          17,
          4
        ],
        [
          208,
          86,
          6
        ],
        [
          95,
          35,
          170
        ]
      ],
      "confusion_matrix_labels": [
        "Verified",
        "Manual Review",
        "Rejected"
      ],
      "errors": {
        "Verified -> Manual Review": 17,
        "Verified -> Rejected": 4,
        "Manual Review -> Verified": 208,
        "Manual Review -> Rejected": 6,
        "Rejected -> Verified": 95,
        "Rejected -> Manual Review": 35
      },
      "probability_calibration": {
        "log_loss": 0.7898361054224619,
        "multiclass_brier_sum": 0.4611110051199686,
        "brier_definition": "Mean sum of squared errors over 3 classes, range [0,2].",
        "classwise_ece_10_bins": {
          "Verified": 0.2053727324212735,
          "Manual Review": 0.1434534504280226,
          "Rejected": 0.06593906338228817
        },
        "reliability_bins": {
          "Verified": [
            {
              "lower": 0.0,
              "n": 318,
              "mean_probability": 0.020403125115870252,
              "observed_fraction": 0.0660377358490566
            },
            {
              "lower": 0.4,
              "n": 1182,
              "mean_probability": 0.4953068592057893,
              "observed_fraction": 0.7436548223350253
            }
          ],
          "Manual Review": [
            {
              "lower": 0.0,
              "n": 171,
              "mean_probability": 0.01895028652680166,
              "observed_fraction": 0.017543859649122806
            },
            {
              "lower": 0.1,
              "n": 9,
              "mean_probability": 0.1458333333333333,
              "observed_fraction": 0.3333333333333333
            },
            {
              "lower": 0.30000000000000004,
              "n": 1182,
              "mean_probability": 0.3451263537905948,
              "observed_fraction": 0.17597292724196278
            },
            {
              "lower": 0.5,
              "n": 1,
              "mean_probability": 0.5714285714285715,
              "observed_fraction": 0.0
            },
            {
              "lower": 0.7000000000000001,
              "n": 137,
              "mean_probability": 0.7207401306134249,
              "observed_fraction": 0.6277372262773723
            }
          ],
          "Rejected": [
            {
              "lower": 0.1,
              "n": 1182,
              "mean_probability": 0.15956678700359914,
              "observed_fraction": 0.08037225042301184
            },
            {
              "lower": 0.2,
              "n": 137,
              "mean_probability": 0.24265760970541023,
              "observed_fraction": 0.24817518248175183
            },
            {
              "lower": 0.4,
              "n": 1,
              "mean_probability": 0.4285714285714286,
              "observed_fraction": 1.0
            },
            {
              "lower": 0.8,
              "n": 9,
              "mean_probability": 0.8541666666666663,
              "observed_fraction": 0.6666666666666666
            },
            {
              "lower": 0.9,
              "n": 171,
              "mean_probability": 0.9724316771543315,
              "observed_fraction": 0.9590643274853801
            }
          ]
        }
      }
    },
    "identity_only": {
      "accuracy": 0.7486666666666667,
      "macro_f1": 0.664889976691769,
      "weighted_f1": 0.7338079355948933,
      "per_class": {
        "verified": {
          "label": "Verified",
          "precision": 0.7938247011952191,
          "recall": 0.8855555555555555,
          "f1-score": 0.8371848739495799,
          "support": 900.0,
          "f1": 0.8371848739495799
        },
        "review": {
          "label": "Manual Review",
          "precision": 0.533678756476684,
          "recall": 0.3433333333333333,
          "f1-score": 0.4178498985801217,
          "support": 300.0,
          "f1": 0.4178498985801217
        },
        "rejected": {
          "label": "Rejected",
          "precision": 0.735973597359736,
          "recall": 0.7433333333333333,
          "f1-score": 0.7396351575456053,
          "support": 300.0,
          "f1": 0.7396351575456053
        }
      },
      "classification_report": {
        "Verified": {
          "precision": 0.7938247011952191,
          "recall": 0.8855555555555555,
          "f1-score": 0.8371848739495799,
          "support": 900.0
        },
        "Manual Review": {
          "precision": 0.533678756476684,
          "recall": 0.3433333333333333,
          "f1-score": 0.4178498985801217,
          "support": 300.0
        },
        "Rejected": {
          "precision": 0.735973597359736,
          "recall": 0.7433333333333333,
          "f1-score": 0.7396351575456053,
          "support": 300.0
        },
        "accuracy": 0.7486666666666667,
        "macro avg": {
          "precision": 0.6878256850105463,
          "recall": 0.6574074074074074,
          "f1-score": 0.664889976691769,
          "support": 1500.0
        },
        "weighted avg": {
          "precision": 0.7302252914844154,
          "recall": 0.7486666666666667,
          "f1-score": 0.7338079355948933,
          "support": 1500.0
        }
      },
      "confusion_matrix": [
        [
          797,
          51,
          52
        ],
        [
          169,
          103,
          28
        ],
        [
          38,
          39,
          223
        ]
      ],
      "confusion_matrix_labels": [
        "Verified",
        "Manual Review",
        "Rejected"
      ],
      "errors": {
        "Verified -> Manual Review": 51,
        "Verified -> Rejected": 52,
        "Manual Review -> Verified": 169,
        "Manual Review -> Rejected": 28,
        "Rejected -> Verified": 38,
        "Rejected -> Manual Review": 39
      },
      "probability_calibration": {
        "log_loss": 0.6678011098622052,
        "multiclass_brier_sum": 0.3771314753056631,
        "brier_definition": "Mean sum of squared errors over 3 classes, range [0,2].",
        "classwise_ece_10_bins": {
          "Verified": 0.04416404410508559,
          "Manual Review": 0.03426952825048753,
          "Rejected": 0.019801733195630652
        },
        "reliability_bins": {
          "Verified": [
            {
              "lower": 0.1,
              "n": 387,
              "mean_probability": 0.13088064593403737,
              "observed_fraction": 0.11369509043927649
            },
            {
              "lower": 0.2,
              "n": 1,
              "mean_probability": 0.20360268677754298,
              "observed_fraction": 1.0
            },
            {
              "lower": 0.30000000000000004,
              "n": 34,
              "mean_probability": 0.35533405865873896,
              "observed_fraction": 0.4117647058823529
            },
            {
              "lower": 0.4,
              "n": 91,
              "mean_probability": 0.4570978157458643,
              "observed_fraction": 0.6043956043956044
            },
            {
              "lower": 0.5,
              "n": 8,
              "mean_probability": 0.5300316591260148,
              "observed_fraction": 0.75
            },
            {
              "lower": 0.7000000000000001,
              "n": 525,
              "mean_probability": 0.7945248599773965,
              "observed_fraction": 0.7523809523809524
            },
            {
              "lower": 0.8,
              "n": 454,
              "mean_probability": 0.8048660355064335,
              "observed_fraction": 0.8480176211453745
            }
          ],
          "Manual Review": [
            {
              "lower": 0.0,
              "n": 36,
              "mean_probability": 0.025608890631163613,
              "observed_fraction": 0.25
            },
            {
              "lower": 0.1,
              "n": 1254,
              "mean_probability": 0.15941765249372997,
              "observed_fraction": 0.14513556618819776
            },
            {
              "lower": 0.4,
              "n": 58,
              "mean_probability": 0.4844282254518758,
              "observed_fraction": 0.25862068965517243
            },
            {
              "lower": 0.5,
              "n": 149,
              "mean_probability": 0.5360859142390768,
              "observed_fraction": 0.610738255033557
            },
            {
              "lower": 0.6000000000000001,
              "n": 3,
              "mean_probability": 0.6011865477568533,
              "observed_fraction": 1.0
            }
          ],
          "Rejected": [
            {
              "lower": 0.0,
              "n": 1068,
              "mean_probability": 0.0414336659928485,
              "observed_fraction": 0.03838951310861423
            },
            {
              "lower": 0.2,
              "n": 38,
              "mean_probability": 0.26979978756067996,
              "observed_fraction": 0.2631578947368421
            },
            {
              "lower": 0.30000000000000004,
              "n": 91,
              "mean_probability": 0.3337719204316382,
              "observed_fraction": 0.2857142857142857
            },
            {
              "lower": 0.5,
              "n": 12,
              "mean_probability": 0.5847293690419866,
              "observed_fraction": 0.08333333333333333
            },
            {
              "lower": 0.6000000000000001,
              "n": 136,
              "mean_probability": 0.6846155410688669,
              "observed_fraction": 0.7941176470588235
            },
            {
              "lower": 0.7000000000000001,
              "n": 155,
              "mean_probability": 0.7295692323654134,
              "observed_fraction": 0.7354838709677419
            }
          ]
        }
      }
    }
  },
  "accuracy_difference": 0.0006666666666667043,
  "macro_f1_difference": 0.0021732190444760935,
  "paired_uncertainty": {
    "paired_bootstrap_macro_f1_difference_95_percent_interval": [
      -0.0010511307847866746,
      0.006854749742914959
    ],
    "bootstrap_repeats": 1000,
    "caveat": "Conditional on this fitted pair and synthetic population; not real-world or training-seed uncertainty.",
    "accuracy_difference_95_percent_interval": [
      -0.0013333333333333333,
      0.0033333333333333335
    ]
  },
  "permutation_importance": [
    {
      "feature": "face_match_score",
      "importance": 0.11044218744418285,
      "std": 0.0059948739786623234
    },
    {
      "feature": "liveness_score",
      "importance": 0.2013802958956386,
      "std": 0.008477352561759405
    },
    {
      "feature": "ocr_confidence_score",
      "importance": 0.049801803680355784,
      "std": 0.00758782838611898
    },
    {
      "feature": "blur_score",
      "importance": 0.0038308071117566012,
      "std": 0.0033569902461075035
    },
    {
      "feature": "brightness_score",
      "importance": -0.0003592163421191286,
      "std": 0.00392406430600547
    },
    {
      "feature": "contrast_score",
      "importance": -0.0034394830448940873,
      "std": 0.0036047996188125465
    }
  ],
  "duplicate_diagnostics": {
    "combined_rows": 11500,
    "exact_duplicate_vectors": 0,
    "near_duplicate_pairs": 0,
    "definition": "All differences <= face .1, live .001, OCR .001, log1p(blur) .01, brightness .1, contrast .1"
  },
  "fresh_dataset_sha256": "00e0710d7d564c5595e3b0697e8f7abf5a4e49c3119f4f05e00acc2cdce79606",
  "limitations": [
    "Fresh synthetic draw from the SAME assumptions; not independent real-world validation.",
    "Previously observed v2 results motivated the hypotheses; original test was retired.",
    "Calibration and selection are disjoint but small (750 each); searching policies can overfit selection.",
    "Isotonic calibration may overfit small calibration samples; temperature can preserve poor decision rankings.",
    "Latent review and genuine scenarios can share observed distributions; missing evidence remains irreducible.",
    "Decision-policy preferences do not change calibrated probability values.",
    "Quality transform and calibrators are static; no online learning."
  ],
  "promotion": {
    "promoted": true,
    "reason": "Passed predeclared release gate: accuracy increased, macro F1 and both false-verification counts did not worsen."
  }
}
```


---

## ai-service/ml/experiments/v3/protocol.json

```json
{
  "version": "3.0.0",
  "seed": 42,
  "fresh_test_seed": 2684470948,
  "dataset_sha256": "d6dbe75aa5d765e4b3d92112e2825dde608f75d3ddf98ad265c735e632855cb0",
  "generator_config_sha256": "a308e701ebd9cf2242dc61826f445d208d8365cd9797e715d92c5ae2d3a00570",
  "generator_source_sha256": "b6b2f1281ed8fc339ceed5e5b5dfe9fb966763b1efd5ef7d9ba1fa5053f067d2",
  "architectures": [
    "raw_native",
    "power_native",
    "raw_ovr",
    "power_ovr"
  ],
  "grid_C": [
    0.1,
    1,
    10,
    100
  ],
  "grid_gamma": [
    0.001,
    0.01,
    0.1,
    1,
    "scale",
    "auto"
  ],
  "calibrations": [
    "sigmoid",
    "isotonic",
    "temperature"
  ],
  "cv": "5-fold training-only macro F1; accuracy also recorded",
  "partitions": {
    "train": 7000,
    "calibration": 750,
    "selection": 750,
    "retired_test": 1500,
    "new_test": 1500
  },
  "selection": "Maximum selection accuracy with macro F1, Manual Review recall and both false-verification counts no worse than raw-native-sigmoid baseline; tie macro F1 then log loss.",
  "release_gate": "Strictly higher fresh accuracy, macro F1 not lower, neither false-verification count higher than saved v2 on same fresh rows. Failure retains v2; no retries.",
  "no_online_learning": true,
  "label_generator_changed": false,
  "fresh_test_generated_after_freeze": true
}
```


---

## ai-service/ml/experiments/v3/README.md

# Automated offline KYC improvement experiment (v3)

Run from the repository root using the existing locked environment:

```powershell
.\.venv-kyc\Scripts\python.exe ai-service/ml/improve_model.py --jobs 3 --promote
```

The runner saves resumable training checkpoints and refuses to rerun a completed
experiment against the same evaluation draw. Inspect `improvement_report.json`
after completion. Do not delete it to try different models on the same test set.
Reproducing this exact experiment in a clean copy is valid; its evaluation is
then reproduction, not a newly unseen test. Source modules `ml.decision_model`
and their matching scikit-learn runtime must accompany the pickled v3 model.

## What is automated

- Reuse the original 7,000 training rows and unchanged labels.
- Fit three additional 24-candidate RBF SVM grids with five-fold training CV.
- Compare native multiclass SVC with explicit OneVsRest SVC using continuous
  binary margins. Every underlying SVC keeps balanced classes and seed 42.
- Compare raw features with a training-fitted Yeo–Johnson quality transform.
  The latter normalizes skewed quality distributions, then uses MinMaxScaler.
  Six input columns and their order remain unchanged; identity columns are
  untouched by the quality transformation. All fitted transforms stay inside CV.
- Reuse the original raw-native grid winner, with recorded dataset-hash and
  training-CV provenance; do not repeat that already completed search.
- Divide the original 1,500 validation rows into 750 calibration and 750 selection
  rows, stratified with seed 42. Each has 450 Verified, 150 Review, 150 Rejected.
- Fit sigmoid, isotonic and temperature calibrators on calibration rows only.
  Isotonic has a particular overfitting risk at this sample size; its independent
  selection metrics are retained rather than assuming it is superior.
- Compare native classifier decisions and probability-based review policies.
  Policy candidates vary a review preference multiplier, verification confidence
  threshold and verification margin. These are empirically selected decision
  parameters, not manual feature weights. They never alter returned probabilities.
- Select the highest validation accuracy among candidates whose macro F1,
  Manual Review recall and both false-verification counts are no worse than a
  raw-native-sigmoid comparator calibrated on the same 750 calibration rows.
- Freeze the candidate, then draw one fresh 1,500-row synthetic evaluation set
  (900/300/300). Its independent seed comes from NumPy SeedSequence(42).
- Audit duplicates against all 10,000 original rows, then evaluate the frozen
  candidate and saved v2 incumbent on identical fresh rows. Also record the
  saved tree and identity-only models as descriptive references, not candidates.
- Report paired bootstrap intervals, calibration diagnostics and permutation
  importance. A predeclared release check requires higher fresh accuracy,
  non-decreasing macro F1, and no increase in either false-verification count.
  Failure leaves v2 active; it does not trigger retuning or candidate switching.

## What this experiment can establish

This is a model/decision-policy comparison under an unchanged simulator. It does
not improve accuracy by changing labels or making class distributions easier.
The original test set is retired because its outcomes informed the new research
questions. It is neither training data nor selection data here. The fresh test
is generated only after candidate selection. The release check uses it once for
acceptance, not tuning; report that distinction when presenting promoted models.

The existing simulator intentionally contains some observationally identical
Verified and Manual Review components. Their missing adjudication information
cannot be recovered by a more powerful classifier. Better score modelling and
calibration may improve measured performance, but high accuracy is not promised.

A better score on the fresh set demonstrates improvement only for the same
synthetic assumptions. It does not establish real-world KYC performance. The
bootstrap interval describes these fitted models on this simulated population,
not uncertainty over all possible training data or operational conditions.

## Deployment contract

The model remains static after training; there is no online learning or automatic
retraining when KYC completes. `svmService` now calls the saved model's `predict`
method so a learned review policy is honored. It still returns the classifier's
unchanged class probabilities, `decisionBasis=svm_model`, and model version. A
new optional `decisionPolicy` object explains whether the decision used native
boundaries or calibrated-probability review parameters. The Node/Supabase enum
contract and fallback provenance remain unchanged.

Prior v2 artifacts and reports are preserved under `ml/legacy_v2`. If promoted,
the new SVM and raw MinMaxScaler replace the production pair; the fitted quality
transform is packaged inside the model. No remote Hugging Face publication or
live database writes are performed by this experiment.



---

## ai-service/ml/experiments/v3/selection_frozen.json

```json
{
  "selected": {
    "candidate": "raw_native_sigmoid",
    "policy": "probability",
    "review_multiplier": 1.0,
    "verified_threshold": 0.0,
    "verified_margin": 0.0,
    "log_loss": 0.703824505781107,
    "accuracy": 0.7573333333333333,
    "macro_f1": 0.6598946388372183,
    "rejected_to_verified": 29,
    "review_to_verified": 92,
    "review_recall": 0.3,
    "eligible": true
  },
  "baseline": {
    "candidate": "raw_native_sigmoid",
    "policy": "probability",
    "review_multiplier": 1.0,
    "verified_threshold": 0.0,
    "verified_margin": 0.0,
    "log_loss": 0.703824505781107,
    "accuracy": 0.7573333333333333,
    "macro_f1": 0.6598946388372183,
    "rejected_to_verified": 29,
    "review_to_verified": 92,
    "review_recall": 0.3
  },
  "training": {
    "best_params": {
      "C": 10,
      "gamma": "scale"
    },
    "cv_macro_f1": 0.6727661071732829,
    "cv_source": "legacy_v2/reports/full_svm_grid_search.csv (same training rows)"
  },
  "frozen_at": "2026-10-02T19:51:36.107832+00:00"
}
```


---

## ai-service/ml/experiments/v3/SUMMARY.md

# KYC v3 improvement experiment

Production promotion: **True**. Passed predeclared release gate: accuracy increased, macro F1 and both false-verification counts did not worsen.

Both rows below were evaluated on the SAME fresh 1,500 synthetic cases. The original v2 74.33% result used a different test set and must not be used as the before value here.

| Model | Accuracy | Macro F1 | Weighted F1 | Rejected → Verified | Manual Review → Verified |
|---|---:|---:|---:|---:|---:|
| Saved v2 incumbent | 75.733% | 0.651909 | 0.730391 | 44 | 186 |
| Selected v3 candidate | 75.800% | 0.654082 | 0.731979 | 43 | 184 |

Accuracy difference: **0.067 percentage points**.
Paired bootstrap 95% interval: [-0.0013333333333333333, 0.0033333333333333335] (accuracy fraction).
Macro F1 difference: 0.002173; paired interval: [-0.0010511307847866746, 0.006854749742914959].

## Selected model and policy

Candidate: **raw_native_sigmoid**.
Training-only hyperparameters: `{'C': 10, 'gamma': 'scale'}`; CV macro F1: 0.672766.
Policy: probability; review multiplier 1.0; verification threshold 0.0; verification margin 0.0.
All six input features and the generator assumptions were retained. Quality transforms, where selected, are learned inside training folds. Probabilities are unchanged by the decision policy.

| Selection metrics | Accuracy | Macro F1 | Review recall | Rejected → Verified | Review → Verified |
|---|---:|---:|---:|---:|---:|
| Comparable baseline | 0.757333 | 0.659895 | 0.300000 | 29 | 92 |
| Selected candidate | 0.757333 | 0.659895 | 0.300000 | 29 | 92 |

## Fresh per-class results

| Model | Class | Precision | Recall | F1 |
|---|---|---:|---:|---:|
| v2 | Verified | 0.783427 | 0.924444 | 0.848114 |
| v2 | Manual Review | 0.634921 | 0.266667 | 0.375587 |
| v2 | Rejected | 0.717949 | 0.746667 | 0.732026 |
| v3 | Verified | 0.785444 | 0.923333 | 0.848825 |
| v3 | Manual Review | 0.630769 | 0.273333 | 0.381395 |
| v3 | Rejected | 0.717949 | 0.746667 | 0.732026 |

## incumbent confusion matrix

Actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[832, 14, 54]
[186, 80, 34]
[44, 32, 224]
```

## candidate confusion matrix

Actual rows / predicted columns; order Verified, Manual Review, Rejected.

```text
[831, 15, 54]
[184, 82, 34]
[43, 33, 224]
```

## Probability quality

| Model | Log loss | Multiclass Brier |
|---|---:|---:|
| incumbent | 0.660123 | 0.373659 |
| candidate | 0.659596 | 0.373110 |

## What was compared

Four SVM variants (raw/power quality × native/explicit one-vs-rest), three calibration methods (sigmoid/isotonic/temperature), and native versus validation-selected review policies. Three new 24-point five-fold searches were run; the prior raw-native CV winner was reused with provenance. All policy/calibration variants are in `validation_candidates.csv`.

## Isolation and autonomy

Original train=7,000; calibration=750; selection=750. Original test=1,500 retired. Fresh evaluation=1,500, generated only after selection freeze. Exact and near-duplicate checks cover all 11,500 rows. The test is used once for reported evaluation and a predeclared release acceptance check, not candidate tuning. Training checkpoints allow recovery from implementation errors; completed experiments are not silently rerun. No online learning exists.

## Permutation importance

| Feature | Macro F1 decrease | Repeat SD |
|---|---:|---:|
| liveness_score | 0.201380 | 0.008477 |
| face_match_score | 0.110442 | 0.005995 |
| ocr_confidence_score | 0.049802 | 0.007588 |
| blur_score | 0.003831 | 0.003357 |
| brightness_score | -0.000359 | 0.003924 |
| contrast_score | -0.003439 | 0.003605 |

## Limitations

- Fresh synthetic draw from the SAME assumptions; not independent real-world validation.
- Previously observed v2 results motivated the hypotheses; original test was retired.
- Calibration and selection are disjoint but small (750 each); searching policies can overfit selection.
- Isotonic calibration may overfit small calibration samples; temperature can preserve poor decision rankings.
- Latent review and genuine scenarios can share observed distributions; missing evidence remains irreducible.
- Decision-policy preferences do not change calibrated probability values.
- Quality transform and calibrators are static; no online learning.
- The original data contains observationally identical components with different assumed adjudication outcomes. Their minimum population error contribution is 8%; other overlap can add more.
- Accuracy improvements do not by themselves establish acceptable false-approval rates. Examine the exact counts above.
- Local integration and API checks do not constitute remote Hugging Face deployment or live database validation.

## Files

- [baseline_calibration_diagnostic.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/baseline_calibration_diagnostic.json>)
- [candidate_calibration.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_calibration.png>)
- [candidate_confusion_matrix.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_confusion_matrix.png>)
- [candidate_model.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_model.pkl>)
- [candidate_scaler.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/candidate_scaler.pkl>)
- [comparison.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/comparison.png>)
- [development_split_manifest.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/development_split_manifest.csv>)
- [fresh_evaluation_1500.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/fresh_evaluation_1500.csv>)
- [fresh_evaluation_metadata.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/fresh_evaluation_metadata.json>)
- [identifiability_diagnostic.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/identifiability_diagnostic.json>)
- [improvement_report.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/improvement_report.json>)
- [incumbent_calibration.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/incumbent_calibration.png>)
- [incumbent_confusion_matrix.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/incumbent_confusion_matrix.png>)
- [power_native_grid.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_native_grid.csv>)
- [power_native_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_native_training.pkl>)
- [power_ovr_grid.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_ovr_grid.csv>)
- [power_ovr_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/power_ovr_training.pkl>)
- [protocol.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/protocol.json>)
- [raw_native_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/raw_native_training.pkl>)
- [raw_ovr_grid.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/raw_ovr_grid.csv>)
- [raw_ovr_training.pkl](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/raw_ovr_training.pkl>)
- [README.md](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/README.md>)
- [selection_frozen.json](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/selection_frozen.json>)
- [svm_permutation_importance.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/svm_permutation_importance.csv>)
- [svm_permutation_importance.png](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/svm_permutation_importance.png>)
- [validation_candidates.csv](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/experiments/v3/validation_candidates.csv>)

- [Runner](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/improve_model.py>)
- [Saved-policy implementation](<C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/ai-service/ml/decision_model.py>)



---

## ai-service/ml/experiments/v3/verification_checks.json

```json
[
  {
    "test": "test_svm.py",
    "exit_code": 0,
    "output": "test_class_probability_order_is_not_assumed (__main__.SVMContractTests.test_class_probability_order_is_not_assumed) ... ok\ntest_rejects_missing_malformed_nonfinite_out_of_range (__main__.SVMContractTests.test_rejects_missing_malformed_nonfinite_out_of_range) ... ok\ntest_saved_artifact_prediction_parity_and_legacy_contract (__main__.SVMContractTests.test_saved_artifact_prediction_parity_and_legacy_contract) ... ok\ntest_saved_review_policy_is_honored_without_rewriting_probabilities (__main__.SVMContractTests.test_saved_review_policy_is_honored_without_rewriting_probabilities) ... ok\ntest_sharp_image_valid_without_assumed_decision (__main__.SVMContractTests.test_sharp_image_valid_without_assumed_decision) ... ok\ntest_unavailable_has_no_silent_prediction (__main__.SVMContractTests.test_unavailable_has_no_silent_prediction) ... ok\n\n----------------------------------------------------------------------\nRan 6 tests in 0.677s\n\nOK\n"
  },
  {
    "test": "test_kyc_experiment.py",
    "exit_code": 0,
    "output": "test_saved_dataset_is_reproducible_and_has_no_hidden_predictors (__main__.ExperimentTests.test_saved_dataset_is_reproducible_and_has_no_hidden_predictors) ... ok\ntest_split_manifest_and_scaler_only_fit_training (__main__.ExperimentTests.test_split_manifest_and_scaler_only_fit_training) ... ok\n\n----------------------------------------------------------------------\nRan 2 tests in 1.125s\n\nOK\n"
  },
  {
    "test": "test_kyc_improvement.py",
    "exit_code": 0,
    "output": "test_native_boundary_can_differ_from_probability_argmax (__main__.ImprovementTests.test_native_boundary_can_differ_from_probability_argmax) ... ok\ntest_probability_column_order_and_margin (__main__.ImprovementTests.test_probability_column_order_and_margin) ... ok\ntest_quality_transform_preserves_identity_columns_and_fitted_state (__main__.ImprovementTests.test_quality_transform_preserves_identity_columns_and_fitted_state) ... ok\ntest_review_policy_changes_decision_without_changing_probability (__main__.ImprovementTests.test_review_policy_changes_decision_without_changing_probability) ... ok\n\n----------------------------------------------------------------------\nRan 4 tests in 0.162s\n\nOK\n"
  },
  {
    "test": "backend/tests/kycDecision.test.js",
    "exit_code": 0,
    "output": "\u00e2\u0153\u201d Incomplete scores fail before inference or threshold fallback (6.7918ms)\n\u00e2\u0153\u201d Model prediction preserves database enums and decision basis (13.6958ms)\n\u00e2\u201e\u00b9 tests 2\n\u00e2\u201e\u00b9 suites 0\n\u00e2\u201e\u00b9 pass 2\n\u00e2\u201e\u00b9 fail 0\n\u00e2\u201e\u00b9 cancelled 0\n\u00e2\u201e\u00b9 skipped 0\n\u00e2\u201e\u00b9 todo 0\n\u00e2\u201e\u00b9 duration_ms 2550.3257\n"
  }
]
```


---

## ai-service/ml/models/artifact_manifest.json

```json
{
  "version": "3.0.0",
  "features": [
    "face_match_score",
    "liveness_score",
    "ocr_confidence_score",
    "blur_score",
    "brightness_score",
    "contrast_score"
  ],
  "classes": [
    "Manual Review",
    "Rejected",
    "Verified"
  ],
  "library_versions": {
    "scikit-learn": "1.9.0",
    "numpy": "2.5.3",
    "scipy": "1.18.1",
    "pandas": "3.0.6",
    "joblib": "1.6.0",
    "matplotlib": "3.11.2",
    "flask": "3.1.3"
  },
  "dataset_sha256": "d6dbe75aa5d765e4b3d92112e2825dde608f75d3ddf98ad265c735e632855cb0",
  "artifacts": {
    "decision_tree_calibrated.pkl": "7bbb16dcbb85ce8bd2d1d4071f40781a4414d2c869554ccbd382118e2680cb85",
    "decision_tree_model.pkl": "2d864bb79936e778602be9c1bc9ec559dd3e4370d39093172b223b64446d58eb",
    "identity_only_scaler.pkl": "969438a416da02345fcfdb99e01f632b8c1c21e26b0fe6fc7ed60ca20fbf9abe",
    "identity_only_svm.pkl": "b55e0d80615c074bb90e068cec7ca1f71d5758a0ccdadd92046d781a5af47a44",
    "scaler.pkl": "30eefb02ca9d4463e915ded112256880e4f6df4884662e34b4ed4e3e9abf9da6",
    "svm_kyc_model.pkl": "df2d9f20d0f74440254967d8e1084ac301d8d862599fff133c8930a443304912"
  },
  "decision_policy": {
    "name": "probability",
    "review_multiplier": 1.0,
    "verified_threshold": 0.0,
    "verified_margin": 0.0
  }
}
```


---

## ai-service/ml/models/model_version.txt

```txt
3.0.0
trained_at=2026-10-02T19:52:30+00:00

```


---

## ai-service/ml/legacy_v1/evaluation_report.json

```json
{
  "model_version": "1.0.0",
  "training_date": "2026-09-24T19:47:25+00:00",
  "dataset_size": 4000,
  "split_sizes": {
    "train": 2800,
    "validation": 600,
    "test": 600
  },
  "accuracy": 1.0,
  "macro_f1": 1.0,
  "weighted_f1": 1.0,
  "per_class": {
    "verified": {
      "label": "Verified",
      "precision": 1.0,
      "recall": 1.0,
      "f1": 1.0,
      "support": 360
    },
    "review": {
      "label": "Manual Review",
      "precision": 1.0,
      "recall": 1.0,
      "f1": 1.0,
      "support": 120
    },
    "rejected": {
      "label": "Rejected",
      "precision": 1.0,
      "recall": 1.0,
      "f1": 1.0,
      "support": 120
    }
  },
  "confusion_matrix": [
    [
      360,
      0,
      0
    ],
    [
      0,
      120,
      0
    ],
    [
      0,
      0,
      120
    ]
  ],
  "confusion_matrix_labels": [
    "verified",
    "review",
    "rejected"
  ],
  "best_params": {
    "C": 0.1,
    "gamma": 0.1
  },
  "kernel": "rbf",
  "features": [
    "faceMatchScore",
    "livenessScore",
    "ocrConfidenceScore",
    "blurScore",
    "brightnessScore",
    "contrastScore"
  ]
}
```


---

## documentation/final_draft_evidence/backend.json

```json
{
  "suite": "backend",
  "command": [
    "C:\\Users\\ikari\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\bin\\node.exe",
    "--test",
    "backend/tests/kycDecision.test.js",
    "backend/tests/documentRetention.test.js",
    "backend/tests/passkeys.test.js",
    "backend/tests/passkeyRoutes.test.js",
    "backend/tests/passkeyDatabase.test.js"
  ],
  "exit_code": 0,
  "output": "\u2714 three full Nairobi business days skip weekends and cross months (12.3686ms)\n\u2714 window uses successful decision time and closes exactly at expiry (1.0733ms)\n\u2714 purges expired and superseded images while preserving metadata and newer uploads (3.0108ms)\n\u2714 does not delete files inside the window or for pending/review/rejected requests (0.4756ms)\n\u2714 failed storage deletion preserves file references for retry (0.8565ms)\n\u2714 Incomplete scores fail before inference or threshold fallback (7.155ms)\n\u2714 Model prediction preserves database enums and decision basis (71.2427ms)\n\u2714 PostgreSQL migration enforces replay, privileges, rate limits, uniqueness, scoping and last-method protection (4047.405ms)\n[fraudConfig] Missing env vars (using defaults): FRAUD_MAX_FAILED_ATTEMPTS_PER_IP, FRAUD_MAX_FAILED_ATTEMPTS_PER_DEVICE, FRAUD_LOOKBACK_HOURS\n\u2714 HTTP endpoints enforce origin, auth, complete profile, generic failures and rate limits (1308.7031ms)\n(node:4916) ExperimentalWarning: The supports Web Crypto API method is an experimental feature and might change at any time\n(Use `node --trace-warnings ...` to show where the warning was created)\n(node:4916) ExperimentalWarning: The ML-DSA-44 Web Crypto API algorithm is an experimental feature and might change at any time\n\u2714 origin config fails closed and allows only HTTPS or localhost (4.1288ms)\n\u2714 options have random 32-byte challenges, discoverable login, UV, opaque handle, exclusion and attachment policy (15.9953ms)\n\u2714 successful login consumes challenge, checks verifier arguments, updates counter and issues normal session (2.4725ms)\n\u2714 failed assertions consume challenges and never issue sessions (6.436ms)\n\u2714 expired, wrong-user and wrong-purpose challenges fail; userHandle binds the account (3.2783ms)\n\u2714 counter regression rejects and logs; synced zero counters work (1.3265ms)\n\u2714 registration stores only verified credentials, parses UA, and rejects duplicate and replay (19.0603ms)\n\u2714 management scopes rename/delete and protects last method (1.2398ms)\n\u2714 an email or Google identity can remove a passkey the database still treats as the last method (1.4398ms)\n\u2139 tests 18\n\u2139 suites 0\n\u2139 pass 18\n\u2139 fail 0\n\u2139 cancelled 0\n\u2139 skipped 0\n\u2139 todo 0\n\u2139 duration_ms 12403.3747\n"
}
```


---

## documentation/final_draft_evidence/frontend.json

```json
{
  "suite": "frontend",
  "command": [
    "C:\\Users\\ikari\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\bin\\node.exe",
    "frontend/node_modules/vitest/vitest.mjs",
    "run",
    "--config",
    "vitest.config.js"
  ],
  "exit_code": 1,
  "output": "node:internal/modules/cjs/loader:1520\n  throw err;\n  ^\n\nError: Cannot find module 'C:\\Users\\ikari\\Desktop\\School Work\\Intelligent-Agent-Identity-Verification-System\\frontend\\frontend\\node_modules\\vitest\\vitest.mjs'\n    at Module._resolveFilename (node:internal/modules/cjs/loader:1517:15)\n    at wrapResolveFilename (node:internal/modules/cjs/loader:1071:27)\n    at defaultResolveImplForCJSLoading (node:internal/modules/cjs/loader:1095:10)\n    at resolveForCJSWithHooks (node:internal/modules/cjs/loader:1122:12)\n    at Module._load (node:internal/modules/cjs/loader:1294:5)\n    at wrapModuleLoad (node:internal/modules/cjs/loader:255:19)\n    at Module.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:154:5)\n    at node:internal/main/run_main_module:33:47 {\n  code: 'MODULE_NOT_FOUND',\n  requireStack: []\n}\n\nNode.js v24.19.0\n"
}
```


---

## documentation/final_draft_evidence/frontend_retest.txt

```txt
X [ERROR] Cannot read directory "../../../..": Access is denied.

X [ERROR] Could not resolve "C:\\Users\\ikari\\Desktop\\School Work\\Intelligent-Agent-Identity-Verification-System\\frontend\\vitest.config.js"

failed to load config from C:\Users\ikari\Desktop\School Work\Intelligent-Agent-Identity-Verification-System\frontend\vitest.config.js

⎯⎯⎯⎯⎯⎯⎯ Startup Error ⎯⎯⎯⎯⎯⎯⎯⎯
Error: Build failed with 2 errors:
error: Cannot read directory "../../../..": Access is denied.
error: Could not resolve "C:\\Users\\ikari\\Desktop\\School Work\\Intelligent-Agent-Identity-Verification-System\\frontend\\vitest.config.js"
    at failureErrorWithLog (C:\Users\ikari\Desktop\School Work\Intelligent-Agent-Identity-Verification-System\frontend\node_modules\esbuild\lib\main.js:1467:15)
    at C:\Users\ikari\Desktop\School Work\Intelligent-Agent-Identity-Verification-System\frontend\node_modules\esbuild\lib\main.js:926:25
    at runOnEndCallbacks (C:\Users\ikari\Desktop\School Work\Intelligent-Agent-Identity-Verification-System\frontend\node_modules\esbuild\lib\main.js:1307:45)
    at buildResponseToResult (C:\Users\ikari\Desktop\School Work\Intelligent-Agent-Identity-Verification-System\frontend\node_modules\esbuild\lib\main.js:924:7)
    at C:\Users\ikari\Desktop\School Work\Intelligent-Agent-Identity-Verification-System\frontend\node_modules\esbuild\lib\main.js:951:16
    at responseCallbacks.<computed> (C:\Users\ikari\Desktop\School Work\Intelligent-Agent-Identity-Verification-System\frontend\node_modules\esbuild\lib\main.js:603:9)
    at handleIncomingPacket (C:\Users\ikari\Desktop\School Work\Intelligent-Agent-Identity-Verification-System\frontend\node_modules\esbuild\lib\main.js:658:12)
    at Socket.readFromStdout (C:\Users\ikari\Desktop\School Work\Intelligent-Agent-Identity-Verification-System\frontend\node_modules\esbuild\lib\main.js:581:7)
    at Socket.emit (node:events:509:28)
    at addChunk (node:internal/streams/readable:563:12) {
  errors: [Getter/Setter],
  warnings: [Getter/Setter]
}




```


---

## documentation/final_draft_evidence/frontend_retest_unrestricted.txt

```txt

 RUN  v5.0.3 C:/Users/ikari/Desktop/School Work/Intelligent-Agent-Identity-Verification-System/frontend


 Test Files  2 passed (2)
      Tests  16 passed (16)
   Start at  06:52:28
   Duration  27.02s (environment 99%, import 1%, transform 1%)


```


---

## documentation/final_draft_evidence/live_summary.json

```json
{
  "source_files": [
    "Supabase Snippet Untitled query.csv",
    "Supabase Snippet Untitled query (1).csv",
    "Supabase Snippet Untitled query (2).csv"
  ],
  "request_count": 12,
  "unique_agents": 8,
  "score_count": 12,
  "decision_count": 9,
  "request_status": {
    "verified": 7,
    "rejected": 2,
    "pending": 3
  },
  "decision_status": {
    "verified": 7,
    "rejected": 2
  },
  "decision_basis": {
    "svm_model": 5,
    "placeholder_threshold": 4
  },
  "request_date_range": [
    "2026-09-20 22:48:25.916221+00",
    "2026-10-03 09:52:25.018259+00"
  ],
  "decision_date_range": [
    "2026-09-20 22:58:52.975+00",
    "2026-10-03 09:53:12.975+00"
  ],
  "requests_without_decisions": 3,
  "all_requests_have_scores": true,
  "orphan_decisions": 0,
  "status_matches": 9,
  "zero_score_rows": 0,
  "nonzero_score_rows": 12,
  "probability_sums_valid": true,
  "anonymized_decisions": [
    {
      "case": 1,
      "final_decision": "verified",
      "basis": "svm_model",
      "scores": [
        "22.0025",
        "0.9941",
        "1",
        "293.4472",
        "160.449",
        "55.449"
      ]
    },
    {
      "case": 2,
      "final_decision": "rejected",
      "basis": "svm_model",
      "scores": [
        "38.6509",
        "1",
        "0.1111",
        "60.12",
        "172.4109",
        "32.7058"
      ]
    },
    {
      "case": 3,
      "final_decision": "verified",
      "basis": "svm_model",
      "scores": [
        "69.0711",
        "0.9832",
        "1",
        "30.953",
        "151.1958",
        "50.163"
      ]
    },
    {
      "case": 4,
      "final_decision": "verified",
      "basis": "placeholder_threshold",
      "scores": [
        "71.2233",
        "0.9993",
        "1",
        "133.4403",
        "174.1388",
        "56.9895"
      ]
    },
    {
      "case": 5,
      "final_decision": "verified",
      "basis": "placeholder_threshold",
      "scores": [
        "55.5091",
        "0.9853",
        "1",
        "92.6757",
        "162.6252",
        "36.0968"
      ]
    },
    {
      "case": 6,
      "final_decision": "rejected",
      "basis": "placeholder_threshold",
      "scores": [
        "59.376",
        "0.9999",
        "1",
        "27.7065",
        "172.4101",
        "49.5776"
      ]
    },
    {
      "case": 7,
      "final_decision": "verified",
      "basis": "svm_model",
      "scores": [
        "28.2329",
        "1",
        "1",
        "90.5744",
        "156.4394",
        "50.2763"
      ]
    },
    {
      "case": 8,
      "final_decision": "verified",
      "basis": "svm_model",
      "scores": [
        "46.453",
        "0.9999",
        "1",
        "209.7952",
        "152.0512",
        "44.3273"
      ]
    },
    {
      "case": 9,
      "final_decision": "verified",
      "basis": "placeholder_threshold",
      "scores": [
        "55.5091",
        "0.9853",
        "1",
        "92.6757",
        "162.6252",
        "36.0968"
      ]
    }
  ]
}
```


---

## documentation/final_draft_evidence/test_kyc_experiment.json

```json
{
  "suite": "test_kyc_experiment",
  "command": [
    "C:\\Users\\ikari\\Desktop\\School Work\\Intelligent-Agent-Identity-Verification-System\\.venv-kyc\\Scripts\\python.exe",
    "-X",
    "utf8",
    "ai-service/tests/test_kyc_experiment.py"
  ],
  "exit_code": 0,
  "output": "test_saved_dataset_is_reproducible_and_has_no_hidden_predictors (__main__.ExperimentTests.test_saved_dataset_is_reproducible_and_has_no_hidden_predictors) ... ok\ntest_split_manifest_and_scaler_only_fit_training (__main__.ExperimentTests.test_split_manifest_and_scaler_only_fit_training) ... ok\n\n----------------------------------------------------------------------\nRan 2 tests in 0.590s\n\nOK\n"
}
```


---

## documentation/final_draft_evidence/test_kyc_improvement.json

```json
{
  "suite": "test_kyc_improvement",
  "command": [
    "C:\\Users\\ikari\\Desktop\\School Work\\Intelligent-Agent-Identity-Verification-System\\.venv-kyc\\Scripts\\python.exe",
    "-X",
    "utf8",
    "ai-service/tests/test_kyc_improvement.py"
  ],
  "exit_code": 0,
  "output": "test_native_boundary_can_differ_from_probability_argmax (__main__.ImprovementTests.test_native_boundary_can_differ_from_probability_argmax) ... ok\ntest_probability_column_order_and_margin (__main__.ImprovementTests.test_probability_column_order_and_margin) ... ok\ntest_quality_transform_preserves_identity_columns_and_fitted_state (__main__.ImprovementTests.test_quality_transform_preserves_identity_columns_and_fitted_state) ... ok\ntest_review_policy_changes_decision_without_changing_probability (__main__.ImprovementTests.test_review_policy_changes_decision_without_changing_probability) ... ok\n\n----------------------------------------------------------------------\nRan 4 tests in 0.192s\n\nOK\n"
}
```


---

## documentation/final_draft_evidence/test_svm.json

```json
{
  "suite": "test_svm",
  "command": [
    "C:\\Users\\ikari\\Desktop\\School Work\\Intelligent-Agent-Identity-Verification-System\\.venv-kyc\\Scripts\\python.exe",
    "-X",
    "utf8",
    "ai-service/tests/test_svm.py"
  ],
  "exit_code": 0,
  "output": "test_class_probability_order_is_not_assumed (__main__.SVMContractTests.test_class_probability_order_is_not_assumed) ... ok\ntest_rejects_missing_malformed_nonfinite_out_of_range (__main__.SVMContractTests.test_rejects_missing_malformed_nonfinite_out_of_range) ... ok\ntest_saved_artifact_prediction_parity_and_legacy_contract (__main__.SVMContractTests.test_saved_artifact_prediction_parity_and_legacy_contract) ... ok\ntest_saved_review_policy_is_honored_without_rewriting_probabilities (__main__.SVMContractTests.test_saved_review_policy_is_honored_without_rewriting_probabilities) ... ok\ntest_sharp_image_valid_without_assumed_decision (__main__.SVMContractTests.test_sharp_image_valid_without_assumed_decision) ... ok\ntest_unavailable_has_no_silent_prediction (__main__.SVMContractTests.test_unavailable_has_no_silent_prediction) ... ok\n\n----------------------------------------------------------------------\nRan 6 tests in 0.299s\n\nOK\n"
}
```


---

## documentation/final_draft_evidence/threshold_metrics.json

```json
{
  "accuracy": 0.2866666666666667,
  "macro_f1": 0.26364742135166636,
  "weighted_f1": 0.2123978983962154,
  "confusion_matrix": [
    [
      66,
      363,
      471
    ],
    [
      8,
      77,
      215
    ],
    [
      0,
      13,
      287
    ]
  ]
}
```


---

## ai-service/ml/README.md

> Current installed model: **v3.0.0**. See [v3 results](experiments/v3/SUMMARY.md) and [offline improvement workflow](experiments/v3/README.md). On the same fresh evaluation set, accuracy changed from 75.733% to 75.800% (one additional correct decision); this is not statistically conclusive. The original v2 methodology below is preserved for reproduction. Running `train_model.py` replaces artifacts with the v2 training workflow; use the v3 instructions for the improvement experiment.

# KYC experiment v2: reproducibility and deployment

Run from the repository root (Python 3.13 used for the recorded run):

```powershell
python -m venv .venv-kyc
.\.venv-kyc\Scripts\python.exe -m pip install -r ai-service/ml/requirements-experiment.lock.txt
.\.venv-kyc\Scripts\python.exe ai-service/ml/train_model.py --version 2.0.0 --jobs 2
.\.venv-kyc\Scripts\python.exe ai-service/tests/test_svm.py
.\.venv-kyc\Scripts\python.exe ai-service/tests/test_kyc_experiment.py
node --test backend/tests/kycDecision.test.js
```

`requirements-experiment.lock.txt` is an isolated experiment environment; it does
not require downloading the image/face/OCR models. Production still uses
`ai-service/requirements.txt`. Pickles require compatible scikit-learn (1.9.0 in
this run); load only trusted artifacts. No online or automatic training exists.
Do not run a training job concurrently with the serving process. Stop/restart the
service after copying the **whole** `ml/models` artifact set; startup verifies
model/scaler hashes, version and feature contract. The Hugging Face Space must
include those files and use the matching dependency versions. This local change
does not itself publish a new Space revision.

## Data and methodology

The exact shared feature order is:
1. `face_match_score`: ArcFace score, 0–100.
2. `liveness_score`: anti-spoof score, 0–1.
3. `ocr_confidence_score`: document text agreement score, 0–1.
4. `blur_score`: raw Laplacian variance, nonnegative (higher means sharper).
5. `brightness_score`: raw mean HSV V, 0–255.
6. `contrast_score`: raw grayscale standard deviation, 0–127.5.

**Quality scores are not normalized inputs.** The 0.72/0.81/0.76 example is valid
numerically but means an extremely low-quality image in the current pipeline.
There is no documented conversion from generic 0–1 quality ratings to these raw
metrics; silently guessing one would break compatibility. MinMaxScaler handles
normalization after receiving raw features and clips to training extrema.

The stored local LFW (1,000 pairs), NUAA (1,200 presentations), MIDV quality
(500 frames), and MIDV OCR measurements are read directly. Their hashes and
computed moments are recorded in the dataset metadata. We do not claim to have
rerun their source images or independently verified historical measurements.
LFW uses the project's face scoring implementation; NUAA measures real/photo
presentations; MIDV OCR measures text similarity to ground-truth fields, not
solely EasyOCR's internal confidence. None supplies three-class KYC decisions.

`generation_config.json` fixes all scenario probabilities, borderline parameters,
quality shifts and observation noise **before** test evaluation. There are 6,000
Verified, 2,000 Manual Review and 2,000 Rejected simulated adjudication outcomes.
These are experimental quotas, not prevalence estimates. Scenarios are sampled
within each quota. Faces and liveness use truncated normals informed by local
measured means/SDs. Truncation changes resulting moments, especially near zero or
one. Clear OCR uses measured moments conditional on the upper half of observed
agreement (the conditioning itself is an assumption). Quality uses a continuous
multivariate normal over log1p(blur), brightness and contrast fitted to measured
quality covariance. Fresh draws avoid copying benchmark observations.

Class labels describe *assumed latent scenarios*, not a threshold applied to
observed scores. Borderline genuine and unresolved cases deliberately share
observed distributions, representing information missing from the six scores.
No labels are flipped and no accuracy is targeted. This ambiguity is a modelling
assumption, not evidence that real adjudicators would label those cases that way.
The simulator therefore tests behavior under an explicit assumed population;
it cannot establish a real operational decision policy.

Rejected scenarios include face mismatch, photograph presentation, document
mismatch, difficult face mismatch and difficult presentation attacks; unaffected
channels can remain strong. Review contains uncertain face, OCR, presentation,
multiple uncertainties and genuine recapture cases. Quality is shared across
identity outcomes except the explicitly simulated recapture condition. Poor
latent sharpness/contrast reduces OCR agreement in every class. Brightness alone
does not assign a rejected label; excellent quality does not replace identity
signals. The coefficients in this measurement simulation are assumptions, not
manual classifier feature weights. The SVM learns its boundary without weights
on individual features.

Exact and near-duplicate checks occur before splitting, failing closed if found.
The narrow near-duplicate tolerance is documented in the report and is a useful
screen, not proof of statistical independence. There are no persistent simulated
subjects or resampled parent observations crossing partitions. A stratified
70/15/15 row split gives 7,000/1,500/1,500. `split_manifest.csv` records assignments;
its row IDs and the latent scenarios never enter the seven-column training CSV.

Each SVM grid has C=[0.1,1,10,100] and gamma=[0.001,0.01,0.1,1,scale,auto], with
5-fold shuffled stratification, macro F1, RBF kernel, balanced classes and seed
42. MinMaxScaler is inside the grid Pipeline, so each fold fits only on its
training rows. Refit uses only the 7,000 training rows. Both six-feature and
identity-only SVMs are tuned independently using identical folds and candidate
grids. Identity-only order is face, liveness, OCR, the first three columns of the
shared contract. The Decision Tree grid searches max_depth=[3,5,8,None] and
min_samples_leaf=[5,20,50], also on training CV only.

Sigmoid CalibratedClassifierCV wraps a FrozenEstimator, learning calibration on
validation only without changing the SVM or scaler. Deployed decisions use the
largest calibrated probability. Calibration can change the balanced SVM's
original decisions toward the experimental class prior; this is reported rather
than hidden. The tree baseline reports its native predictions/probabilities;
a separate sigmoid tree comparison is also saved for probability diagnostics.
Validation is consumed for calibration and is not an independent calibration
test. Test metrics, reliability curves and importance are computed only after
all models/calibrators are frozen. No test-guided redesign is performed.

Permutation importance is the actual drop in test macro F1 over 20 shuffles,
with standard deviation across shuffles. Correlated features can share or mask
importance. Tree importance is impurity decrease, with its known split-selection
biases; the two quantities are not interchangeable. Ablation uses paired bootstrap
resampling of the same test predictions (1,000 replicates). Its interval is
conditional on this generator and fitted models, not all training randomness or
real-world populations. Six features remain the production contract regardless
of ablation outcome; no feature is removed automatically.

## API and backend compatibility

`POST /api/svm/predict` accepts all six snake_case fields and returns display
labels (`Verified`, `Manual Review`, `Rejected`) and a `probabilities` mapping.
It also returns the three legacy probability fields. Class columns are mapped
using `classes_`; no positional class assumption is made.

All-camelCase requests remain supported and receive the existing lowercase
`finalDecision` enum (`verified`, `review`, `rejected`) required by Node/Supabase.
Units are identical for both spellings. Supplying both aliases for one feature,
unknown fields, missing values, booleans, strings, non-finite numbers, negative
values or out-of-range bounded scores returns HTTP 400. A missing/inconsistent
model bundle returns 503. High but finite raw blur is allowed, not assigned an
arbitrary physical maximum. Model responses always say `decisionBasis=svm_model`.

The only backend changes remove number coercion and zero defaults for missing
scores. Invalid evidence fails before inference or placeholder fallback.
Existing fallback decisions still say `placeholder_threshold`, log the reason,
and persist their different basis through the existing controller. Their 0/1
values are rule outputs, not calibrated model certainty. No database migration
or changes to face/OCR/liveness processing were made by this experiment.

## Historical audit and limitations

Old code/artifacts are preserved in `legacy_v1`; the original 4,000-row CSV is
retained. The original notebooks are historical v1 analyses, not the authority
for v2 results. Use `train_model.py` for reproducible v2 training.

The old generator preassigned labels then sampled almost isolated ranges in all
six channels, including quality. Training-set-only scaler fitting was correct
at the outer split level, but notebook CV reused that scaler across folds. The
retraining script hard-coded earlier grid winners. There is no direct target
column in its predictor or observed code evidence of final-test fitting; absence
of historical repeated test use cannot be established. The audit reports exact,
conflicting and near duplicates and individual-feature training CV scores.

The new audit addresses target/identifier exclusion, artificial class patterns,
within-class variation, fold-local scaling, cross-split duplicates, explicit
calibration separation, fixed protocol before test, trivial feature separators
and scenario-label artifacts. If accuracy >=98%, the report flags a near-perfect
result for investigation; it must not trigger automatic label alteration or
parameter changes. Even moderate performance is not proof of realism.

Dissertation limitations: synthetic labels and assumed joint dependencies;
limited benchmark domains and sample sizes; source measurement version drift
(the image pipeline has ongoing local changes); no demographic fairness, modern
attack, camera/domain shift or external prospective validation; text agreement
cannot prove document authenticity; experimental class prior affects calibration;
false verification costs are not represented by macro F1 alone. A real deployment
needs confirmed labels, cost-aware policy validation and external calibration.
Future retraining is explicit offline batch work using administrator-confirmed
records, never triggered by completing a KYC attempt.



---

## ai-service/ml/generation_config.json

```json
{
  "seed": 42,
  "class_counts": {"Verified": 6000, "Manual Review": 2000, "Rejected": 2000},
  "provenance": "Benchmark moments are computed from existing local measured CSVs. Scenario mixtures, borderline distributions, quality shifts and measurement variation are modelling assumptions, not benchmark results or real fraud prevalence.",
  "face_borderline": [45, 16],
  "face_difficult_impostor": [32, 18],
  "live_borderline": [0.65, 0.17],
  "live_difficult_attack": [0.43, 0.24],
  "ocr_borderline": [0.53, 0.19],
  "ocr_mismatch": [0.22, 0.17],
  "clear_ocr_quantile": 0.5,
  "poor_quality_shift": [-0.65, -20, -7],
  "quality_observation_noise": [0.12, 4, 2],
  "face_measurement_sd": 3,
  "live_measurement_sd": 0.025,
  "ocr_measurement_sd": 0.04,
  "ocr_quality_penalty": 0.16,
  "quality_logblur_reference": 3.4,
  "quality_contrast_reference": 25,
  "scenarios": {
    "Verified": [
      ["consistent_genuine", 0.7, "genuine", "real", "clear", false],
      ["genuine_reading_variation", 0.2, "genuine", "real", "borderline", false],
      ["genuine_face_variation", 0.1, "borderline", "real", "clear", false]
    ],
    "Manual Review": [
      ["uncertain_face", 0.2, "borderline", "real", "clear", false],
      ["uncertain_document", 0.2, "genuine", "real", "borderline", false],
      ["uncertain_presentation", 0.2, "genuine", "borderline", "clear", false],
      ["recapture_needed", 0.25, "genuine", "real", "clear", true],
      ["multiple_uncertainties", 0.15, "borderline", "borderline", "borderline", false]
    ],
    "Rejected": [
      ["identity_mismatch", 0.25, "impostor", "real", "clear", false],
      ["photo_attack", 0.25, "genuine", "attack", "clear", false],
      ["document_mismatch", 0.2, "genuine", "real", "mismatch", false],
      ["difficult_identity_mismatch", 0.15, "difficult_impostor", "real", "clear", false],
      ["difficult_presentation_attack", 0.15, "genuine", "difficult_attack", "clear", false]
    ]
  }
}

```


---

## ai-service/ml/data/kyc_synthetic_dataset_10000.metadata.json

```json
{
  "configuration": {
    "seed": 42,
    "class_counts": {
      "Verified": 6000,
      "Manual Review": 2000,
      "Rejected": 2000
    },
    "provenance": "Benchmark moments are computed from existing local measured CSVs. Scenario mixtures, borderline distributions, quality shifts and measurement variation are modelling assumptions, not benchmark results or real fraud prevalence.",
    "face_borderline": [
      45,
      16
    ],
    "face_difficult_impostor": [
      32,
      18
    ],
    "live_borderline": [
      0.65,
      0.17
    ],
    "live_difficult_attack": [
      0.43,
      0.24
    ],
    "ocr_borderline": [
      0.53,
      0.19
    ],
    "ocr_mismatch": [
      0.22,
      0.17
    ],
    "clear_ocr_quantile": 0.5,
    "poor_quality_shift": [
      -0.65,
      -20,
      -7
    ],
    "quality_observation_noise": [
      0.12,
      4,
      2
    ],
    "face_measurement_sd": 3,
    "live_measurement_sd": 0.025,
    "ocr_measurement_sd": 0.04,
    "ocr_quality_penalty": 0.16,
    "quality_logblur_reference": 3.4,
    "quality_contrast_reference": 25,
    "scenarios": {
      "Verified": [
        [
          "consistent_genuine",
          0.7,
          "genuine",
          "real",
          "clear",
          false
        ],
        [
          "genuine_reading_variation",
          0.2,
          "genuine",
          "real",
          "borderline",
          false
        ],
        [
          "genuine_face_variation",
          0.1,
          "borderline",
          "real",
          "clear",
          false
        ]
      ],
      "Manual Review": [
        [
          "uncertain_face",
          0.2,
          "borderline",
          "real",
          "clear",
          false
        ],
        [
          "uncertain_document",
          0.2,
          "genuine",
          "real",
          "borderline",
          false
        ],
        [
          "uncertain_presentation",
          0.2,
          "genuine",
          "borderline",
          "clear",
          false
        ],
        [
          "recapture_needed",
          0.25,
          "genuine",
          "real",
          "clear",
          true
        ],
        [
          "multiple_uncertainties",
          0.15,
          "borderline",
          "borderline",
          "borderline",
          false
        ]
      ],
      "Rejected": [
        [
          "identity_mismatch",
          0.25,
          "impostor",
          "real",
          "clear",
          false
        ],
        [
          "photo_attack",
          0.25,
          "genuine",
          "attack",
          "clear",
          false
        ],
        [
          "document_mismatch",
          0.2,
          "genuine",
          "real",
          "mismatch",
          false
        ],
        [
          "difficult_identity_mismatch",
          0.15,
          "difficult_impostor",
          "real",
          "clear",
          false
        ],
        [
          "difficult_presentation_attack",
          0.15,
          "genuine",
          "difficult_attack",
          "clear",
          false
        ]
      ]
    }
  },
  "measured_sources": {
    "lfw_face_match": {
      "rows": 1000,
      "sha256": "ed82a85dfb6ab74ab338c1d396eb3cb66439a7a10784c12449f408ed5db9f86c"
    },
    "nuaa_liveness": {
      "rows": 1200,
      "sha256": "bbecefd0c98140ec54a8c230c1c4abf1fc57c9faf129056a4d3957e066787e5f"
    },
    "midv_image_quality": {
      "rows": 500,
      "sha256": "c39f918cdc086f0bb02dd4f8406f049121788c03487379a38f025e1e28250326"
    },
    "midv_ocr": {
      "rows": 480,
      "sha256": "5b13defefbef0ddf92df071b0c933e04a1e2ae81cff4542269cdd184da2c25f1"
    }
  },
  "measured_parameters": {
    "face": {
      "genuine": [
        64.81733419999999,
        16.47402134717157
      ],
      "impostor": [
        2.2927294000000003,
        3.5656385254627487
      ]
    },
    "liveness": {
      "photo_attack": [
        0.0199725,
        0.07516618512376493
      ],
      "real": [
        0.9689096666666668,
        0.07043918443874983
      ]
    },
    "ocr_clear_conditional": [
      0.76895625,
      0.1489445240948629
    ],
    "ocr_all": [
      0.45190208333333337,
      0.35222573712218497
    ],
    "quality_transformed_mean": [
      3.7200620127901636,
      171.70002240000002,
      43.2495346
    ],
    "quality_transformed_covariance": [
      [
        0.7211578661338847,
        11.38622734783699,
        0.4879691908211453
      ],
      [
        11.38622734783699,
        2172.433061105429,
        -275.16620785919343
      ],
      [
        0.4879691908211453,
        -275.16620785919343,
        288.27221128831945
      ]
    ]
  },
  "scenario_counts": {
    "consistent_genuine": 4263,
    "genuine_reading_variation": 1169,
    "genuine_face_variation": 568,
    "uncertain_face": 387,
    "uncertain_document": 445,
    "uncertain_presentation": 381,
    "recapture_needed": 500,
    "multiple_uncertainties": 287,
    "identity_mismatch": 516,
    "photo_attack": 486,
    "document_mismatch": 378,
    "difficult_identity_mismatch": 315,
    "difficult_presentation_attack": 305
  },
  "caveat": "Truncated normals approximate benchmark moments; resulting moments differ after truncation. Joint KYC labels and cross-modality dependencies are assumptions. No benchmark is a joint KYC ground-truth dataset."
}
```


---

## ai-service/ml/requirements-experiment.lock.txt

```txt
blinker==1.9.0
click==8.5.0
cloudpickle==3.1.2
contourpy==1.4.0
cycler==0.12.1
Flask==3.1.3
fonttools==4.66.1
itsdangerous==2.2.0
Jinja2==3.1.6
joblib==1.6.0
kiwisolver==1.5.1
MarkupSafe==3.0.3
matplotlib==3.11.2
narwhals==2.26.0
numpy==2.5.3
packaging==26.3
pandas==3.0.6
pillow==12.3.0
pyparsing==3.3.3
python-dateutil==2.9.0.post0
scikit-learn==1.9.0
scipy==1.18.1
six==1.17.0
threadpoolctl==3.7.0
tzdata==2026.4
Werkzeug==3.1.9

```


---

## ai-service/requirements.txt

```txt
flask
flask-cors
opencv-python>=4.8,<5
easyocr
insightface
onnxruntime
# Pinned: ml/models/*.pkl were pickled with 1.9 — retrain with ml/train_model.py after upgrading
scikit-learn>=1.9,<1.10
joblib
numpy
pillow
python-dotenv
torch
torchvision
timm
easydict
tqdm

```


---

## documentation/chapter4_wireframes/README.md

# Chapter 4 wireframe assets

The chapter contains ten grayscale wireframes as Figures 4.7 to 4.16.
Each figure is supplied as an editable SVG and a high-resolution PNG.
SVG files can be opened in a browser or edited in a vector editor.
They contain placeholder labels, not real applicant records or evaluation results.

## Source mapping

- 4.7: LoginPage.vue, RegisterPage.vue and passkey sign-in controls.
- 4.8: AgentDashboard.vue personal-details step and WorkspaceShell.vue.
- 4.9: AgentDashboard.vue document step and DocumentCaptureStep.vue.
- 4.10: LiveSelfieChallenge.vue.
- 4.11: AgentDashboard.vue progress and outcome states.
- 4.12: AdminDashboard.vue directory, status filters and WorkspaceShell.vue.
- 4.13: AdminDashboard.vue case-detail drawer and decision controls.
- 4.14: AdminDashboard.vue audit list and export dialog.
- 4.15: ManagePasskeysPage.vue.
- 4.16: AdminModelEvaluation.vue.

I use these wireframes as simplified design views of the current system.
Multiple alternative screens/states appear together in Figures 4.7 and 4.11.
The review drawer is expanded for legibility in Figure 4.13.
The chapter explains mobile reflow, state handling and acceptance checks.

## Remaining diagram updates

I have retained Figures 4.1 to 4.6 from the original chapter. I will replace these diagrams after completing the image corrections, retaining the existing figure numbers.

- 4.1: Confirm system boundary and external actors; draw only justified UML relationships.
- 4.2: Use consistent UML multiplicity/ownership notation and identifier terminology.
- 4.3: Account/profile and incomplete-request optionality; required audit and decision fields.
- 4.4: Request/response directions, auth/storage/realtime interactions and hosted boundaries.
- 4.5: Backend coordination, per-step persistence, quality rejection and service-failure paths.
- 4.6: Align the logical schema with Table 4.7, including decision basis, audit context and optional passkey entities.

## Editorial and verification notes

- Original FR-01 to FR-26 and NFR-01 to NFR-15 identifiers are retained with clarified wording.
- Added FR-27 to FR-34, NFR-16 to NFR-20, DR-01 to DR-12 and IR-01 to IR-10.
- Original timing promises lacked an evidence basis; the chapter specifies measurement and does not invent an SLA.
- Requirements describe intended obligations, not completed implementation or passing tests.
- Disclosure, non-verified retention, backup restoration and broad integration retry policy still need explicit evidence/policy.
- I will check consistency with the final approved methodology and objectives when assembling Chapters 1 to 5.
- The manual-versus-two-AI use-case comparison is a separate course activity; its actual diagrams, prompts, outputs and comparison evidence belong in the record of that activity.
- AI assistance: I used Codex for source review, requirements drafting, wireframe preparation and layout checking on 27 and 28 October 2026.
- Chapter pagination starts at 41. I will update the report pagination, contents and list of figures after merging the chapter into the full report.



---

## documentation/chapter4_wireframes/manifest.json

```json
{
  "wireframes": [
    "figure_4_07_authentication",
    "figure_4_08_personal_details",
    "figure_4_09_document_capture",
    "figure_4_10_live_selfie",
    "figure_4_11_verification_states",
    "figure_4_12_admin_directory",
    "figure_4_13_case_review",
    "figure_4_14_audit_export",
    "figure_4_15_passkey_management",
    "figure_4_16_model_evaluation"
  ],
  "width": 1000,
  "height": 700
}
```
