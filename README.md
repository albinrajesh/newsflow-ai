# Newsflow AI v2: Agentic Research Engine

Newsflow AI is a sophisticated **Agentic RAG (Retrieval-Augmented Generation)** platform designed to transform raw data from PDFs and YouTube transcripts into structured, verified intelligence. 

Unlike standard RAG pipelines, Newsflow AI uses a **Directed Acyclic Graph (DAG)** to plan, retrieve, grade, and synthesize information, ensuring zero hallucinations and high contextual accuracy.

## 🚀 Core Features
* **Agentic Workflow:** Powered by **LangGraph**, the system utilizes a "Planner" node to decompose complex queries and a "Grader" node to filter irrelevant context.
* **Multi-Source Ingestion:** Seamlessly ingest and vectorise data from local PDF files and YouTube URLs.
* **Production-Ready Backend:** Built with **FastAPI** using asynchronous streaming for real-time token delivery.
* **Local-First Intelligence:** Optimized for **Ollama (Mistral/Llama3)** to ensure data privacy and "Sovereign AI" deployment.
* **Vector Architecture:** High-performance similarity search using **FAISS** with metadata-aware filtering to prevent context mixing.

## 🛠️ Tech Stack
* **Orchestration:** LangGraph / LangChain
* **API Framework:** FastAPI (Python 3.11+)
* **Vector Database:** FAISS
* **LLM Provider:** Ollama (Local) / Gemini API
* **Frontend:** HTML5/JavaScript (Streaming Fetch API)
* **Processing:** PyPDF, YouTube-Transcript-API, Docker

## 🏗️ System Architecture
1.  **Planner:** Breaks down user intent into atomic sub-questions.
2.  **Researcher:** Parallelized retrieval from local FAISS index and Web Search (MCP).
3.  **Grader:** Evaluates document relevance to prevent noisy synthesization.
4.  **Synthesizer:** Generates the final grounded response with source citations.

## 📦 Installation & Setup
```bash
# Clone the repository
git clone [https://github.com/your-username/newsflow-ai-v2.git](https://github.com/your-username/newsflow-ai-v2.git)

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python -m app.main
