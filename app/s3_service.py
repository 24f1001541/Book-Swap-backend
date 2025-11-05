"""
AWS S3 service for image upload and deletion
Handles book cover image storage
"""
import boto3
from botocore.exceptions import ClientError
import uuid
from .config import get_settings
from .cloudwatch_service import log_to_cloudwatch

settings = get_settings()

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)


async def upload_file_to_s3(file, filename: str) -> str:
    """
    Upload file to S3 bucket and return the public URL
    
    Args:
        file: UploadFile object from FastAPI
        filename: Original filename
        
    Returns:
        str: Public URL of uploaded file
        
    Raises:
        Exception: If upload fails
    """
    try:
        # Generate unique filename to avoid collisions
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload file to S3
        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                'ContentType': file.content_type or 'image/jpeg',
                'ACL': 'public-read'  # Make file publicly readable
            }
        )
        
        # Generate public URL
        url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
        
        log_to_cloudwatch(f"File uploaded to S3: {unique_filename}", level="INFO")
        return url
        
    except ClientError as e:
        error_msg = f"S3 upload error: {str(e)}"
        log_to_cloudwatch(error_msg, level="ERROR")
        raise Exception(f"Failed to upload file to S3: {str(e)}")
    except Exception as e:
        error_msg = f"Unexpected error during S3 upload: {str(e)}"
        log_to_cloudwatch(error_msg, level="ERROR")
        raise Exception(f"Failed to upload file: {str(e)}")


async def delete_file_from_s3(file_url: str) -> bool:
    """
    Delete file from S3 bucket
    
    Args:
        file_url: Full URL of the file to delete
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        # Extract filename from URL
        # URL format: https://bucket-name.s3.region.amazonaws.com/filename.ext
        filename = file_url.split("/")[-1]
        
        # Delete object from S3
        s3_client.delete_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=filename
        )
        
        log_to_cloudwatch(f"File deleted from S3: {filename}", level="INFO")
        return True
        
    except ClientError as e:
        error_msg = f"S3 delete error: {str(e)}"
        log_to_cloudwatch(error_msg, level="ERROR")
        return False
    except Exception as e:
        error_msg = f"Unexpected error during S3 deletion: {str(e)}"
        log_to_cloudwatch(error_msg, level="ERROR")
        return False