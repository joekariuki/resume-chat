from __future__ import annotations

import os
import re
import threading
from pathlib import Path
from typing import Optional, Dict, Any

from pypdf import PdfReader

# Default resume path: api/resume/resume.pdf
DEFAULT_RESUME_PATH = Path(__file__).resolve().parents[1] / "resume"/"resume_sample.pdf"

# Allow overrding via env var if needed
RESUME_PATH = Path(os.getenv("RESUME_PATH", str(DEFAULT_RESUME_PATH)))


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n") 
    text = text.replace("\u00A0", " ")
    text = re.sub(r"-\n(?=\S)", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

class _ResumeTextCache:
    """
    Thread-safe, lazy cache for parsed resume text backed by pypdf.
    Cache invalidates automatically if the PDF mtime changes.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = threading.RLock()
        self._cached_text: Optional[str] = None
        self._cached_mtime: Optional[float] = None
        self._cached_pages: Optional[int] = None

    
    def load(self, force: bool = False) -> str:
        with self._lock:
            if not self._path.exists():
                raise FileNotFoundError(f"Resume not found at {self._path}")
            
            mtime = self._path.stat().st_mtime
            if not force and self._cached_text is not None and self._cached_mtime == mtime:
                return self._cached_text
            
            reader = PdfReader(self._path)
            pages_text = []

            for page in reader.pages:
                try:
                    # pypdf extract_text returns None for non-text (scanned) pages
                    text = page.extract_text() or ""
                except:
                    text = ""
                if text:
                    pages_text.append(text.strip())
            
            joined = "\n\n".join(p for p in pages_text if p)
            cleaned = _normalize_whitespace(joined)

            self._cached_text = cleaned
            self._cached_mtime = mtime
            self._cached_pages = len(reader.pages)
            return self._cached_text
    
    def info(self) -> Dict[str, Any]:
        """
        Returns lightweight info about the cached resume for debugging.
        Will lazy-load the PDF if not already cached.
        """
        text = self.load(force=False)

        return {
            "path": str(self._path),
            "exists": self._path.exists(),
            "pages": self._cached_pages,
            "chars": len(text),
            "mtime": self._cached_mtime,
            "preview": text[:500]
        }

# Module-level singleton used by the app
_cache = _ResumeTextCache(RESUME_PATH)

def get_resume_text(force: bool = False) -> str:
    """
    Returns the text content of the cached resume PDF.
    
    If force is True, will re-load the PDF even if it's already cached.
    """
    return _cache.load(force=force)

def get_resume_info() -> Dict[str, Any]:
    """
    Returns lightweight info about the cached resume for debugging.
    Will lazy-load the PDF if not already cached.
    """
    return _cache.info()
    
            
                
                
            
