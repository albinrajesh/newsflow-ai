import asyncio
import numpy as np
from vector_store.embedder import embed
from vector_store.store import get_store

class VectorService:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.store = get_store()

    async def reload(self):
        async with self.lock:
            self.store.load()

    async def add_documents(self, documents: list):
        """
        Accepts a list of LangChain Document objects or dicts 
        containing 'page_content' and 'metadata'.
        """
        async with self.lock:
            # 1. Ensure latest version is loaded
            self.store.load()
            
            # 2. Extract texts and metadata
            # This handles both raw strings (fallback) and Document objects
            chunks = []
            metadatas = []
            for doc in documents:
                if hasattr(doc, 'page_content'):
                    chunks.append(doc.page_content)
                    metadatas.append(doc.metadata)
                else:
                    chunks.append(str(doc))
                    metadatas.append({})

            # 3. Generate Embeddings
            embeddings = embed(chunks)
            if isinstance(embeddings, list):
                embeddings = np.array(embeddings)
            
            # 4. Save to store (ensure your store.add_chunks supports metadata)
            # If your store is a standard FAISS object, use add_doc_embeddings
            self.store.add_chunks(chunks, embeddings, metadatas=metadatas)
            self.store.save()
            
            # 5. Sync state
            self.store.load()
            print(f"[VectorService] Successfully indexed {len(chunks)} chunks with metadata.")

    def retrieve(self, query: str, top_k: int = 3, source_filter: str = None) -> list:
        """
        Retrieves chunks, optionally filtering by source to avoid context mixing.
        """
        try:
            self.store.load()
            
            # Generate Query Embedding
            query_embeddings = embed([query])
            query_embedding = np.array(query_embeddings[0])
            
            # Search the store
            # Logic: If source_filter is provided, we filter the results
            results = self.store.search(query_embedding, top_k=top_k)
            
            # If your custom store returns 'Document' objects or 'dict' objects:
            final_results = []
            for res in results:
                # Check if this result matches our source filter (if filter is active)
                if source_filter:
                    doc_source = getattr(res, 'metadata', {}).get('source') if hasattr(res, 'metadata') else None
                    if doc_source != source_filter:
                        continue # Skip if it's from the wrong file
                
                # Format the output for the Researcher Node
                if hasattr(res, 'page_content'):
                    source_name = res.metadata.get('source', 'Unknown')
                    final_results.append(f"Source [{source_name}]: {res.page_content}")
                else:
                    final_results.append(str(res))

            return final_results
            
        except Exception as e:
            print(f"[Retriever] Error during search: {e}")
            return []

# Singleton instance
vector_service = VectorService()

def retrieve(query: str, top_k: int = 3, source: str = None) -> list:
    """
    Synchronous retrieval wrapper used by the Researcher Node.
    Now supports an optional 'source' parameter.
    """
    return vector_service.retrieve(query, top_k=top_k, source_filter=source)