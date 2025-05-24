"""
LightRAG Service

This service provides LightRAG functionality following the official HKUDS/LightRAG patterns.
Based on: https://github.com/HKUDS/LightRAG

Key Features:
- Official LightRAG initialization pattern
- Proper async storage management
- Pipeline status initialization
- Graph-based knowledge retrieval
- Incremental document updates
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Official LightRAG imports following their documentation
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import setup_logger

# Setup LightRAG logger as per official documentation
setup_logger("lightrag", level="INFO")
logger = logging.getLogger(__name__)

class LightRAGService:
    """
    LightRAG Service implementation following official HKUDS/LightRAG patterns.
    
    This service manages document insertion and knowledge graph querying using
    the official LightRAG framework patterns and best practices.
    """
    
    def __init__(self):
        """Initialize the LightRAG service with official configuration."""
        # Use absolute path for working directory as recommended
        self.working_dir = os.path.abspath("./backend/lightrag_data")
        self.rag: Optional[LightRAG] = None
        self._initialized = False
        
        # Ensure working directory exists
        os.makedirs(self.working_dir, exist_ok=True)
        
        logger.info(f"🚀 LightRAG Service initialized with working_dir: {self.working_dir}")
    
    async def initialize(self) -> bool:
        """
        Initialize LightRAG following the official pattern.
        
        Based on official documentation:
        https://github.com/HKUDS/LightRAG#a-simple-program
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if self._initialized and self.rag:
            logger.info("✅ LightRAG already initialized")
            return True
            
        try:
            logger.info("🔧 Initializing LightRAG with official pattern...")
            
            # Step 1: Create LightRAG instance with official configuration
            self.rag = LightRAG(
                working_dir=self.working_dir,
                embedding_func=openai_embed,                    # Official OpenAI embedding
                llm_model_func=gpt_4o_mini_complete,           # Official LLM function
                # Optional: Add storage configurations if needed
                # vector_storage="ChromaVectorDBStorage",      # Can specify different storage
                # graph_storage="Neo4JStorage",                # Can use Neo4j if configured
            )
            
            # Step 2: Initialize storages (CRITICAL - from official docs)
            logger.info("📊 Initializing LightRAG storages...")
            await self.rag.initialize_storages()
            
            # Step 3: Initialize pipeline status (CRITICAL - from official docs)
            logger.info("⚙️ Initializing pipeline status...")
            await initialize_pipeline_status()
            
            self._initialized = True
            logger.info("✅ LightRAG initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ LightRAG initialization failed: {e}")
            logger.exception("Full initialization error traceback:")
            self.rag = None
            self._initialized = False
            return False
    
    async def insert_document(self, content: str, document_id: str) -> bool:
        """
        Insert a document into LightRAG using official pattern.
        
        Args:
            content: Document text content
            document_id: Unique document identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure LightRAG is initialized
            if not await self.initialize():
                logger.error("❌ Cannot insert document - LightRAG initialization failed")
                return False
            
            logger.info(f"📄 Inserting document: {document_id}")
            logger.info(f"   • Content length: {len(content):,} characters")
            
            # Use official LightRAG async insert method to avoid event loop conflicts
            # This handles all the graph construction, entity extraction, etc.
            await self.rag.ainsert(content)
            
            logger.info(f"✅ Document {document_id} inserted successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to insert document {document_id}: {e}")
            logger.exception("Full insert error traceback:")
            return False
    
    async def query_knowledge_graph(
        self, 
        query: str, 
        mode: str = "hybrid",
        **kwargs
    ) -> str:
        """
        Query the LightRAG knowledge graph using official pattern.
        
        Args:
            query: User query string
            mode: Query mode - "local", "global", "hybrid", "naive", "mix"
            **kwargs: Additional query parameters
            
        Returns:
            str: Generated response or error message
        """
        try:
            # Ensure LightRAG is initialized
            if not await self.initialize():
                logger.error("❌ Cannot query - LightRAG initialization failed")
                return "I apologize, but the knowledge system is not available right now."
            
            logger.info(f"🔍 Querying LightRAG with mode '{mode}': {query[:100]}...")
            
            # Create QueryParam with official pattern
            query_param = QueryParam(mode=mode)
            
            # Use official async query method (aquery for proper async operation)
            response = await self.rag.aquery(query, param=query_param)
            
            logger.info(f"✅ Query completed successfully (response length: {len(response)} chars)")
            return response
            
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            logger.exception("Full query error traceback:")
            return f"I encountered an error while processing your query: {str(e)}"
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the LightRAG knowledge base.
        
        Returns:
            Dict containing system statistics
        """
        try:
            stats = {
                "initialized": self._initialized,
                "working_dir": self.working_dir,
                "working_dir_exists": os.path.exists(self.working_dir),
                "files_in_working_dir": [],
            }
            
            if os.path.exists(self.working_dir):
                stats["files_in_working_dir"] = os.listdir(self.working_dir)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {"error": str(e)}
    
    async def finalize(self):
        """
        Properly finalize LightRAG following official pattern.
        
        This should be called when shutting down the service.
        """
        try:
            if self.rag:
                logger.info("🔄 Finalizing LightRAG storages...")
                await self.rag.finalize_storages()
                self.rag = None
                self._initialized = False
                logger.info("✅ LightRAG finalized successfully")
        except Exception as e:
            logger.error(f"❌ Error during finalization: {e}")

# Global service instance following singleton pattern
lightrag_service = LightRAGService()

# Convenience functions for easy access
async def initialize_lightrag() -> bool:
    """Initialize the global LightRAG service."""
    return await lightrag_service.initialize()

async def insert_document(content: str, document_id: str) -> bool:
    """Insert a document into the global LightRAG service."""
    return await lightrag_service.insert_document(content, document_id)

async def query_knowledge_graph(query: str, mode: str = "hybrid") -> str:
    """Query the global LightRAG knowledge graph."""
    return await lightrag_service.query_knowledge_graph(query, mode)

async def get_lightrag_stats() -> Dict[str, Any]:
    """Get statistics from the global LightRAG service."""
    return await lightrag_service.get_stats()

async def finalize_lightrag():
    """Finalize the global LightRAG service."""
    await lightrag_service.finalize() 