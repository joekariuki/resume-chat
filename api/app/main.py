from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging


from .core.config import settings
from .router_chat import router as router_chat
from .router_contact import router as router_contact
from .router_debug import router as debug_router

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(router_chat)
app.include_router(router_contact)


if settings.enable_debug_routes:
    app.include_router(debug_router)

origins = [o.strip() for o in (settings.allowed_origins or "").split(",") if o.strip()]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def warm_resume_loader():
    """
        Light warm-up so first query is fast.
        We only touch the resume text here. If you add a `warm_start()` in retrieval,
        call it here instead.
    """
    try:
        from .pdf_loader import get_resume_text
        _ = get_resume_text()
        logger.info("Resume loaded successfully on startup.")
    except FileNotFoundError:
        logger.info("Resume not found on startup; retriever will build lazily.")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
    