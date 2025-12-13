"""
Application configuration management.

Centralizes environment variable loading and provides type-safe configuration access.
"""
import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from multiple files
# 1. First load .env.config (non-sensitive settings)
# 2. Then load .env (sensitive settings, overrides .env.config if keys overlap)
load_dotenv('.env.config', override=False)  # Load config first
load_dotenv('.env', override=True)  # Load secrets, override if needed


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Discord
    discord_bot_token: str = Field(
        ...,
        description="Discord bot token for authentication"
    )
    tennis_memo_channel_id: Optional[int] = Field(
        default=None,
        description="Discord channel ID for tennis memo input"
    )
    tennis_output_channel_id: Optional[int] = Field(
        default=None,
        description="Discord channel ID for tennis analysis output"
    )

    # Gemini AI
    gemini_api_key: str = Field(
        ...,
        description="Google Gemini API key for AI processing"
    )

    # GitHub
    github_repo: str = Field(
        ...,
        description="GitHub repository name (format: username/repo-name)"
    )
    github_token: str = Field(
        ...,
        description="GitHub personal access token"
    )
    obsidian_path: str = Field(
        default="sessions",
        description="Base directory path in GitHub repository"
    )

    # Obsidian Vault
    obsidian_vault_path: Path = Field(
        default=Path("./obsidian_vault"),
        description="Local path to Obsidian vault"
    )

    # Application Settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode with verbose logging"
    )
    max_file_size_mb: int = Field(
        default=20,
        description="Maximum file size in MB for attachments"
    )

    # Gemini Model Settings
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        description="Gemini model to use for processing"
    )
    gemini_embedding_model: str = Field(
        default="text-embedding-004",
        description="Gemini embedding model for vector search"
    )

    # ChromaDB Settings
    chromadb_path: Path = Field(
        default=Path("./chromadb_data"),
        description="Path to ChromaDB persistent storage"
    )
    chromadb_collection_name: str = Field(
        default="tennis_memos",
        description="ChromaDB collection name"
    )

    def get_max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.obsidian_vault_path.mkdir(parents=True, exist_ok=True)
        self.chromadb_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
# This will be initialized when the module is imported
try:
    settings = Settings()
    settings.ensure_directories()
except Exception as e:
    # If settings cannot be loaded (e.g., in test environment without .env),
    # create a dummy settings object that can be overridden
    print(f"Warning: Could not load settings from environment: {e}")
    print("Using default settings. Some features may not work correctly.")
    # Create settings with dummy values for testing
    settings = Settings(
        discord_bot_token=os.getenv("DISCORD_BOT_TOKEN", "dummy_token"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", "dummy_key"),
        github_repo=os.getenv("GITHUB_REPO", "user/repo"),
        github_token=os.getenv("GITHUB_TOKEN", "dummy_github_token"),
    )
