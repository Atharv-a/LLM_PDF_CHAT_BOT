from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str 
    database_port: str 
    database_password: str 
    database_name: str 
    database_username: str 
    aws_access_key_id: str
    aws_secret_access_key: str
    s3_region_name: str
    s3_bucket_name: str 
    google_api_key: str

    class Config:
        env_file = ".env"  # Specify the environment file
        extra = "allow"  # Allow additional environment variables

settings = Settings()
