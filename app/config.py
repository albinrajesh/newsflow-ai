import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # --- API Keys ---
    tavily_api_key: str
    openrouter_api_key: str = ""
    
    # --- Langfuse (Observability) ---
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https:// cloud.langfuse.com"
    
    # --- Model & Server Config ---
    # Defaulting to Llama 3.3 via OpenRouter as per your last config
    ollama_model: str = "openrouter/meta-llama/llama-3.3-70b-instruct:free"
    # Updated to match your port 8001 preference
    mcp_server_url: str = "http://localhost:8001"

    # --- Pydantic Engine Config ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # This is the "Safety Switch" that prevents the 'Extra inputs' error
        extra="ignore" 
    )

# Initialize the settings object
settings = Settings()