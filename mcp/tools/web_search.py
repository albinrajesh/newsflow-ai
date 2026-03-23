import os
from tavily import TavilyClient
from app.config import settings

def search_tavily(query: str, max_results: int = 5):
    if not settings.tavily_api_key:
        return "Tavily API Key missing."
    
    client = TavilyClient(api_key=settings.tavily_api_key)
    # Search for context/snippets
    response = client.search(query=query, search_depth="advanced", max_results=max_results)
    
    formatted_results = []
    for result in response.get("results", []):
        formatted_results.append({
            "title": result.get("title"),
            "url": result.get("url"),
            "content": result.get("content")
        })
    return formatted_results