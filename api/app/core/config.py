from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PositiveInt, NonNegativeInt

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # tolerate unused/env keys for MVP
    )

    # Core
    allowed_origins: str = Field("*", alias="ALLOWED_ORIGINS")
    similarity_threshold: float = Field(0.25, alias="SIMILARITY_THRESHOLD")
    port: PositiveInt = Field(8000, alias="PORT")
    resume_path: str | None = Field(None, alias="RESUME_PATH")
    enable_debug_routes: bool = Field(True, alias="ENABLE_DEBUG_ROUTES")

    # Retrieval (flattened for simplicity)
    retrieve_chunk_size: PositiveInt = Field(1200, alias="RETRIEVE_CHUNK_SIZE")
    retrieve_chunk_overlap: NonNegativeInt = Field(200, alias="RETRIEVE_CHUNK_OVERLAP")
    retrieve_top_k: PositiveInt = Field(3, alias="RETRIEVE_TOP_K")
    retrieve_boundary_window: PositiveInt = Field(50, alias="RETRIEVE_BOUNDARY_WINDOW")
    retrieve_tfidf_ngram_min: PositiveInt = Field(1, alias="RETRIEVE_TFIDF_NGRAM_MIN")
    retrieve_tfidf_ngram_max: PositiveInt = Field(1, alias="RETRIEVE_TFIDF_NGRAM_MAX")
    retrieve_tfidf_min_df: float = Field(1.0, alias="RETRIEVE_TFIDF_MIN_DF")
    retrieve_tfidf_max_df: float = Field(1.0, alias="RETRIEVE_TFIDF_MAX_DF")

settings = AppSettings()