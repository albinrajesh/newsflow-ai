import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi
from rag.retriever import vector_service

async def ingest_pdf_service(file_bytes, filename):
    temp_path = f"temp_{filename}"
    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_docs = splitter.split_documents(docs)

        chunks = [doc.page_content for doc in final_docs]

        await vector_service.add_documents(chunks)
        return {"status": "success", "chunks": len(chunks)}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

async def ingest_url_service(url: str):
    try:
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError("Invalid YouTube URL")

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry['text'] for entry in transcript])
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(full_text)
        
        await vector_service.add_documents(chunks)
        return {"status": "success", "chunks": len(chunks)}
    except Exception as e:
        raise Exception(f"Failed to ingest URL: {e}")
