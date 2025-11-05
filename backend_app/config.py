"""
Configuration management using Pydantic Settings
Loads environment variables from .env file
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    DATABASE_URL: str
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    
    # S3 Configuration
    S3_BUCKET_NAME: str
    
    # Cognito Configuration
    COGNITO_USER_POOL_ID: str
    COGNITO_APP_CLIENT_ID: str
    COGNITO_REGION: str = "us-east-1"
    
    # CloudWatch Configuration
    CLOUDWATCH_LOG_GROUP: str = "/aws/bookswap"
    CLOUDWATCH_LOG_STREAM: str = "backend-logs"
    
    # Application Configuration
    APP_NAME: str = "BookSwap Cloud"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache settings instance
    @lru_cache ensures we only load settings once
    """
    return Settings()