from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from pydantic import RedisDsn


class Settings(BaseSettings):
    """Application settings."""

    DATABASE_DSN: PostgresDsn
    REDIS_DSN: RedisDsn

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
