from redis.asyncio import ConnectionPool
from redis.asyncio import Redis

from app.config import settings

pool = ConnectionPool.from_url(  # type: ignore
    settings.REDIS_DSN.unicode_string(),
    decode_responses=True,
)
redis_client = Redis(connection_pool=pool)
