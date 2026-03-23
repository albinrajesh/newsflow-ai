from fastapi import FastAPI
from pydantic import BaseModel
from mcp.tools.web_search import search_tavily
from mcp.tools.document_reader import read_document
from mcp.tools.memory_store import save_memory, search_memory

app = FastAPI(title="MCP Tool Server", version="1.0.0")

class ToolRequest(BaseModel):
    query: str = ""
    source: str = ""
    summary: str = ""
    max_results: int = 5

@app.post("/tools/web_search")
def web_search_tool(request: ToolRequest):
    return {"results": search_tavily(request.query, request.max_results)}

@app.post("/tools/document_reader")
def document_reader_tool(request: ToolRequest):
    return {"content": read_document(request.source)}

@app.post("/tools/memory_store/save")
def memory_save_tool(request: ToolRequest):
    save_memory(request.query, request.summary)
    return {"status": "saved"}

@app.post("/tools/memory_store/search")
def memory_search_tool(request: ToolRequest):
    return {"memory": search_memory(request.query)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)