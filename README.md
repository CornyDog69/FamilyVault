# Family Document Vault

A secure, private web application for storing and sharing important family PDF documents — passports, insurance papers, property documents, etc. — with AES-256 encryption at rest and OTP-based login.

## Demonstration

<img src="demo.gif" alt="Demonstration Video" width="100%" autoplay loop />

---

## Features

- **Striking Neo-Brutalism Theme** — Features a bold, high-contrast, and interactive modern web design
- **Email OTP login** — no passwords, 6-digit codes valid for 5 minutes
- **AES-256 encryption** — all PDFs encrypted before touching disk
- **Protected document access** — files never served directly; decrypted on-the-fly per authenticated request
- **Admin-only uploads** — only the designated admin email can add/delete documents
- **Rate-limited OTPs** — max 5 OTP requests per email per hour
- **10 document limit** — perfect for a small family vault
- **First-login username** — family members choose a display name on first login

---

## Quick Start

### 1. Clone & configure

```bash
git clone <your-repo>
cd family-doc-vault
cp .env.example .env
# Edit .env with your values
```

### 2. Install dependencies

```bash
pip install -r req.txt
```

### 3. Run locally

```bash
uvicorn backend.main:app --reload
```

Open: http://localhost:8000

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `MONGO_URI` | MongoDB connection string | `mongodb+srv://...` |
| `JWT_SECRET` | Secret for JWT signing (random string) | `abc123xyz...` |
| `AES_KEY` | 32-character AES-256 key | `MyFamilyVaultKey1234567890ABCD!` |
| `ADMIN_EMAIL` | Email that can upload/delete documents | `dad@family.com` |
| `SMTP_HOST` | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | Gmail address | `vault@gmail.com` |
| `SMTP_PASS` | Gmail App Password | `xxxx xxxx xxxx xxxx` |
| `APP_NAME` | Display name in emails | `Family Document Vault` |

### Gmail Setup
1. Enable 2-Factor Authentication on your Gmail
2. Go to **Google Account → Security → App Passwords**
3. Generate a new App Password for "Mail"
4. Use that 16-character password as `SMTP_PASS`

---

## Deployment on Render (Free Tier)

1. Push code to GitHub
2. Connect repo in [Render Dashboard](https://dashboard.render.com)
3. Create a **Web Service** with:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Add a **Disk** (1 GB) mounted at `/opt/render/project/src/secure_docs`
5. Set all environment variables in the Render dashboard
6. Deploy!

Alternatively, use the included `render.yaml` for blueprint deployment.

---

## MongoDB Atlas Setup (Free Tier)

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a database user
3. Whitelist all IPs: `0.0.0.0/0` (required for Render)
4. Copy the connection string to `MONGO_URI`

The app auto-creates these collections with indexes:
- `users` — family member accounts
- `documents` — document metadata (no file content)
- `otp_codes` — TTL-indexed (auto-deletes after expiry)

---

## Project Structure

```
------- REPLACE
family-doc-vault/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, routes setup, static file serving
│   ├── config.py            # Configuration management
│   ├── database.py          # MongoDB connection & collection references
│   ├── auth.py              # JWT creation/verification, auth dependency
│   ├── otp_service.py       # OTP generation, storage, email sending
│   ├── encryption.py        # AES-256 encrypt/decrypt helpers
│   ├── document_service.py  # File upload, retrieval, delete logic
│   ├── utils/
│   │   ├── helpers.py       # Utility functions
│   │   └── logger.py        # Logging configuration
│   └── routes/
│       ├── __init__.py
│       ├── auth_routes.py   # /api/auth/* endpoints
│       └── document_routes.py  # /api/documents, /api/get_document/*
├── frontend/
│   ├── __init__.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── dashboard.css
│   │   │   ├── login.css
│   │   │   └── upload.css
│   │   └── js/
│   │       ├── dashboard.js
│   │       ├── login.js
│   │       └── upload.js
│   ├── templates/
│   │   ├── login.html       # OTP login flow
│   │   ├── dashboard.html   # Document listing & download
│   │   └── upload.html      # Admin document upload
│   └── package.json         # Frontend dependencies and scripts
├── secure_docs/             # AES-encrypted .enc files (gitignored)
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_document.py
│   └── conftest.py
├── scripts/
│   └── seed_data.py         # Scripts for seeding test data
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI workflow
├── requirements.txt
├── render.yaml              # Render deployment blueprint
└── .env
```

---

## Security Notes

- `secure_docs/` contains encrypted `.enc` files; even if accessed directly they are unreadable without the AES key
- Documents are **only** accessible via `/api/get_document/{id}` which requires a valid JWT cookie
- JWT tokens expire after 72 hours
- OTPs expire after 5 minutes and are single-use
- Set `secure=True` on cookies when deploying with HTTPS (update `COOKIE_SETTINGS` in `auth_routes.py`)

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/request-otp` | None | Send OTP to email |
| POST | `/api/auth/verify-otp` | None | Verify OTP, receive session cookie |
| POST | `/api/auth/set-username` | None | Set username (first login) |
| POST | `/api/auth/logout` | None | Clear session cookie |
| GET | `/api/auth/me` | User | Get current user info |
| GET | `/api/documents` | User | List all document metadata |
| GET | `/api/get_document/{id}` | User | Decrypt & stream PDF |
| POST | `/api/upload-document` | Admin | Upload & encrypt PDF |
| DELETE | `/api/documents/{id}` | Admin | Delete document & file |

## Project Directory Analysis

- **Backend (`backend/`)**: Contains the core application logic built with FastAPI. Key modules include:
  - `auth.py` – JWT creation/verification and authentication dependencies.
  - `otp_service.py` – OTP generation, storage, and email sending.
  - `encryption.py` – AES‑256 encrypt/decrypt helpers.
  - `document_service.py` – File upload, retrieval, and delete logic.
  - `routes/` – Separate route files for authentication (`auth_routes.py`) and documents (`document_routes.py`).
- **Frontend (`frontend/`)**: Static HTML pages (`login.html`, `dashboard.html`, `upload.html`) along with CSS and JavaScript assets structured under a **Neo-Brutalism** design theme for bold and dynamic client-side experiences.
- **Encrypted Storage (`secure_docs/`)**: Holds AES‑encrypted `.enc` files; files are never stored in plaintext.
- **Configuration**: Environment variables are defined in `.env`; dependency list is in `requirements.txt`.
- **Deployment**: `render.yaml` provides a blueprint for deploying on Render; environment variables are configured in the Render dashboard.
- **Security**: Encrypted documents are only decrypted on-the-fly per authenticated request; JWTs expire after 72 hours; OTPs are single‑use and expire after 5 minutes.

---

## Authors

- **Frontend:** [Prateek Priyanshu](https://github.com/p7xtxxk)
- **Backend:** [Ishan Gupta](https://github.com/CornyDog69)