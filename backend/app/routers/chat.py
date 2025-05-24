"""
Chat API Router

This router handles chat interactions with the LightRAG knowledge graph
using the official HKUDS/LightRAG patterns for reliable query processing.

Features:
- Knowledge graph queries using multiple modes
- Official LightRAG query processing
- Simple and reliable chat interface
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ..services.lightrag_service import query_knowledge_graph

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    """Request model for chat queries."""
    message: str
    mode: str = "hybrid"  # local, global, hybrid, naive, mix

class ChatResponse(BaseModel):
    """Response model for chat queries."""
    response: str
    mode: str
    success: bool

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest) -> ChatResponse:
    """
    Process a chat query using LightRAG knowledge graph.
    
    This endpoint queries the LightRAG knowledge graph using the official
    patterns and returns an AI-generated response based on the stored knowledge.
    
    Args:
        request: Chat request containing message and query mode
        
    Returns:
        ChatResponse with the generated answer
    """
    try:
        logger.info(f"🔍 Processing chat query with mode '{request.mode}': {request.message[:100]}...")
        
        # Validate query mode
        valid_modes = ["local", "global", "hybrid", "naive", "mix"]
        if request.mode not in valid_modes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid query mode. Must be one of: {valid_modes}"
            )
        
        # Query LightRAG using official pattern
        response = await query_knowledge_graph(
            query=request.message,
            mode=request.mode
        )
        
        logger.info(f"✅ Chat query completed successfully (response length: {len(response)} chars)")
        
        return ChatResponse(
            response=response,
            mode=request.mode,
            success=True
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"❌ Chat query failed: {e}")
        logger.exception("Full chat query error traceback:")
        
        # Return error response instead of raising exception
        return ChatResponse(
            response=f"I apologize, but I encountered an error processing your request: {str(e)}",
            mode=request.mode,
            success=False
        )

@router.get("/health")
async def chat_health() -> Dict[str, Any]:
    """
    Check the health status of the chat service.
    
    Returns:
        Health status information
    """
    try:
        # Import here to avoid circular imports
        from ..services.lightrag_service import get_lightrag_stats
        
        stats = await get_lightrag_stats()
        
        return {
            "status": "healthy",
            "service": "chat",
            "lightrag_stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Chat health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "chat",
            "error": str(e)
        } 