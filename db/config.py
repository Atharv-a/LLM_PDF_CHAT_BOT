from pydantic_settings import BaseSettings
from pydantic import ConfigDict

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

    model_config = ConfigDict(env_file=".env", extra="allow")

settings = Settings()
