"""
Lightweight TF-IDF retrieval over chunked resume text.

Public entrypoint:
    retrieve_top_chunks(query: str, top_k: int = TOP_K_DEFAULT) -> RetrievalResult
"""

from __future__ import annotations

import hashlib
import logging
import threading
from dataclasses import dataclass
from typing import List
from .core.config import settings

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity 

from .pdf_loader import get_resume_text


# -----------------------------------------------------------------------------
# Configuration (env vars with safe fallbacks)
# -----------------------------------------------------------------------------

CHUNK_SIZE = settings.retrieve_chunk_size
CHUNK_OVERLAP = settings.retrieve_chunk_overlap
TOP_K_DEFAULT = settings.retrieve_top_k
BOUNDARY_BACKOFF_WINDOW = settings.retrieve_boundary_window
TFIDF_NGRAM_MIN = settings.retrieve_tfidf_ngram_min
TFIDF_NGRAM_MAX = settings.retrieve_tfidf_ngram_max
TFIDF_MIN_DF = settings.retrieve_tfidf_min_df
TFIDF_MAX_DF = settings.retrieve_tfidf_max_df

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Public data structures
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class RetrievedChunk:
    """
    A single retrieved text chunk.

    Attributes:
        text: The chunk content.
        score: Similarity score in [0, 1], higher is more similar.
        index: Position of the chunk in the source chunk list.
    """
    text: str
    score: float
    index: int


@dataclass(frozen=True)
class RetrievalResult:
    """
    Retrieval output for a query.

    Attributes:
        query: The original query string.
        top_chunks: Ranked list of the best matching chunks.
        confidence: The top chunk score, or 0.0 if no results.
    """
    query: str
    top_chunks: List[RetrievedChunk]
    confidence: float  # the top score (0..1)

# Explicitly export only the public API symbol(s)
__all__ = ["RetrievedChunk", "RetrievalResult", "retrieve_top_chunks"]

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
def _split_into_chunks(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text into overlapping chunks while trying to preserve word boundaries.

    The function trims the input text, then slices it into segments of up to
    `chunk_size` characters. It avoids cutting words in half by stepping
    backwards from the tentative end to the nearest whitespace within a window
    of `BOUNDARY_BACKOFF_WINDOW`. Consecutive chunks overlap by `overlap`
    characters to preserve context.

    Args:
        text: Input text to split.
        chunk_size: Maximum length of each chunk in characters. Must be > overlap.
        overlap: Number of characters to overlap between consecutive chunks. Must be >= 0.

    Returns:
        A list of non-empty, whitespace-trimmed chunks.

    Raises:
        ValueError: If parameters are invalid.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)

        # Avoid cutting in the middle of a word if possible
        if end < n and not text[end].isspace():
            back = end
            # Walk backwards up to BOUNDARY_BACKOFF_WINDOW chars looking for whitespace
            while back > start and (end - back) < BOUNDARY_BACKOFF_WINDOW and not text[back].isspace():
                back -= 1
            if back > start and text[back].isspace():
                end = back

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == n:
            break

        # Overlap backwards to keep context
        start = max(0, end - overlap)

    return chunks


def _hash_text(s: str) -> str:
    """Stable hash of text for inexpensive change detection."""
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


# -----------------------------------------------------------------------------
# Internal retriever
# -----------------------------------------------------------------------------
class _TfidfChunkRetriever:
    """
    Lazily builds a TF-IDF index over chunked resume text and serves cosine similarity queries.

    Thread-safe via an RLock. The index is rebuilt if the resume content hash changes.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._fitted = False
        self._last_hash: str | None = None
        self._chunks: List[str] = []
        self._vectorizer: TfidfVectorizer | None = None
        self._tfidf_matrix: csr_matrix | None = None

    def _ensure_fitted(self) -> None:
        """
        Ensure the TF-IDF index is built and current. Safe for concurrent calls.
        """
        # Fast path without locking if already up-to-date
        try:
            resume_text = get_resume_text() or ""
        except FileNotFoundError:
            # Propagate to caller; public API will handle gracefully
            raise

        current_hash = _hash_text(resume_text)
        if self._fitted and self._last_hash == current_hash:
            return

        # Slow path with lock and re-check
        with self._lock:
            try:
                resume_text = get_resume_text() or ""
            except FileNotFoundError:
                raise

            current_hash = _hash_text(resume_text)
            if self._fitted and self._last_hash == current_hash:
                return

            try:
                chunks = _split_into_chunks(resume_text, CHUNK_SIZE, CHUNK_OVERLAP)
            except ValueError as e:
                logger.error("Invalid chunk params: %s", e)
                chunks = []

            if not chunks:
                # Build a tiny index to keep downstream code simple
                chunks = ["(resume is empty)"]

            vectorizer = TfidfVectorizer(
                lowercase=True,
                sublinear_tf=True,
                stop_words="english",
                ngram_range=(TFIDF_NGRAM_MIN, TFIDF_NGRAM_MAX),
                min_df=TFIDF_MIN_DF,
                max_df=TFIDF_MAX_DF,
            )
            tfidf_matrix = vectorizer.fit_transform(chunks)

            self._chunks = chunks
            self._vectorizer = vectorizer
            self._tfidf_matrix = tfidf_matrix
            self._fitted = True
            self._last_hash = current_hash
            logger.debug("TF-IDF index built: %d chunks", len(chunks))

    def retrieve(self, query: str, top_k: int = TOP_K_DEFAULT) -> RetrievalResult:
        """
        Retrieve the top matching chunks for a query using cosine similarity.

        Args:
            query: The natural language query string.
            top_k: Number of top chunks to return. Minimum of 1 is enforced.

        Returns:
            RetrievalResult with ranked chunks and a confidence score.

        Notes:
            Confidence is the top similarity score in [0, 1].
        """
        q = (query or "").strip()
        if not q:
            return RetrievalResult(query=query, top_chunks=[], confidence=0.0)

        # Clamp top_k to a sensible minimum
        k = max(1, int(top_k))

        self._ensure_fitted()
        assert self._vectorizer is not None and self._tfidf_matrix is not None

        query_vec = self._vectorizer.transform([q])

        # Cosine similarity between the query and each chunk (shape: [num_chunks])
        sims = cosine_similarity(query_vec, self._tfidf_matrix).ravel()

        if sims.size == 0:
            return RetrievalResult(query=query, top_chunks=[], confidence=0.0)

        # Select top-k via partial selection, then order those k by score desc
        k = min(k, sims.size)
        sel = np.argpartition(-sims, kth=max(0, k - 1))[:k]
        order = sel[np.argsort(sims[sel])[::-1]]
        results: List[RetrievedChunk] = [
            RetrievedChunk(text=self._chunks[i], score=float(sims[i]), index=int(i))
            for i in order
        ]
        confidence = results[0].score if results else 0.0
        return RetrievalResult(query=query, top_chunks=results, confidence=confidence)


# Module-level instance of retriever (internal)
_retriever = _TfidfChunkRetriever()


def retrieve_top_chunks(query: str, top_k: int = TOP_K_DEFAULT) -> RetrievalResult:
    """
    Public API for retrieval. Safe to call from routers.

    Args:
        query: The natural language query string.
        top_k: Number of top chunks to return. Defaults to TOP_K_DEFAULT.

    Returns:
        RetrievalResult with ranked chunks. Returns an empty result if the resume
        text is missing or no chunks are available.
    """
    try:
        return _retriever.retrieve(query=query, top_k=top_k)
    except FileNotFoundError:
        logger.error("Error retrieving top chunks: resume not found")
        return RetrievalResult(query=query, top_chunks=[], confidence=0.0)