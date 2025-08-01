"""
Document management API endpoints
Handles document upload, processing, and management
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import List
import io
import logging

from app.models.document import Document, DocumentUploadResponse, DocumentSearchResult
from app.services.document_service import document_service
from app.core.database import get_supabase_admin

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    chatbot_id: str = Form(...),
    file: UploadFile = File(...),
    user_email: str = Form(...)
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
        
        # Get user ID from email
        supabase = get_supabase_admin()
        user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_id = user_response.data[0]["id"]
        
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("id").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or access denied"
            )

        # Upload and process document
        result = await document_service.upload_document(
            file=file_io,
            filename=file.filename,
            chatbot_id=chatbot_id,
            user_id=user_id
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
    user_email: str
):
    """List all documents for a chatbot"""
    try:
        # Get user ID from email
        supabase = get_supabase_admin()
        user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_id = user_response.data[0]["id"]
        
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots").select("id").eq("id", chatbot_id).eq("user_id", user_id).execute()
        if not chatbot_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found or access denied"
            )

        documents = await document_service.list_documents(
            chatbot_id=chatbot_id,
            user_id=user_id
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
    user_email: str
):
    """Get a specific document"""
    try:
        # Get user ID from email
        supabase = get_supabase_admin()
        user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_id = user_response.data[0]["id"]
        
        document = await document_service.get_document(
            document_id=document_id,
            user_id=user_id
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
    user_email: str
):
    """Delete a document and its embeddings"""
    try:
        # Get user ID from email
        supabase = get_supabase_admin()
        user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_id = user_response.data[0]["id"]
        
        success = await document_service.delete_document(
            document_id=document_id,
            user_id=user_id
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
    user_email: str = Form(...),
    limit: int = Form(10)
):
    """Search documents by content similarity"""
    try:
        from app.services.vector_store_service import vector_store_service
        
        # Get user ID from email
        supabase = get_supabase_admin()
        user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_id = user_response.data[0]["id"]
        
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots") \
            .select("id") \
            .eq("id", chatbot_id) \
            .eq("user_id", user_id) \
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


@router.post("/process/{chatbot_id}")
async def process_documents(
    chatbot_id: str,
    user_email: str
):
    """Process unprocessed documents for a chatbot (generate embeddings)"""
    try:
        print(f"🚀 RAG DEBUG: Manual document processing triggered for chatbot {chatbot_id}")
        
        # Get user ID from email
        supabase = get_supabase_admin()
        user_response = supabase.table("users").select("id").eq("email", user_email).limit(1).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_id = user_response.data[0]["id"]
        
        # Verify chatbot ownership
        chatbot_response = supabase.table("chatbots") \
            .select("id") \
            .eq("id", chatbot_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not chatbot_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        # Process documents
        processing_result = await document_service.process_chatbot_documents(chatbot_id, user_id)
        
        print(f"📊 RAG DEBUG: Manual processing result: {processing_result}")
        
        return {
            "message": "Document processing completed",
            "processed_count": processing_result.get("processed_count", 0),
            "total_embeddings": processing_result.get("total_embeddings", 0),
            "success": processing_result.get("success", True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 RAG DEBUG: Manual document processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )