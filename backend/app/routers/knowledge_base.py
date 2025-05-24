"""
Knowledge Base API Router

This module handles knowledge base management including:
- Creating and managing multiple knowledge bases
- Knowledge base statistics and analytics
- Export/import functionality
- Graph visualization endpoints
"""

import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from app.config.settings import settings
from app.services.lightrag_service import lightrag_service, LightRAGService


# Pydantic models for request/response validation
class KnowledgeBaseInfo(BaseModel):
    """Knowledge base information model."""
    id: str
    name: str
    description: Optional[str] = None
    created_date: str
    last_updated: str
    document_count: int = 0
    entity_count: int = 0
    relationship_count: int = 0
    status: str  # active, inactive, processing


class KnowledgeBaseCreateRequest(BaseModel):
    """Request model for creating a knowledge base."""
    name: str
    description: Optional[str] = None


class KnowledgeBaseUpdateRequest(BaseModel):
    """Request model for updating a knowledge base."""
    name: Optional[str] = None
    description: Optional[str] = None


class KnowledgeBaseListResponse(BaseModel):
    """Response model for knowledge base listing."""
    knowledge_bases: List[KnowledgeBaseInfo]
    total_count: int


class KnowledgeBaseStats(BaseModel):
    """Knowledge base statistics model."""
    id: str
    name: str
    total_documents: int
    total_entities: int
    total_relationships: int
    total_size_mb: float
    last_query_date: Optional[str] = None
    query_count: int = 0
    most_common_entities: List[Dict[str, Any]] = []
    recent_documents: List[str] = []


class GraphVisualizationData(BaseModel):
    """Graph visualization data model."""
    nodes: List[Dict]
    edges: List[Dict]
    metadata: Dict


# Create router instance
router = APIRouter()

# In-memory storage for knowledge base information (replace with database in production)
knowledge_bases_db: Dict[str, KnowledgeBaseInfo] = {}


@router.post("/", response_model=KnowledgeBaseInfo)
async def create_knowledge_base(request: KnowledgeBaseCreateRequest) -> KnowledgeBaseInfo:
    """
    Create a new knowledge base.
    
    Args:
        request: Knowledge base creation request
        
    Returns:
        KnowledgeBaseInfo containing the created knowledge base information
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        # Generate unique knowledge base ID
        kb_id = str(uuid.uuid4())
        
        # Create knowledge base info
        now = datetime.now().isoformat()
        kb_info = KnowledgeBaseInfo(
            id=kb_id,
            name=request.name,
            description=request.description,
            created_date=now,
            last_updated=now,
            document_count=0,
            entity_count=0,
            relationship_count=0,
            status="active"
        )
        
        # Store in database
        knowledge_bases_db[kb_id] = kb_info
        
        logger.info(f"Knowledge base created: {kb_id} ({request.name})")
        
        return kb_info
        
    except Exception as e:
        logger.error(f"Error creating knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Failed to create knowledge base")


@router.get("/", response_model=KnowledgeBaseListResponse)
async def list_knowledge_bases() -> KnowledgeBaseListResponse:
    """
    List all knowledge bases.
    
    Returns:
        KnowledgeBaseListResponse containing all knowledge bases
    """
    try:
        knowledge_bases = list(knowledge_bases_db.values())
        
        # Sort by creation date (newest first)
        knowledge_bases.sort(key=lambda x: x.created_date, reverse=True)
        
        return KnowledgeBaseListResponse(
            knowledge_bases=knowledge_bases,
            total_count=len(knowledge_bases)
        )
        
    except Exception as e:
        logger.error(f"Error listing knowledge bases: {e}")
        raise HTTPException(status_code=500, detail="Failed to list knowledge bases")


@router.get("/{kb_id}", response_model=KnowledgeBaseInfo)
async def get_knowledge_base(kb_id: str) -> KnowledgeBaseInfo:
    """
    Get information about a specific knowledge base.
    
    Args:
        kb_id: Knowledge base ID
        
    Returns:
        KnowledgeBaseInfo containing knowledge base details
        
    Raises:
        HTTPException: If knowledge base is not found
    """
    try:
        if kb_id not in knowledge_bases_db:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        return knowledge_bases_db[kb_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting knowledge base {kb_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get knowledge base")


@router.put("/{kb_id}", response_model=KnowledgeBaseInfo)
async def update_knowledge_base(kb_id: str, request: KnowledgeBaseUpdateRequest) -> KnowledgeBaseInfo:
    """
    Update a knowledge base.
    
    Args:
        kb_id: Knowledge base ID
        request: Update request with new information
        
    Returns:
        KnowledgeBaseInfo containing updated knowledge base information
        
    Raises:
        HTTPException: If knowledge base is not found or update fails
    """
    try:
        if kb_id not in knowledge_bases_db:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        kb_info = knowledge_bases_db[kb_id]
        
        # Update fields if provided
        if request.name is not None:
            kb_info.name = request.name
        if request.description is not None:
            kb_info.description = request.description
        
        # Update timestamp
        kb_info.last_updated = datetime.now().isoformat()
        
        logger.info(f"Knowledge base updated: {kb_id}")
        
        return kb_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating knowledge base {kb_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update knowledge base")


@router.delete("/{kb_id}")
async def delete_knowledge_base(kb_id: str) -> Dict[str, str]:
    """
    Delete a knowledge base and all associated data.
    
    Args:
        kb_id: Knowledge base ID
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If knowledge base is not found or deletion fails
    """
    try:
        if kb_id not in knowledge_bases_db:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        # TODO: Implement cleanup of associated data
        # - Remove all documents from this knowledge base
        # - Remove from vector database
        # - Remove from graph database
        # - Clean up any background processing tasks
        
        # Remove from knowledge bases database
        del knowledge_bases_db[kb_id]
        
        logger.info(f"Knowledge base deleted: {kb_id}")
        
        return {"message": f"Knowledge base {kb_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge base {kb_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete knowledge base")


@router.get("/{kb_id}/stats", response_model=KnowledgeBaseStats)
async def get_knowledge_base_stats(kb_id: str) -> KnowledgeBaseStats:
    """
    Get detailed statistics for a knowledge base using LightRAG.
    
    Args:
        kb_id: Knowledge base ID
        
    Returns:
        KnowledgeBaseStats containing detailed statistics from LightRAG
        
    Raises:
        HTTPException: If knowledge base is not found
    """
    try:
        if kb_id not in knowledge_bases_db:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        kb_info = knowledge_bases_db[kb_id]
        
        # Get real statistics from LightRAG
        try:
            lightrag_stats = await lightrag_service.get_knowledge_graph_stats()
            
            # Calculate storage size from cache files
            total_size_mb = 0.0
            cache_size = lightrag_stats.get("cache_size", 0)
            if cache_size > 0:
                total_size_mb = cache_size / (1024 * 1024)  # Convert bytes to MB
            
            # Get document count from our documents database
            from .documents import documents_db
            total_documents = len([doc for doc in documents_db.values() if doc.status == "completed"])
            
            # Extract storage backend information
            storage_backends = lightrag_stats.get("storage_backends", {})
            
            stats = KnowledgeBaseStats(
                id=kb_id,
                name=kb_info.name,
                total_documents=total_documents,
                total_entities=0,  # LightRAG doesn't expose entity count directly
                total_relationships=0,  # LightRAG doesn't expose relationship count directly
                total_size_mb=round(total_size_mb, 2),
                last_query_date=None,  # Could be tracked separately
                query_count=0,  # Could be tracked separately
                most_common_entities=[
                    # Note: LightRAG doesn't provide entity frequency data directly
                    # This would require custom analysis of the knowledge graph
                ],
                recent_documents=[
                    doc.filename for doc in sorted(
                        [d for d in documents_db.values() if d.status == "completed"],
                        key=lambda x: x.upload_date,
                        reverse=True
                    )[:5]  # Last 5 processed documents
                ]
            )
            
            # Update KB info with current document count
            kb_info.document_count = total_documents
            kb_info.last_updated = datetime.now().isoformat()
            
            logger.info(f"📊 Knowledge base stats generated for {kb_id}")
            logger.info(f"   Documents: {total_documents}, Size: {total_size_mb:.2f}MB")
            logger.info(f"   Storage: {storage_backends}")
            
            return stats
            
        except Exception as e:
            logger.warning(f"Could not get LightRAG stats: {e}")
            
            # Fallback to basic stats if LightRAG is not available
            stats = KnowledgeBaseStats(
                id=kb_id,
                name=kb_info.name,
                total_documents=kb_info.document_count,
                total_entities=0,
                total_relationships=0,
                total_size_mb=0.0,
                last_query_date=None,
                query_count=0,
                most_common_entities=[],
                recent_documents=[]
            )
            
            return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats for knowledge base {kb_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get knowledge base statistics")


@router.get("/{kb_id}/export")
async def export_knowledge_base(kb_id: str, format: str = "json") -> Dict:
    """
    Export a knowledge base in the specified format.
    
    Args:
        kb_id: Knowledge base ID
        format: Export format (json, csv, graphml)
        
    Returns:
        Exported knowledge base data
        
    Raises:
        HTTPException: If knowledge base is not found or export fails
    """
    try:
        if kb_id not in knowledge_bases_db:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        # TODO: Implement actual export functionality
        # - Query all entities and relationships
        # - Format according to requested format
        # - Include metadata and statistics
        
        # For now, return placeholder data
        export_data = {
            "knowledge_base_id": kb_id,
            "export_format": format,
            "export_date": datetime.now().isoformat(),
            "entities": [],
            "relationships": [],
            "metadata": knowledge_bases_db[kb_id].dict()
        }
        
        logger.info(f"Knowledge base exported: {kb_id} (format: {format})")
        
        return export_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting knowledge base {kb_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to export knowledge base")


@router.post("/{kb_id}/import")
async def import_knowledge_base(kb_id: str, data: Dict) -> Dict[str, str]:
    """
    Import data into a knowledge base.
    
    Args:
        kb_id: Knowledge base ID
        data: Import data in supported format
        
    Returns:
        Import status message
        
    Raises:
        HTTPException: If knowledge base is not found or import fails
    """
    try:
        if kb_id not in knowledge_bases_db:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        # TODO: Implement actual import functionality
        # - Validate import data format
        # - Parse entities and relationships
        # - Update vector database
        # - Update graph database
        # - Update knowledge base statistics
        
        logger.info(f"Data imported to knowledge base: {kb_id}")
        
        return {"message": f"Data imported successfully to knowledge base {kb_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing to knowledge base {kb_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to import data")


@router.get("/{kb_id}/visualize", response_model=GraphVisualizationData)
async def get_graph_visualization(
    kb_id: str,
    max_nodes: int = 100,
    entity_type: Optional[str] = None
) -> GraphVisualizationData:
    """
    Get graph visualization data for a knowledge base.
    
    Args:
        kb_id: Knowledge base ID
        max_nodes: Maximum number of nodes to return
        entity_type: Filter by entity type (optional)
        
    Returns:
        GraphVisualizationData containing nodes and edges for visualization
        
    Raises:
        HTTPException: If knowledge base is not found or visualization fails
    """
    try:
        if kb_id not in knowledge_bases_db:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        if not settings.ENABLE_GRAPH_VISUALIZATION:
            raise HTTPException(status_code=404, detail="Graph visualization is disabled")
        
        # TODO: Implement actual graph data retrieval
        # - Query graph database for entities and relationships
        # - Apply filters (entity_type, max_nodes)
        # - Format for visualization library (e.g., D3.js, vis.js)
        # - Include node positions and styling information
        
        # For now, return placeholder data
        visualization_data = GraphVisualizationData(
            nodes=[
                {"id": "1", "label": "Sample Entity 1", "type": "Person", "size": 10},
                {"id": "2", "label": "Sample Entity 2", "type": "Organization", "size": 15}
            ],
            edges=[
                {"from": "1", "to": "2", "label": "works_for", "weight": 1.0}
            ],
            metadata={
                "total_nodes": 2,
                "total_edges": 1,
                "layout": "force-directed",
                "filters_applied": {"entity_type": entity_type} if entity_type else {}
            }
        )
        
        logger.info(f"Graph visualization data generated for KB: {kb_id}")
        
        return visualization_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating visualization for {kb_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate graph visualization") 