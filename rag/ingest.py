import os
import asyncio
from typing import List, Optional
from urllib.parse import urlparse, parse_qs

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from youtube_transcript_api import YouTubeTranscriptApi
from rag.retriever import vector_service

# Global lock to prevent FAISS file access violations during simultaneous writes
ingestion_lock = asyncio.Lock()

def extract_video_id(url: str) -> Optional[str]:
    """
    Robustly extracts the video ID from various YouTube URL formats including 
    Shorts, Embeds, and mobile links.
    """
    try:
        parsed_url = urlparse(url)
        
        # Handle youtu.be/VIDEO_ID
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        
        # Handle youtube.com formats
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                query = parse_qs(parsed_url.query)
                return query.get('v', [None])[0]
            
            # Handle /shorts/, /embed/, or /v/
            path_parts = parsed_url.path.split('/')
            if len(path_parts) >= 3 and path_parts[1] in ('shorts', 'embed', 'v'):
                return path_parts[2]
    except Exception:
        return None
    return None

async def ingest_pdf_service(file_bytes: bytes, filename: str):
    """
    Saves PDF bytes to a temp file, parses into chunks with metadata, 
    and updates the FAISS index safely.
    """
    temp_path = f"temp_{filename}"
    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        
        # Use standard chunking for Mistral/Gemini compatibility
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_docs = splitter.split_documents(docs)

        # Add additional metadata if missing
        for doc in final_docs:
            doc.metadata["source"] = filename
            doc.metadata["type"] = "pdf"

        async with ingestion_lock:
            await vector_service.add_documents(final_docs)
            
        print(f"[Ingest] Successfully added {len(final_docs)} chunks from {filename}")
        return {"status": "success", "chunks": len(final_docs), "source": filename}
    
    except Exception as e:
        print(f"[Ingest Error] PDF failed: {e}")
        return {"status": "error", "message": f"PDF Error: {str(e)}"}
    
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

async def ingest_url_service(url: str):
    """
    Extracts YouTube transcripts, chunks text, and stores with URL metadata.
    """
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return {"status": "error", "message": "Invalid YouTube URL format."}

        # Attempt to get English or Hindi transcripts
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
        except Exception:
            # Fallback to any available transcript
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            except Exception as e:
                return {"status": "error", "message": f"No transcript available: {str(e)}"}

        full_text = " ".join([entry['text'] for entry in transcript_list])
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(full_text)
        
        # Wrap chunks in Document objects to keep the source URL attached
        docs_to_add = [
            Document(page_content=chunk, metadata={"source": url, "type": "youtube"}) 
            for chunk in chunks
        ]

        async with ingestion_lock:
            await vector_service.add_documents(docs_to_add)
            
        print(f"[Ingest] Successfully added {len(chunks)} chunks from YouTube: {url}")
        return {"status": "success", "chunks": len(chunks), "source": url}

    except Exception as e:
        print(f"[Ingest Error] URL failed: {e}")
        return {"status": "error", "message": f"URL Error: {str(e)}"}