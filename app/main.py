import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Import your routers
from app.routers import health, research

app = FastAPI(title="Deep Research Agent", version="1.0.0")

# 3. Mount the Frontend Directory (Windows-Safe Pathing)
# We resolve the absolute path to the 'frontend' folder
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# 2. Include your Research Router (Streaming + Ingestion)
app.include_router(health.router)
app.include_router(research.router)

# 1. Handle CORS (Cross-Origin Resource Sharing)
# This allows your frontend to talk to your backend without being blocked by the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Include your Research Router (Streaming + Ingestion)
app.include_router(research.router)

# 3. Mount the Frontend Directory (Windows-Safe Pathing)
# We resolve the absolute path to the 'frontend' folder
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(current_dir, "..", "frontend")

# Verify the path exists so you don't get a startup error
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    print(f"[System] Frontend mounted successfully at: {frontend_path}")
else:
    print(f"[Warning] Frontend directory NOT found at: {frontend_path}")

@app.get("/")
async def root():
    return {"message": "Newsflow AI Backend is Running. Access UI at /static/chat_upload.html"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)