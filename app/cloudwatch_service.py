"""
AWS CloudWatch logging service
Sends application logs to CloudWatch for monitoring
"""
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from .config import get_settings

settings = get_settings()

# Initialize CloudWatch Logs client
cloudwatch_client = boto3.client(
    'logs',
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)


def ensure_log_group_exists():
    """
    Create CloudWatch log group and stream if they don't exist
    Called on application startup
    """
    try:
        # Create log group
        cloudwatch_client.create_log_group(
            logGroupName=settings.CLOUDWATCH_LOG_GROUP
        )
        print(f"✅ Created CloudWatch log group: {settings.CLOUDWATCH_LOG_GROUP}")
    except cloudwatch_client.exceptions.ResourceAlreadyExistsException:
        print(f"ℹ️  CloudWatch log group already exists: {settings.CLOUDWATCH_LOG_GROUP}")
    except Exception as e:
        print(f"⚠️  Error creating log group: {str(e)}")
    
    try:
        # Create log stream
        cloudwatch_client.create_log_stream(
            logGroupName=settings.CLOUDWATCH_LOG_GROUP,
            logStreamName=settings.CLOUDWATCH_LOG_STREAM
        )
        print(f"✅ Created CloudWatch log stream: {settings.CLOUDWATCH_LOG_STREAM}")
    except cloudwatch_client.exceptions.ResourceAlreadyExistsException:
        print(f"ℹ️  CloudWatch log stream already exists: {settings.CLOUDWATCH_LOG_STREAM}")
    except Exception as e:
        print(f"⚠️  Error creating log stream: {str(e)}")


def log_to_cloudwatch(message: str, level: str = "INFO"):
    """
    Send log message to CloudWatch
    
    Args:
        message: Log message to send
        level: Log level (INFO, WARNING, ERROR)
    """
    try:
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        
        # Send log event to CloudWatch
        cloudwatch_client.put_log_events(
            logGroupName=settings.CLOUDWATCH_LOG_GROUP,
            logStreamName=settings.CLOUDWATCH_LOG_STREAM,
            logEvents=[
                {
                    'timestamp': timestamp,
                    'message': f"[{level}] {message}"
                }
            ]
        )
        
        # Also print to console for local development
        if settings.DEBUG:
            print(f"[CloudWatch] [{level}] {message}")
            
    except ClientError as e:
        # If CloudWatch logging fails, fall back to console logging
        print(f"⚠️  CloudWatch logging failed: {str(e)}")
        print(f"[{level}] {message}")
    except Exception as e:
        print(f"⚠️  Unexpected error in CloudWatch logging: {str(e)}")
        print(f"[{level}] {message}")