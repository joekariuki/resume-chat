from fastapi import APIRouter, HTTPException
from .pdf_loader import get_resume_info, get_resume_text

router = APIRouter()

@router.get("/debug/resume")
def debug_resume():
    try:
        info = get_resume_info()
        return info
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/debug/reload-resume")
def debug_reload_resume():
    try:
        text = get_resume_text(force=True)
        return {"ok": True, "chars": len(text)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))