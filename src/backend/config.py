from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str = Field(..., description="OpenAI API key")
    mcp_server_host: str = Field(default="localhost", description="MCP server host")
    mcp_server_port: int = Field(default=8001, description="MCP server port")
    backend_host: str = Field(default="localhost", description="Backend server host")
    backend_port: int = Field(default=8000, description="Backend server port")
    model_name: str = Field(default="gpt-4o-mini", description="OpenAI model name")
    max_tokens: int = Field(default=1000, description="Maximum tokens for response")
    temperature: float = Field(default=0.7, description="Temperature for model response")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError('Temperature must be between 0 and 2')
        return v
    
    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        if v < 1:
            raise ValueError('Max tokens must be at least 1')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()