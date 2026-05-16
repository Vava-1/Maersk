"""
AfriSwarm Configuration - Enterprise-grade settings management.
Supports on-prem deployment with zero external dependencies for core reasoning.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings with on-prem defaults."""

    # Application
    APP_NAME: str = "AfriSwarm Maersk Resilience Swarm"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Security
    SECRET_KEY: str = os.urandom(32).hex()
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RBAC_ENABLED: bool = True
    AUDIT_LOG_ENABLED: bool = True
    PII_REDACTION_ENABLED: bool = True
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Default Credentials (override via ENV in production)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "afriswarm2026"
    OPERATOR_USERNAME: str = "operator"
    OPERATOR_PASSWORD: str = "operator2026"

    # Database - PostgreSQL
    DATABASE_URL: str = "postgresql://afriswarm:secure_password@postgres:5432/afriswarm"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Vector Database - PGVector
    PGVECTOR_ENABLED: bool = True
    VECTOR_DIMENSION: int = 1536

    # Redis - Caching & Pub/Sub
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_PASSWORD: Optional[str] = None

    # Kafka - Event Streaming
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_ENABLED: bool = True

    # LangGraph & LLM
    LANGGRAPH_CHECKPOINT_ENABLED: bool = True
    LANGGRAPH_THREAD_TTL: int = 3600
    # Default to local model for on-prem; can be overridden for cloud
    LLM_PROVIDER: str = "local"  # Options: local, openai, anthropic, azure
    LOCAL_MODEL_URL: str = "http://localhost:11434"  # Ollama/llama.cpp
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AZURE_OPENAI_KEY: Optional[str] = None

    # Multi-model routing
    FAST_MODEL: str = "llama3.1:8b"  # For quick tasks
    POWERFUL_MODEL: str = "llama3.1:70b"  # For complex reasoning
    VISION_MODEL: str = "llava:34b"  # For multimodal tasks

    # Observability
    LANGSMITH_API_KEY: Optional[str] = None
    PROMETHEUS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = True

    # Agent Configuration
    AGENT_HEALTH_CHECK_INTERVAL: float = 0.5  # 500ms
    HEALING_TIMEOUT_SECONDS: int = 30
    MAX_RETRIES: int = 3
    CHECKPOINT_DIR: str = "./checkpoints"

    # Maersk-specific
    MAERSK_API_KEY: Optional[str] = None
    MAERSK_TENANT_ID: str = "default"
    AFRICA_CORRIDORS: List[str] = [
        "mombasa_nairobi_addis",
        "dar_es_salaam_lusaka",
        "lagos_accra_abidjan",
        "casablanca_dakar",
        "cairo_nairobi_mombasa",
    ]

    # Neo4j - Knowledge Graph
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "secure_password"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB

    # Compliance
    DATA_RETENTION_DAYS: int = 2555  # 7 years
    GDPR_ENABLED: bool = True
    CCPA_ENABLED: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
