import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config import get_settings
from app.services.knowledge_base import KnowledgeBaseService
from app.tools.opening_hours import get_opening_hours
from app.tools.knowledge_query import query_knowledge_base

settings = get_settings()


def seed_knowledge_base():
    """Seed the knowledge base with city data on startup."""
    try:
        kb = KnowledgeBaseService()
        status = kb.get_status()

        if status["document_count"] > 0:
            print(f"Knowledge base already has {status['document_count']} documents, skipping seed.")
            return

        kb_path = settings.knowledge_base_path
        if not os.path.exists(kb_path):
            print(f"No knowledge base directory found at {kb_path}")
            return

        documents = []
        for root, dirs, files in os.walk(kb_path):
            for filename in files:
                if filename.endswith(".md"):
                    filepath = os.path.join(root, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    rel_path = os.path.relpath(filepath, kb_path)
                    category = os.path.dirname(rel_path) or "general"
                    doc_id = os.path.splitext(rel_path)[0].replace("/", "-").replace("\\", "-")

                    documents.append({
                        "id": doc_id,
                        "content": content,
                        "metadata": {
                            "category": category,
                            "filename": filename,
                            "source": rel_path,
                        },
                    })

        if documents:
            kb.add_documents(documents)
            print(f"Knowledge base seeded with {len(documents)} documents")
        else:
            print("No markdown files found to seed")

    except Exception as e:
        print(f"Warning: Failed to seed knowledge base: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("Starting CityVoice API...")
    seed_knowledge_base()
    yield
    print("Shutting down CityVoice API...")


app = FastAPI(
    title=settings.app_name,
    description="Voice AI Backend for CityVoice - Lüneburg City Services",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Basic Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "0.2.0",
        "status": "operational",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# =============================================================================
# Data Endpoints (for frontend display)
# =============================================================================

@app.get("/api/opening-hours")
async def get_opening_hours_data():
    """Get all opening hours data for frontend display."""
    from app.tools.opening_hours import load_opening_hours
    data = load_opening_hours()
    return JSONResponse(content=data)


@app.get("/api/knowledge/status")
async def knowledge_status():
    """Get knowledge base status."""
    kb = KnowledgeBaseService()
    return kb.get_status()


# =============================================================================
# ElevenLabs Webhook Endpoints (for Agent Tools)
# =============================================================================

class OpeningHoursRequest(BaseModel):
    """Request body for opening hours tool."""
    department: Optional[str] = None


class KnowledgeQueryRequest(BaseModel):
    """Request body for knowledge query tool."""
    query: str


@app.post("/api/tools/opening-hours")
async def tool_opening_hours(request: OpeningHoursRequest):
    """
    ElevenLabs webhook for opening hours tool.
    Called by the ElevenLabs agent when user asks about opening hours.
    """
    print(f"[Tool] Opening hours request: department={request.department}")

    result = get_opening_hours(request.department)

    print(f"[Tool] Opening hours result: {result[:100]}...")

    return {"result": result}


@app.post("/api/tools/knowledge-query")
async def tool_knowledge_query(request: KnowledgeQueryRequest):
    """
    ElevenLabs webhook for knowledge base query tool.
    Called by the ElevenLabs agent when user asks about city services.
    """
    print(f"[Tool] Knowledge query request: query={request.query}")

    result = query_knowledge_base(request.query)

    print(f"[Tool] Knowledge query result: {result[:100]}...")

    return {"result": result}


# =============================================================================
# Debugging Endpoints
# =============================================================================

@app.post("/api/test/opening-hours")
async def test_opening_hours(department: Optional[str] = None):
    """Test endpoint for opening hours tool."""
    result = get_opening_hours(department)
    return {"department": department, "result": result}


@app.post("/api/test/knowledge-query")
async def test_knowledge_query(query: str):
    """Test endpoint for knowledge query tool."""
    result = query_knowledge_base(query)
    return {"query": query, "result": result}
