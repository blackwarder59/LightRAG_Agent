"""
Application Settings Configuration

This module manages all configuration settings for the LightRAG Agent application,
including environment variables, database connections, and API configurations.
Uses Pydantic Settings for type validation and environment variable loading.
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    All settings can be overridden via environment variables.
    Example: DATABASE_URL=postgresql://... python app.py
    """
    
    # Application settings
    APP_NAME: str = Field(default="LightRAG Agent", description="Application name")
    VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: str = Field(default="development", description="Environment (development, production, testing)")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    
    # Server configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    # Database settings
    NEO4J_URI: str = Field(default="bolt://localhost:7687", description="Neo4j database URI")
    NEO4J_USER: str = Field(default="neo4j", description="Neo4j username")
    NEO4J_PASSWORD: str = Field(default="password", description="Neo4j password")
    NEO4J_DATABASE: str = Field(default="neo4j", description="Neo4j database name")
    
    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    
    # OpenAI API settings
    OPENAI_API_KEY: str = Field(description="OpenAI API key for LLM and embeddings")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="OpenAI model for text generation")
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small", 
        description="OpenAI model for embeddings"
    )
    OPENAI_MAX_TOKENS: int = Field(default=4096, description="Maximum tokens for OpenAI responses")
    OPENAI_TEMPERATURE: float = Field(default=0.7, description="Temperature for OpenAI responses")
    
    # Anthropic API settings (optional)
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API key")
    ANTHROPIC_MODEL: str = Field(default="claude-3-5-sonnet-20241022", description="Anthropic model")
    
    # LightRAG configuration
    LIGHTRAG_WORKING_DIR: str = Field(default="./lightrag_data", description="LightRAG working directory")
    LIGHTRAG_MODEL: str = Field(default="gpt-4o-mini", description="LightRAG model for processing")
    LIGHTRAG_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small", 
        description="LightRAG embedding model"
    )
    LIGHTRAG_MAX_ASYNC: int = Field(default=4, description="Maximum async operations for LightRAG")
    LIGHTRAG_MAX_TOKENS: int = Field(default=32768, description="Maximum tokens for LightRAG")
    
    # Document processing settings
    CHUNK_SIZE: int = Field(default=512, description="Text chunk size for processing")
    CHUNK_OVERLAP: int = Field(default=50, description="Overlap between text chunks")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="Maximum upload size (10MB)")
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[".docx", ".pdf", ".txt", ".md"],
        description="Allowed file types for upload"
    )
    UPLOAD_DIR: str = Field(default="./uploads", description="Directory for uploaded files")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Log format"
    )
    LOG_FILE: Optional[str] = Field(default="logs/app.log", description="Log file path")
    
    # Security settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production", 
        description="Secret key for JWT and encryption"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration time")
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per minute")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    # WebSocket settings
    WS_MAX_CONNECTIONS: int = Field(default=100, description="Maximum WebSocket connections")
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, description="WebSocket heartbeat interval")
    
    # Vector database settings
    VECTOR_DB_TYPE: str = Field(default="chroma", description="Vector database type (chroma, faiss)")
    CHROMA_PERSIST_DIR: str = Field(default="./chroma_db", description="ChromaDB persistence directory")
    CHROMA_COLLECTION_NAME: str = Field(default="lightrag", description="ChromaDB collection name")
    
    # Knowledge graph settings
    ENABLE_GRAPH_VISUALIZATION: bool = Field(default=True, description="Enable graph visualization endpoints")
    MAX_GRAPH_NODES: int = Field(default=1000, description="Maximum nodes in graph visualization")
    
    # Cache settings
    CACHE_TTL: int = Field(default=3600, description="Cache TTL in seconds")
    ENABLE_QUERY_CACHE: bool = Field(default=True, description="Enable query result caching")
    
    # Background task settings
    CELERY_BROKER_URL: Optional[str] = Field(default=None, description="Celery broker URL for background tasks")
    CELERY_RESULT_BACKEND: Optional[str] = Field(default=None, description="Celery result backend")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
        
    def __init__(self, **kwargs):
        """Initialize settings and create necessary directories."""
        super().__init__(**kwargs)
        
        # Create necessary directories
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.LIGHTRAG_WORKING_DIR, exist_ok=True)
        os.makedirs(self.CHROMA_PERSIST_DIR, exist_ok=True)
        
        # Create logs directory if log file is specified
        if self.LOG_FILE:
            log_dir = os.path.dirname(self.LOG_FILE)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

    @property
    def database_url(self) -> str:
        """Get formatted database URL for SQLAlchemy."""
        return f"neo4j://{self.NEO4J_USER}:{self.NEO4J_PASSWORD}@{self.NEO4J_URI.replace('bolt://', '')}"
    
    @property
    def redis_config(self) -> dict:
        """Get Redis configuration dictionary."""
        config = {
            "url": self.REDIS_URL,
            "db": self.REDIS_DB,
            "decode_responses": True
        }
        if self.REDIS_PASSWORD:
            config["password"] = self.REDIS_PASSWORD
        return config
    
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins, handling both string and list formats."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS
    
    def get_openai_config(self) -> dict:
        """Get OpenAI configuration dictionary."""
        return {
            "api_key": self.OPENAI_API_KEY,
            "model": self.OPENAI_MODEL,
            "embedding_model": self.OPENAI_EMBEDDING_MODEL,
            "max_tokens": self.OPENAI_MAX_TOKENS,
            "temperature": self.OPENAI_TEMPERATURE
        }
    
    def get_lightrag_config(self) -> dict:
        """Get LightRAG configuration dictionary."""
        return {
            "working_dir": self.LIGHTRAG_WORKING_DIR,
            "llm_model": self.LIGHTRAG_MODEL,
            "embedding_model": self.LIGHTRAG_EMBEDDING_MODEL,
            "max_async": self.LIGHTRAG_MAX_ASYNC,
            "max_tokens": self.LIGHTRAG_MAX_TOKENS,
            "chunk_size": self.CHUNK_SIZE,
            "chunk_overlap": self.CHUNK_OVERLAP
        }
    
    @property
    def lightrag_data_dir(self) -> str:
        """Get LightRAG data directory path."""
        return self.LIGHTRAG_WORKING_DIR
    
    @property
    def neo4j_uri(self) -> str:
        """Get Neo4j URI."""
        return self.NEO4J_URI
    
    @property
    def neo4j_username(self) -> str:
        """Get Neo4j username."""
        return self.NEO4J_USER
    
    @property
    def neo4j_password(self) -> str:
        """Get Neo4j password."""
        return self.NEO4J_PASSWORD
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL."""
        return self.REDIS_URL
    
    @property
    def chromadb_host(self) -> str:
        """Get ChromaDB host (for compatibility)."""
        return "localhost"  # ChromaDB is local in our setup


# Create global settings instance
settings = Settings() 