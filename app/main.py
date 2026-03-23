from fastapi import FastAPI
from app.routers import health, research

app = FastAPI(title="Deep Research Agent", version="1.0.0")

app.include_router(health.router)
app.include_router(research.router)