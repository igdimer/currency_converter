from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, HttpUrl


class Settings(BaseSettings):
    """Application settings."""

    DATABASE_DSN: PostgresDsn
    REDIS_DSN: RedisDsn
    EXCHANGERATE_URL: HttpUrl
    EXCHANGERATE_ACCESS_KEY: str

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
