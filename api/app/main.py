from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .router_chat import router as router_chat
from .router_contact import router as router_contact
from .router_debug import router as debug_router
import os

load_dotenv(override=True)

app = FastAPI()
app.include_router(router_chat)
app.include_router(router_contact)

if os.getenv("ENABLE_DEBUG_ROUTES", "1") == "1":
    app.include_router(debug_router)

origins = [o.strip() for o in (os.getenv("ALLOWED_ORIGINS") or "").split(",") if o.strip()]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def warm_resume_loader():

    try:
        from .pdf_loader import get_resume_text
        _ = get_resume_text()
    except FileNotFoundError:
        print("Resume not found")
        pass

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
    