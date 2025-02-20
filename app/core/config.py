from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    POLLINATIONS_BASE_URL: str = "https://text.pollinations.ai"
    DEFAULT_MODEL: str = "openai"
    ENABLE_FUNCTION_CALLING: bool = True
    FUNCTION_CALLING_SYSTEM_PROMPT: str = """You are a helpful AI assistant capable of using tools through function calling.
When a function is available and relevant to the user's request, you should use it.
Always structure your function call responses in valid JSON format."""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings() 