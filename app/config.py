from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    tavily_api_key: str
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = "https://cloud.langfuse.com"
    ollama_model: str = "openrouter/meta-llama/llama-3.3-70b-instruct:free"
    mcp_server_url: str = "http://localhost:8001"
    openrouter_api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()