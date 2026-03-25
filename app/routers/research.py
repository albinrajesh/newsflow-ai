import json
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
    Stateless version: no thread_id required.
    """
    print(f"\n[API] Received research request: {request.query}")
    
    # Pass only the query; initial state handles list initializations
    initial_input = {"query": request.query}

    async def event_generator():
        print("DEBUG: event_generator started")
        try:
            # 2. Stream events using version 'v2'
            # We no longer pass 'config' here because checkpointer is removed
            async for event in agent.astream_events(initial_input, version="v2"):
                kind = event["event"]
                node = event.get("metadata", {}).get("langgraph_node", "unknown")

                # --- DEBUG LOGGING & STATUS UPDATES ---
                if kind == "on_chain_start" and node != "unknown":
                    print(f"DEBUG: Starting Node: {node}")
                    yield f"data: {json.dumps({'status': f'Processing {node}...'})}\n\n"

                # 3. Capture Token Streaming - FILTERED
                # Only stream if the synthesiser is active (UX Play)
                if kind == "on_chat_model_stream":
                    if node == "synthesiser": 
                        content = event["data"]["chunk"].content
                        if content:
                            yield f"data: {json.dumps({'content': content})}\n\n"
                    else:
                        continue

                # 4. Log completion of nodes
                if kind == "on_chain_end" and node != "unknown":
                    print(f"DEBUG: Finished Node: {node}")

            # 5. Signal completion for the test script
            print("DEBUG: Stream Finished Successfully")
            yield "data: [DONE]\n\n"

        except Exception as e:
            print(f"CRITICAL ERROR in event_generator: {str(e)}")
            yield f"data: {json.dumps({'error': f'Internal Server Error: {str(e)}'})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream"
    )