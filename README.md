# ResumeChat

**ResumeChat** is an open-source app that turns your resume into an interactive chat agent.

- Users can ask questions about your resume (stored as a PDF in the repo).
- If the agent cannot answer, it notifies you (email/SMS/WhatsApp).
- Visitors can also leave their contact info, which triggers a notification.

Built with **Next.js**, **FastAPI**, **OpenAI**, **Resend**, and **Twilio**.

## Features

- 📄 Resume-based Q&A (reads from `resume/resume.pdf`)
- ❓ Saves and notifies you about unanswered questions
- 📬 Lead capture form with notifications
- 📲 Notifications via Email (Resend), SMS & WhatsApp (Twilio)
- 🌐 Web UI built with Next.js + TailwindCSS

## Tech Stack

- **Frontend:** Next.js (deployed on Vercel)
- **Backend:** FastAPI (Python, deployed on Render/Railway)
- **LLM:** OpenAI API
- **Email:** Resend
- **SMS/WhatsApp:** Twilio

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/joekariuki/resume-chat.git
cd resume-chat
```

### 2. Setup API (FastAPI)

```bash
cd api
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Setup Web (Next.js)

```bash
cd web
cp .env.local.example .env.local
npm install
npm run dev
```

## Deployment

- **Frontend:** Deploy `web/` to Vercel.
- **Backend:** Deploy `api/` to Railway or Render (Dockerfile included).
- Set `NEXT_PUBLIC_API_URL` in the web app to point to your backend URL.

## Environment Variables

### API (`api/.env.example`)

```env
OPENAI_API_KEY=
RESEND_API_KEY=
EMAIL_FROM="ResumeChat <notify@yourdomain.com>"
NOTIFY_TO_EMAIL=you@domain.com

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_SMS_FROM=+1XXXXXXXXXX
TWILIO_WA_FROM=whatsapp:+1XXXXXXXXXX
NOTIFY_TO_PHONE=+1YYYYYYYYYY
NOTIFY_TO_WHATSAPP=+1YYYYYYYYYY
```

### Web (`web/.env.local.example`)

```env
NEXT_PUBLIC_API_URL=https://your-api.onrender.com
```

## Demo

🔗 Live demo: [link here]  
📂 Repo: [GitHub link]

## License

MIT License
