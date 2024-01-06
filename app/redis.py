from redis import asyncio as aioredis

from app.config import settings

redis_client = aioredis.from_url(settings.REDIS_DSN.unicode_string(), decode_responses=True)
