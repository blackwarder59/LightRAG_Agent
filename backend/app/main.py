"""
LightRAG Agent FastAPI Application

A FastAPI backend for the LightRAG conversational agent with document processing,
knowledge graph construction, and real-time chat capabilities.

This implementation follows patterns from the ottomator-agents light-rag-agent example
and integrates with the HKUDS/LightRAG repository for core functionality.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.config.settings import settings
from app.routers import chat, documents, knowledge_base
from app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events.
    
    This handles:
    - Application startup initialization
    - Database connections
    - Redis connections  
    - LightRAG initialization
    - Cleanup on shutdown
    """
    # Startup
    logger.info("Starting LightRAG Agent application...")
    
    # Initialize logging
    setup_logging()
    
    # Initialize database connections
    # TODO: Initialize Neo4j connection
    # TODO: Initialize Redis connection
    # TODO: Initialize LightRAG service
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down LightRAG Agent application...")
    # TODO: Close database connections
    # TODO: Cleanup resources
    logger.info("Application shutdown complete")


# Create FastAPI application instance
app = FastAPI(
    title="LightRAG Agent API",
    description="A conversational AI agent powered by LightRAG for document-based knowledge graphs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error response format."""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions with error logging."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify the application is running.
    
    Returns:
        Dict containing application status and version
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "lightrag-agent",
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint with basic application information.
    
    Returns:
        Dict containing welcome message and API documentation links
    """
    return {
        "message": "Welcome to LightRAG Agent API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# Include API routers with correct prefixes
# Note: Routers already define their own prefixes, so we don't add them here
app.include_router(
    chat.router,
    tags=["Chat"]
)

app.include_router(
    documents.router,
    tags=["Documents"]
)

app.include_router(
    knowledge_base.router,
    tags=["Knowledge Base"]
)


# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(websocket, session_id: str):
    """
    WebSocket endpoint for real-time chat communication.
    
    Args:
        websocket: WebSocket connection
        session_id: Unique session identifier for the chat
    """
    # TODO: Implement WebSocket chat handler
    # This will be implemented in the chat router
    pass


if __name__ == "__main__":
    import uvicorn
    
    # Run the application using uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 