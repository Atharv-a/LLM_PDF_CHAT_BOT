from redis import Redis
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
import os
import logging

logger = logging.getLogger("pdf_chat_bot")

async def setup_redis():
    try:
        # Get Redis credentials from environment variables
        redis_host = os.getenv("REDIS_HOST")
        redis_port = int(os.getenv("REDIS_PORT")) 
        redis_password = os.getenv("REDIS_PASSWORD")

        # Connect to Redis (online instance)
        # redis_connection = Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        redis_connection = redis.from_url(
            f"redis://{redis_host}:{redis_port}",
            password=redis_password,
            encoding="utf-8",
            decode_responses=True,
        )
        # Initialize the rate limiter with Redis
        await FastAPILimiter.init(redis_connection)
        logger.info("Redis for limiter has been set up successfully.")
        return redis_connection
    except Exception as e:
        logger.error(f"Redis setup failed: {e}")
        raise e
