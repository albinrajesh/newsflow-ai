import json
import uuid
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Import the compiled graph from your agent/graph.py
from agent.graph import agent

router = APIRouter(prefix="/research", tags=["research"])

class ResearchRequest(BaseModel):
    query: str

@router.post("/stream")
async def research_stream(request: ResearchRequest):
    """
    Endpoint to stream research results using LangGraph astream_events.
    """
    print(f"\n[API] Received research request: {request.query}")
    
    # 1. Initialize State and Config
    # We use a unique thread_id so SqliteSaver can track this specific run
    thread_id = str(uuid.uuid4())
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    # Pass only the query; let the AgentState handles the list initializations
    initial_input = {"query": request.query}

    async def event_generator():
        print("DEBUG: event_generator started")
        try:
            # 2. Stream events using version 'v2'
            async for event in agent.astream_events(initial_input, config, version="v2"):
                kind = event["event"]
                # Get the name of the node currently running
                node = event.get("metadata", {}).get("langgraph_node", "unknown")

                # --- DEBUG LOGGING ---
                if kind == "on_chain_start" and node != "unknown":
                    print(f"DEBUG: Starting Node: {node}")
                    # We can still send status updates for the UI
                    yield f"data: {json.dumps({'status': f'Processing {node}...'})}\n\n"

                # 3. Capture Token Streaming - FILTERED
                # We ONLY yield tokens if the current node is 'synthesiser'
                if kind == "on_chat_model_stream":
                    if node == "synthesiser":  # <--- CRITICAL FILTER
                        content = event["data"]["chunk"].content
                        if content:
                            yield f"data: {json.dumps({'content': content})}\n\n"
                    else:
                        # This skips the Planner's sub-questions and Grader's YES/NO
                        continue

                # 4. Log completion of nodes
                if kind == "on_chain_end" and node != "unknown":
                    print(f"DEBUG: Finished Node: {node}")

            # 5. Signal completion
            print("DEBUG: Stream Finished Successfully")
            yield "data: [DONE]\n\n"

        except Exception as e:
            print(f"CRITICAL ERROR in event_generator: {str(e)}")
            yield f"data: {json.dumps({'error': f'Internal Server Error: {str(e)}'})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream"
    )