# ResumeChat — PRD & Project Plan (Next.js + FastAPI)

## One-liner

**ResumeChat** is a simple open-source app: a web chat that answers questions about a **PDF resume** stored in the repo. If the agent cannot answer, it **alerts the owner** (email/SMS/WhatsApp) and lets visitors **submit contact info** that triggers notifications.

**Goal:** Working public demo **today**. Optimize for speed, clarity, and easy forking.

---

## Architecture (split deploy)

- **Web (UI):** Next.js + TailwindCSS → Vercel
- **API (agent):** FastAPI (Python) → Railway or Render
- **LLM:** OpenAI API
- **Notifications:** Resend (email), Twilio (SMS & WhatsApp)
- **Resume Source:** `/resume/resume.pdf` in the API repo (parsed on startup)
- **Storage:** In-memory or SQLite (for logs/leads); keep simple for MVP

### High-level flow

1. User chats in the Next.js UI → calls `POST {API_URL}/chat`.
2. FastAPI answers using PDF-extracted text + LLM.
3. If uncertain, returns fallback and triggers **QUESTION_UNANSWERED** notifications.
4. “Contact Me” form calls `POST {API_URL}/contact` → **LEAD_CAPTURED** notifications, store lead.

---

## Success criteria (MVP)

- Answers basic questions grounded in the PDF content.
- Sends owner notifications for unanswered questions and leads.
- Deployed, public, and demoable with instructions to fork.

---

## Non-goals (MVP)

- Multi-user accounts
- Auth / dashboards
- Multi-resume support
- Novu orchestration

---

## Repository layout (monorepo)

```
resume-chat/
├─ web/                      # Next.js app (Vercel)
│  ├─ app/ or pages/
│  ├─ components/
│  ├─ lib/
│  ├─ .env.example
│  └─ README.md
├─ api/                      # FastAPI app (Railway/Render)
│  ├─ resume/resume.pdf
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ pdf_loader.py
│  │  ├─ retrieval.py
│  │  ├─ router_chat.py
│  │  ├─ router_contact.py
│  │  ├─ notify.py
│  │  └─ models.py
│  ├─ requirements.txt
│  ├─ Dockerfile
│  ├─ render.yaml            # (if using Render)
│  └─ Procfile               # (Railway optional)
└─ PRD.md
```

---

## API design (FastAPI)

### Endpoints

- `POST /chat`  
  **Input:** `{ "message": string }`  
  **Output:** `{ "reply": string, "handled": boolean }`  
  Behavior: embed/retrieve from parsed resume text, call OpenAI.  
  If low confidence → `handled=false`, send **QUESTION_UNANSWERED** notification.

- `POST /contact`  
  **Input:** `{ "name": string, "email"?: string, "phone"?: string }`  
  **Output:** `{ "success": boolean }`  
  Behavior: store lead (JSON or SQLite), send **LEAD_CAPTURED** notification.

- `GET /healthz`  
  Returns `{ "ok": true }` for health checks.

### Core modules

- `pdf_loader.py` — parse `/resume/resume.pdf` into clean text.
- `retrieval.py` — split text, embed with OpenAI, store vectors in memory/SQLite.
- `notify.py` — wrappers for Resend + Twilio.
- `router_chat.py` — `/chat` logic.
- `router_contact.py` — `/contact` logic.

---

## Web design (Next.js)

- Single page:
  - Chat window (message list + input).
  - Small “About the resume” card with a short blurb.
  - “Contact Me” modal (name, email, phone).
- Calls API via `NEXT_PUBLIC_API_URL`.
- API enables CORS for Vercel domain.

---

## Environment variables

### API (`api/.env.example`)

```env
# OpenAI
OPENAI_API_KEY=

# Resend (Email)
RESEND_API_KEY=
EMAIL_FROM="ResumeChat <notify@yourdomain.com>"
NOTIFY_TO_EMAIL=you@yourdomain.com

# Twilio (SMS & WhatsApp)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_SMS_FROM=+1XXXXXXXXXX
TWILIO_WA_FROM=whatsapp:+1XXXXXXXXXX
NOTIFY_TO_PHONE=+1YYYYYYYYYY       # E.164 format
NOTIFY_TO_WHATSAPP=+1YYYYYYYYYY    # E.164 format

# CORS
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000

# Optional
SIMILARITY_THRESHOLD=0.25
PORT=8000
```

### Web (`web/.env.local.example`)

```env
NEXT_PUBLIC_API_URL=https://your-api.onrender.com
```

---

## Minimal infra files (API)

**`requirements.txt`**

```
fastapi
uvicorn[standard]
python-dotenv
openai
tiktoken
pdfminer.six
numpy
scikit-learn
requests
```

**`Dockerfile`**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential poppler-utils && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Render config (render.yaml)**

```yaml
services:
  - type: web
    name: resumechat-api
    env: docker
    plan: free
    autoDeploy: true
    healthCheckPath: /healthz
```

**Railway (Procfile, optional)**

```
web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

---

## CORS snippet

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS","*").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Notifications routing

- **QUESTION_UNANSWERED:** WhatsApp → SMS → Email
- **LEAD_CAPTURED:** Email + WhatsApp

Use FastAPI `BackgroundTasks` to avoid blocking responses.

---

## Deployment steps

### API (Render)

1. Push repo, connect Render to `api/` directory.
2. Choose **Docker** deploy, set env vars.
3. Wait for `/healthz` to pass.
4. Copy service URL, set as `NEXT_PUBLIC_API_URL` in web app.

### API (Railway)

1. Create service from GitHub repo (`api/`).
2. Use Docker or Procfile.
3. Set env vars, deploy, copy URL.

### Web (Vercel)

1. Create new project → `web/`.
2. Set `NEXT_PUBLIC_API_URL`.
3. Deploy.

---

## Timeline (3 hours)

**Hour 1**

- Scaffold Next.js UI (chat + contact modal).
- Scaffold FastAPI app, add PDF parsing + `/healthz`.

**Hour 2**

- Add retrieval + OpenAI Q&A.
- Implement `/chat` with fallback + notifications.
- Implement `/contact` with lead notifications.

**Hour 3**

- Deploy API (Render/Railway).
- Deploy Web (Vercel).
- Test notifications.
- Push repo, write LinkedIn post.

---

## LinkedIn launch post (draft)

Today I built something fun: **ResumeChat** 🎉

👉 An open-source chat agent that can read my resume, answer questions, and even ping me if:

- It can’t answer a question
- Someone wants to connect

**Stack:** Next.js (UI on Vercel), FastAPI (API on Render/Railway), OpenAI, Resend, Twilio.

Try it: [Live demo link]  
Repo: [GitHub link]

Built in a few hours to show how resumes can be interactive (and forkable). Curious what you think 👀

#opensource #ai #resume #fastapi #nextjs
