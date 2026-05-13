"""
LegalBuddy Legal Assistant — FastAPI Backend
Serves the frontend and provides the /chat API endpoint
powered by the existing RAG pipeline.
"""

import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Path setup — so we can import rag_engine from the project root
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv(ROOT_DIR / ".env")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")

# ---------------------------------------------------------------------------
# RAG Engine initialisation
# ---------------------------------------------------------------------------
from rag_engine import LegalRAGEngine  # noqa: E402

rag_engine: LegalRAGEngine | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    global rag_engine
    try:
        print("⚙️  Initializing RAG Engine...")
        rag_engine = LegalRAGEngine(
            data_folder=str(ROOT_DIR / "data"),
            chroma_db_path=str(ROOT_DIR / "chroma_db"),
            model_name=OLLAMA_MODEL,
        )
        rag_engine.initialize()
        print("✅ RAG Engine ready!")
    except Exception as e:
        print(f"❌ RAG Engine failed to initialize: {e}")
        rag_engine = None
    yield
    # Shutdown — nothing to clean up
    print("👋 Shutting down LegalBuddy backend.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="LegalBuddy — Legal Assistant API",
    description="Backend API for the LegalBuddy legal assistant powered by RAG + Ollama.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow everything during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Health check — reports whether the RAG engine and Ollama are available."""
    import httpx

    rag_ok = rag_engine is not None
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            ollama_ok = resp.status_code == 200
    except Exception:
        ollama_ok = False

    status = "ok" if (rag_ok and ollama_ok) else "degraded"
    return {
        "status": status,
        "rag_engine": "ready" if rag_ok else "unavailable",
        "ollama": "connected" if ollama_ok else "disconnected",
        "model": OLLAMA_MODEL,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Accept a user question, run it through the RAG pipeline,
    and return the answer with source documents.
    """
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG Engine is not available. Please wait for initialisation or check server logs.",
        )

    query = req.query.strip()
    if len(query) < 3:
        raise HTTPException(status_code=400, detail="Query is too short. Please ask a more detailed question.")

    try:
        result = rag_engine.query(query)
        return ChatResponse(
            answer=result.get("answer", "I could not generate an answer. Please try rephrasing your question."),
            sources=result.get("sources", []),
        )
    except Exception as e:
        error_msg = str(e)
        # Provide user-friendly messages for common errors
        if "Connection refused" in error_msg or "ConnectError" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="Cannot connect to Ollama. Please make sure Ollama is running (ollama serve).",
            )
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your question: {error_msg}",
        )


# ---------------------------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------------------------
FRONTEND_DIR = ROOT_DIR / "frontend"


@app.get("/")
async def serve_index():
    """Serve the main frontend page."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(
        status_code=404,
        content={"error": "Frontend not found. Ensure /frontend/index.html exists."},
    )


@app.get("/style.css")
async def serve_css():
    """Serve the CSS stylesheet."""
    css_path = FRONTEND_DIR / "style.css"
    if css_path.exists():
        return FileResponse(str(css_path), media_type="text/css")
    return JSONResponse(status_code=404, content={"error": "style.css not found"})


@app.get("/app.js")
async def serve_js():
    """Serve the JavaScript bundle."""
    js_path = FRONTEND_DIR / "app.js"
    if js_path.exists():
        return FileResponse(str(js_path), media_type="application/javascript")
    return JSONResponse(status_code=404, content={"error": "app.js not found"})


# ---------------------------------------------------------------------------
# Run with: uvicorn backend.main:app --reload
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        reload=True,
    )
