import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # --- API Keys ---
    tavily_api_key: str
    # openrouter_api_key: str = ""
    google_api_key: str  # Add this line
    ollama_model: str = "gemini-2.0-flash-lite"
    
    # --- Langfuse (Observability) ---
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    
    # --- Model & Server Config ---
    ollama_model: str = "openrouter/meta-llama/llama-3.3-70b-instruct:free"
    
    # --- MCP Server Config (ADDED THIS) ---
    # Default to localhost:8001 to match your running MCP terminal
    mcp_server_url: str = "http://127.0.0.1:8001" 
    
    # --- Pydantic Engine Config ---
    max_retries: int = 3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" 
    )

# Initialize the settings object
settings = Settings()