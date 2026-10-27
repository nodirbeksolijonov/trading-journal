import os


class Settings:
    # Swap for e.g. postgresql+psycopg://user:pass@db:5432/journal when moving to Postgres.
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./trading_journal.db")
    cors_origins: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")


settings = Settings()
