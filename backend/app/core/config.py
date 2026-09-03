"""Configuração centralizada da aplicação (12-factor: tudo via ambiente)."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# NoDecode: por padrão, pydantic-settings tenta decodificar campos list[str]
# lidos do ambiente como JSON, o que quebra um simples CSV como
# "http://a,http://b". Com NoDecode, o valor bruto da env var chega como
# string para o validator abaixo, que faz o split.
CsvList = Annotated[list[str], NoDecode]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Aplicação ---
    APP_NAME: str = "Verifica.AI API"
    ENVIRONMENT: Literal["development", "test", "production"] = "development"
    DEBUG: bool = False
    API_PREFIX: str = "/v1"

    # --- Rede / CORS ---
    # Origens explícitas — NUNCA usar "*" em produção. Ex.: "http://localhost:5173,https://verifica.ai"
    CORS_ORIGINS: CsvList = Field(default_factory=lambda: ["http://localhost:5173"])
    # IDs de extensão de navegador autorizados (chrome-extension://<id>, moz-extension://<id>)
    ALLOWED_EXTENSION_ORIGINS: CsvList = Field(default_factory=list)
    ALLOWED_HOSTS: CsvList = Field(default_factory=lambda: ["localhost", "127.0.0.1"])

    @field_validator(
        "CORS_ORIGINS",
        "ALLOWED_EXTENSION_ORIGINS",
        "ALLOWED_HOSTS",
        "ALLOWED_CONTENT_TYPES",
        mode="before",
    )
    @classmethod
    def _split_csv(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    # --- Rate limiting ---
    RATE_LIMIT_ANALYZE: str = "10/minute"
    RATE_LIMIT_DEFAULT: str = "60/minute"
    # Por cliente (chave de API), não por IP — ver app/api/v1/endpoints/public.py
    RATE_LIMIT_PUBLIC_API: str = "30/minute"

    # --- Upload / validação de imagem ---
    MAX_UPLOAD_MB: int = 10
    ALLOWED_CONTENT_TYPES: CsvList = Field(
        default_factory=lambda: ["image/jpeg", "image/png", "image/webp"]
    )
    MAX_IMAGE_PIXELS: int = 40_000_000  # ~40MP — proteção contra decompression bombs

    # --- Detector ---
    # auto: tenta gemini (checkpoint próprio, se existir) -> ensemble
    # (frequency + hf + llm_judge, o que estiver disponível) -> mock.
    DETECTOR_MODE: Literal[
        "auto", "mock", "hf", "gemini", "ensemble", "frequency", "llm_judge"
    ] = "auto"
    HF_MODEL_ID: str = "umm-maybe/AI-image-detector"
    GEMINI_MODEL_PATH: str = "models/gemini_detector.pt"

    # --- LlmJudgeDetector (juiz forense via API do Gemini — não é o modelo
    # próprio acima, é uma chamada à API do Google) ---
    GEMINI_API_KEY: str | None = None
    # Conferir o ID de modelo mais recente disponível no Google AI Studio —
    # este default pode ficar desatualizado.
    GEMINI_LLM_JUDGE_MODEL: str = "gemini-2.5-flash"

    # --- Banco de dados ---
    DATABASE_URL: str = "postgresql+asyncpg://verifica:verifica@localhost:5432/verifica_ai"
    ENABLE_ANALYSIS_LOGGING: bool = False  # só metadados (hash, prob, label) — nunca a imagem

    # --- Observabilidade ---
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = True

    @property
    def MAX_UPLOAD_BYTES(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
