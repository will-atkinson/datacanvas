"""Application configuration."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Configuration settings for DataCanvas application."""
    app_name: str = "DataCanvas (MVP)"
    max_upload_mb: int = 10
    max_preview_rows: int = 25
    top_n_categories: int = 5


CFG = AppConfig()
