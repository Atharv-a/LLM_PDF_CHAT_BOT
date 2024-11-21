from redis import Redis
from fastapi_limiter import FastAPILimiter
import os
import logging

logger = logging.getLogger("pdf_chat_bot")

def setup_redis():
    try:
        # Get Redis credentials from environment variables
        redis_host = os.getenv("REDIS_HOST")
        redis_port = int(os.getenv("REDIS_PORT")) 
        redis_password = os.getenv("REDIS_PASSWORD")

        # Connect to Redis (online instance)
        redis = Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

        # Initialize the rate limiter with Redis
        FastAPILimiter.init(redis)
        logger.info("Redis for limiter has been set up successfully.")
        return redis
    except Exception as e:
        logger.error(f"Redis setup failed: {e}")
        raise e
