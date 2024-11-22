import boto3
from botocore.exceptions import ClientError
from db.config import settings

# Get the value of the S3_BUCKET_NAME from settings
S3_BUCKET_NAME = settings.s3_bucket_name

# Create the S3 client using LocalStack
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.s3_region_name,
    endpoint_url=settings.aws_endpoint_url, 
)

def ensure_bucket_exists(bucket_name):
    try:
        # Check if the bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} already exists.")
    except s3_client.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        
        if error_code == "404":
            print(f"Bucket {bucket_name} does not exist. Creating bucket...")
            try:
                # Create the bucket
                s3_client.create_bucket(
                    Bucket=bucket_name
                )
                print(f"Bucket {bucket_name} created.")
            except ClientError as create_error:
                print(f"Failed to create bucket: {create_error}")
        else:
            print(f"Failed to check/create bucket: {e}")

# Ensure the bucket exists
ensure_bucket_exists(S3_BUCKET_NAME)
