"""
Document management API endpoints
Handles document upload, processing, and management
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List
import io

from app.models.document import Document, DocumentUploadResponse, DocumentSearchResult
from app.core.auth import get_current_user
from app.services.document_service import document_service

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    chatbot_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process a document for a chatbot"""
    try:
        # Validate file upload
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Read file content
        file_content = await file.read()
        file_io = io.BytesIO(file_content)
        
        # Upload and process document
        result = await document_service.upload_document(
            file=file_io,
            filename=file.filename,
            chatbot_id=chatbot_id,
            user_id=current_user["id"]
        )
        
        return DocumentUploadResponse(
            id=result["id"],
            filename=result["filename"],
            file_type=result["file_type"],
            file_size=result["file_size"],
            processed=result["processed"],
            text_length=result.get("text_length"),
            message=f"Document '{file.filename}' uploaded and processed successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {str(e)}"
        )


@router.get("/chatbot/{chatbot_id}", response_model=List[Document])
async def list_documents(
    chatbot_id: str,
    current_user: dict = Depends(get_current_user)
):
    """List all documents for a chatbot"""
    try:
        documents = await document_service.list_documents(
            chatbot_id=chatbot_id,
            user_id=current_user["id"]
        )
        return documents
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific document"""
    try:
        document = await document_service.get_document(
            document_id=document_id,
            user_id=current_user["id"]
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a document and its embeddings"""
    try:
        success = await document_service.delete_document(
            document_id=document_id,
            user_id=current_user["id"]
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied"
            )
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.post("/search/{chatbot_id}", response_model=List[DocumentSearchResult])
async def search_documents(
    chatbot_id: str,
    query: str = Form(...),
    limit: int = Form(10),
    current_user: dict = Depends(get_current_user)
):
    """Search documents by content similarity"""
    try:
        from app.services.vector_store_service import vector_store_service
        
        # Verify chatbot ownership
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        chatbot_response = supabase.table("chatbots") \
            .select("id") \
            .eq("id", chatbot_id) \
            .eq("user_id", current_user["id"]) \
            .execute()
        
        if not chatbot_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Perform search
        results = await vector_store_service.search_documents(
            query=query,
            chatbot_id=chatbot_id,
            limit=limit
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append(DocumentSearchResult(
                content=result.get("content", ""),
                document_id=result.get("document_id", ""),
                similarity=result.get("similarity", 0.0),
                metadata=result.get("metadata", {}),
                document_info=result.get("document_info", {})
            ))
        
        return formatted_results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document search failed: {str(e)}"
        )