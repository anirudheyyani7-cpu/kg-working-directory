from upstash_redis import Redis
from app.config import settings

_redis: Redis | None = None


def get_redis() -> Redis | None:
    global _redis
    if _redis is None and settings.upstash_redis_rest_url and settings.upstash_redis_rest_token:
        _redis = Redis(url=settings.upstash_redis_rest_url, token=settings.upstash_redis_rest_token)
    return _redis


async def is_processed(url: str) -> bool:
    r = get_redis()
    if r is None:
        return False
    result = r.sismember("tmt_kg:processed_urls", url)
    return bool(result)


async def mark_processed(url: str):
    r = get_redis()
    if r is not None:
        r.sadd("tmt_kg:processed_urls", url)


async def get_queue_depth() -> int:
    r = get_redis()
    if r is None:
        return 0
    result = r.llen("tmt_kg:extraction_queue")
    return int(result or 0)
