from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from time import perf_counter

from ..core.config import settings
from ..pdf_loader import get_resume_info, get_resume_text
from ..services import retrieve_top_chunks

router = APIRouter(tags=["debug"])

class RetrieveResultItem(BaseModel):
    index: int
    score: float
    preview: str

class RetrieveResponse(BaseModel):
    query: str
    top_k: int
    confidence: float
    threshold: float
    handled: bool
    elapsed_ms: float
    config: dict
    results: list[RetrieveResultItem]

@router.get("/debug/resume")
def debug_resume():
    try:
        return get_resume_info()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/debug/reload-resume")
def debug_reload_resume():
    try:
        text = get_resume_text(force=True)
        return {"ok": True, "chars": len(text)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/debug/retrieve", response_model=RetrieveResponse)
def debug_retrieve(
    q: str = Query(..., description="Query text"),
    k: int = Query(None, ge=1, description="Top-k to return; defaults to settings"),
    preview_len: int = Query(280, ge=0, le=4000, description="Preview characters per chunk"),
    full_index: int | None = Query(None, description="If provided, return FULL text for this chunk index"),
):
    q = (q or "").strip()
    if not q:
        raise HTTPException(status_code=422, detail="Query must be non-empty.")

    top_k = k or settings.retrieve.top_k
    threshold = settings.similarity_threshold

    # Measure end-to-end retrieval latency
    t0 = perf_counter()
    try:
        result = retrieve_top_chunks(q, top_k=top_k)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resume not found. Load it and try again.")
    elapsed_ms = (perf_counter() - t0) * 1000.0

    if not result.top_chunks:
        return RetrieveResponse(
            query=q,
            top_k=top_k,
            confidence=0.0,
            threshold=threshold,
            handled=False,
            elapsed_ms=elapsed_ms,
            config={
                "chunk_size": settings.retrieve.chunk_size,
                "chunk_overlap": settings.retrieve.chunk_overlap,
                "boundary_window": settings.retrieve.boundary_window,
                "ngram_range": [settings.retrieve.tfidf_ngram_min, settings.retrieve.tfidf_ngram_max],
                "min_df": settings.retrieve.tfidf_min_df,
                "max_df": settings.retrieve.tfidf_max_df,
            },
            results=[],
        )

    confidence = result.confidence
    handled = confidence >= threshold

    items: list[RetrieveResultItem] = []
    for r in result.top_chunks:
        if full_index is not None and r.index == full_index:
            preview = r.text  # full text for the selected index
        else:
            preview = r.text[:preview_len]
        items.append(RetrieveResultItem(index=r.index, score=r.score, preview=preview))

    return RetrieveResponse(
        query=q,
        top_k=top_k,
        confidence=confidence,
        threshold=threshold,
        handled=handled,
        elapsed_ms=elapsed_ms,
        config={
            "chunk_size": settings.retrieve.chunk_size,
            "chunk_overlap": settings.retrieve.chunk_overlap,
            "boundary_window": settings.retrieve.boundary_window,
            "ngram_range": [settings.retrieve.tfidf_ngram_min, settings.retrieve.tfidf_ngram_max],
            "min_df": settings.retrieve.tfidf_min_df,
            "max_df": settings.retrieve.tfidf_max_df,
        },
        results=items,
    )