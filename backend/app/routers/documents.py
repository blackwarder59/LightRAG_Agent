"""
Document Upload and Processing Router

This router handles document upload, text extraction, and LightRAG processing
using the official HKUDS/LightRAG patterns for reliable knowledge graph construction.

Features:
- File upload with multiple format support
- Text extraction and preprocessing  
- Official LightRAG document insertion
- Document status tracking and retrieval
"""

import logging
import uuid
from typing import List, Dict, Any
from pathlib import Path
import mimetypes

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel

from ..services.text_extraction_service import extract_text_from_file
from ..services.lightrag_service import insert_document

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

# In-memory document store (replace with database in production)
documents_db: Dict[str, Dict[str, Any]] = {}

class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    id: str
    filename: str
    content_type: str
    size: int
    text_length: int
    status: str
    message: str

class DocumentInfo(BaseModel):
    """Model for document information."""
    id: str
    filename: str
    content_type: str
    size: int
    text_length: int
    status: str
    upload_time: str

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    """
    Upload and process a document through LightRAG using official patterns.
    
    This endpoint:
    1. Validates and extracts text from uploaded files
    2. Processes content through official LightRAG insertion
    3. Returns processing status and document information
    
    Args:
        file: Uploaded file (PDF, DOCX, TXT, etc.)
        
    Returns:
        DocumentUploadResponse with processing results
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    # Generate unique document ID
    document_id = str(uuid.uuid4())
    
    try:
        logger.info(f"📤 Processing upload: {file.filename} (ID: {document_id})")
        
        # Step 1: Read and validate file
        logger.info(f"📄 Reading file content...")
        
        file_content = await file.read()
        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded"
            )
        
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        file_size = len(file_content)
        
        logger.info(f"   • File size: {file_size:,} bytes")
        logger.info(f"   • Content type: {content_type}")
        
        # Step 2: Extract text content
        logger.info(f"🔤 Extracting text content...")
        
        text_content = extract_text_from_file(file_content, file.filename)
        if not text_content or not text_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content could be extracted from the file"
            )
        
        # Clean and prepare text
        cleaned_text = text_content.strip()
        text_length = len(cleaned_text)
        
        logger.info(f"   • Extracted text length: {text_length:,} characters")
        
        # Step 3: Store document metadata
        from datetime import datetime
        
        document_info = {
            "id": document_id,
            "filename": file.filename,
            "content_type": content_type,
            "size": file_size,
            "text_length": text_length,
            "status": "processing",
            "upload_time": datetime.utcnow().isoformat(),
            "text_content": cleaned_text
        }
        
        documents_db[document_id] = document_info
        
        # Step 4: Process through LightRAG using official pattern
        logger.info(f"🚀 Processing through LightRAG...")
        
        success = await insert_document(cleaned_text, document_id)
        
        if success:
            document_info["status"] = "completed"
            message = "Document successfully processed and added to knowledge base"
            logger.info(f"✅ Document {document_id} processed successfully!")
        else:
            document_info["status"] = "failed"
            message = "Document processing failed - please try again"
            logger.error(f"❌ Document {document_id} processing failed")
        
        documents_db[document_id] = document_info
        
        return DocumentUploadResponse(
            id=document_id,
            filename=file.filename,
            content_type=content_type,
            size=file_size,
            text_length=text_length,
            status=document_info["status"],
            message=message
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error processing {file.filename}: {e}")
        logger.exception("Full upload error traceback:")
        
        # Update document status if it was created
        if document_id in documents_db:
            documents_db[document_id]["status"] = "error"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

@router.get("/", response_model=List[DocumentInfo])
async def list_documents() -> List[DocumentInfo]:
    """
    Get a list of all uploaded documents with their status.
    
    Returns:
        List of document information including processing status
    """
    try:
        logger.info(f"📋 Listing {len(documents_db)} documents")
        
        documents = []
        for doc_data in documents_db.values():
            # Don't include text content in the list response
            doc_info = {k: v for k, v in doc_data.items() if k != "text_content"}
            documents.append(DocumentInfo(**doc_info))
        
        return documents
        
    except Exception as e:
        logger.error(f"❌ Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document list"
        )

@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(document_id: str) -> DocumentInfo:
    """
    Get information about a specific document.
    
    Args:
        document_id: Unique document identifier
        
    Returns:
        Document information and status
    """
    try:
        if document_id not in documents_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = documents_db[document_id]
        # Don't include text content in the response
        doc_info = {k: v for k, v in doc_data.items() if k != "text_content"}
        
        return DocumentInfo(**doc_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document information"
        )

@router.get("/{document_id}/status")
async def get_document_status(document_id: str) -> Dict[str, Any]:
    """
    Get the current processing status of a document.
    
    Args:
        document_id: Unique document identifier
        
    Returns:
        Document status information
    """
    try:
        if document_id not in documents_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        doc_data = documents_db[document_id]
        
        return {
            "document_id": document_id,
            "filename": doc_data["filename"],
            "status": doc_data["status"],
            "upload_time": doc_data["upload_time"],
            "text_length": doc_data["text_length"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting status for document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document status"
        )

@router.delete("/{document_id}")
async def delete_document(document_id: str) -> Dict[str, str]:
    """
    Delete a document from the system.
    
    Args:
        document_id: Unique document identifier
        
    Returns:
        Deletion confirmation
    """
    try:
        if document_id not in documents_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        filename = documents_db[document_id]["filename"]
        del documents_db[document_id]
        
        logger.info(f"🗑️ Deleted document: {filename} (ID: {document_id})")
        
        return {
            "message": f"Document {filename} deleted successfully",
            "document_id": document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document"
        ) 