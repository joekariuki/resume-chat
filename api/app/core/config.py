from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PositiveInt, NonNegativeInt

class RetrievalSettings(BaseSettings):
    chunk_size: PositiveInt = Field(1200, alias="RETRIEVE_CHUNK_SIZE")
    chunk_overlap: NonNegativeInt = Field(200, alias="RETRIEVE_CHUNK_OVERLAP")
    top_k: PositiveInt = Field(3, alias="RETRIEVE_TOP_K")
    boundary_window: PositiveInt = Field(50, alias="RETRIEVE_BOUNDARY_WINDOW")
    tfidf_ngram_min: PositiveInt = Field(1, alias="RETRIEVE_TFIDF_NGRAM_MIN")
    tfidf_ngram_max: PositiveInt = Field(1, alias="RETRIEVE_TFIDF_NGRAM_MAX")
    tfidf_min_df: float = Field(1.0, alias="RETRIEVE_TFIDF_MIN_DF")
    tfidf_max_df: float = Field(1.0, alias="RETRIEVE_TFIDF_MAX_DF")

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    allowed_origins: str = Field("*", alias="ALLOWED_ORIGINS")
    similarity_threshold: float = Field(0.25, alias="SIMILARITY_THRESHOLD")
    port: PositiveInt = Field(8000, alias="PORT")
    resume_path: str = Field(..., alias="RESUME_PATH")
    enable_debug_routes: int = Field(0, alias="ENABLE_DEBUG_ROUTES")
    retrieval: RetrievalSettings = RetrievalSettings()

settings = AppSettings()