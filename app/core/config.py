from functools import lru_cache
from urllib.parse import urlparse

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://event:event@localhost:5432/security_events"
    )
    test_database_url: str = (
        "postgresql+psycopg://event_test:event_test@localhost:5433/"
        "security_events_test"
    )
    api_host: str = "127.0.0.1"
    api_port: int = 8001
    sql_echo: bool = False
    llm_base_url: str = Field(
        default="",
        validation_alias=AliasChoices("LLM_BASE_URL", "llm_base_url"),
    )
    llm_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("LLM_API_KEY", "llm_api_key"),
    )
    llm_model: str = Field(
        default="",
        validation_alias=AliasChoices("LLM_MODEL", "llm_model"),
    )
    embedding_base_url: str = Field(
        default="",
        validation_alias=AliasChoices("EMBEDDING_BASE_URL", "embedding_base_url"),
    )
    embedding_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("EMBEDDING_API_KEY", "embedding_api_key"),
    )
    embedding_model: str = Field(
        default="",
        validation_alias=AliasChoices("EMBEDDING_MODEL", "embedding_model"),
    )
    rag_top_k: int = Field(
        default=5,
        validation_alias=AliasChoices("RAG_TOP_K", "rag_top_k"),
    )
    rag_chunk_size: int = Field(
        default=800,
        validation_alias=AliasChoices("RAG_CHUNK_SIZE", "rag_chunk_size"),
    )
    rag_chunk_overlap: int = Field(
        default=120,
        validation_alias=AliasChoices("RAG_CHUNK_OVERLAP", "rag_chunk_overlap"),
    )
    rag_local_demo_mode: bool = Field(
        default=True,
        validation_alias=AliasChoices("RAG_LOCAL_DEMO_MODE", "rag_local_demo_mode"),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="EVENT_",
        extra="ignore",
    )


def ensure_safe_test_database_url(url: str) -> str:
    database_name = urlparse(url).path.rsplit("/", 1)[-1]
    if "_test" not in database_name:
        raise ValueError("测试数据库名称必须包含 '_test'")
    return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
