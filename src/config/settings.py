"""
Centralized configuration management using Pydantic Settings.
Loads from environment variables and .env file.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==================== Application ====================
    environment: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    max_iterations: int = Field(default=15, ge=1, le=50)
    timeout_seconds: int = Field(default=300, ge=10, le=600)

    # ==================== LLM Configuration ====================
    primary_llm: Literal["groq", "ollama", "claude", "openai"] = "groq"

    # Groq Settings
    groq_api_key: str = Field(default="", description="Groq API key")
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    groq_max_tokens: int = Field(default=4096, ge=256, le=8192)

    # Anthropic Settings (Optional)
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    anthropic_model: str = "claude-sonnet-4-20250514"

    # OpenAI Settings (Optional)
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = "gpt-4"

    # Ollama Settings (Local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.3"

    # ==================== Memory Configuration ====================
    enable_memory: bool = True
    memory_backend: Literal["file", "vector", "disabled"] = "file"
    memory_dir: Path = Field(default=Path("data/memory"))

    # ==================== Tool Configuration ====================
    enable_code_execution: bool = Field(
        default=False, description="SECURITY: Enable tools that execute code"
    )
    enable_web_search: bool = False
    tools_timeout: int = Field(default=30, ge=5, le=120)

    # ==================== Performance ====================
    cache_llm_responses: bool = True
    cache_ttl_seconds: int = Field(default=3600, ge=60)
    cache_dir: Path = Field(default=Path("data/cache"))

    # ==================== Monitoring ====================
    enable_tracing: bool = True
    enable_metrics: bool = True
    log_dir: Path = Field(default=Path("data/logs"))

    # ==================== Paths ====================
    config_dir: Path = Field(default=Path("config"))
    prompts_dir: Path = Field(default=Path("config/prompts"))

    @field_validator("memory_dir", "cache_dir", "log_dir", "config_dir", "prompts_dir")
    @classmethod
    def ensure_path_exists(cls, v: Path) -> Path:
        """Ensure directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("groq_api_key")
    @classmethod
    def validate_groq_key(cls, v: str, info) -> str:
        """Validate Groq API key if Groq is primary LLM."""
        if info.data.get("primary_llm") == "groq" and not v:
            raise ValueError(
                "GROQ_API_KEY is required when primary_llm is 'groq'. "
                "Get one free at https://console.groq.com/"
            )
        return v

    def get_llm_config(self) -> dict:
        """Get configuration for the primary LLM."""
        if self.primary_llm == "groq":
            return {
                "api_key": self.groq_api_key,
                "model": self.groq_model,
                "temperature": self.groq_temperature,
                "max_tokens": self.groq_max_tokens,
            }
        elif self.primary_llm == "anthropic":
            return {
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model,
            }
        elif self.primary_llm == "ollama":
            return {
                "base_url": self.ollama_base_url,
                "model": self.ollama_model,
            }
        else:
            raise ValueError(f"Unsupported LLM: {self.primary_llm}")

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
