from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging


from .core.config import settings
from .routers.chat import router as chat_router
from .routers.contact import router as contact_router
from .routers.debug import router as debug_router


logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(chat_router)
app.include_router(contact_router)


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
    