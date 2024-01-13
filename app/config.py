from pydantic import HttpUrl, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    DATABASE_DSN: PostgresDsn
    REDIS_DSN: RedisDsn
    EXCHANGERATE_URL: HttpUrl
    EXCHANGERATE_ACCESS_KEY: str
    AUTH_SECRET: str
    JWT_TOKEN_SECRET: str
    ACCESS_TOKEN_LIFETIME_DAYS: int
    REFRESH_TOKEN_LIFETIME_DAYS: int

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
