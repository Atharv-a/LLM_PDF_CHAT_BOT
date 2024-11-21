from fastapi import FastAPI
import logging
from db.redis_setup import setup_redis  # Your redis setup function
from aws.s3client import ensure_bucket_exists, S3_BUCKET_NAME
from db import models
from db.database import engine
import google.auth
from google.auth import exceptions
from google.oauth2.service_account import Credentials
import os

logger = logging.getLogger("pdf_chat_bot")

# job of this code is to ensure that
# 1) Connection to AWS S3 bucket is established
# 2) Connection to PostgreSQL is established
# 3) Connection to Redis for rate limiter is established
# 4) Authentication for using google generative ai is complete

async def startup_event(app: FastAPI):
    """
    Startup event for initializing services like Redis, Google Cloud, Database, and S3.
    """
    # Setup Redis for rate limiting
    try:
        redis = setup_redis()  # Call Redis setup function
    except Exception as e:
        logger.error(f"Redis setup failed: {e}")
        raise e

    # Ensure the S3 bucket exists
    try:
        ensure_bucket_exists(S3_BUCKET_NAME)
        logger.info(f"S3 bucket '{S3_BUCKET_NAME}' ensured.")
    except Exception as e:
        logger.error(f"Error ensuring S3 bucket: {e}")

    # Authenticate with Google Cloud
    try:
        GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not GOOGLE_CREDENTIALS_PATH:
            raise ValueError("Google Cloud credentials file path not set.")
        credentials = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH)
        creds, project = google.auth.default()
        logger.info(f"Successfully authenticated. Project: {project}")
    except exceptions.DefaultCredentialsError:
        logger.error("Google Cloud authentication failed.")

    # Create database tables if they don't exist
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
