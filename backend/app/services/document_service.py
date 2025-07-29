"""
Document Processing Service
Handles document upload, parsing, text extraction, and Google Drive integration
"""

import logging
import hashlib
import mimetypes
from typing import List, Dict, Any, Optional, BinaryIO
from pathlib import Path
import tempfile
import os

# Document processing libraries
import PyPDF2
import docx
from bs4 import BeautifulSoup
import markdown

# Google Drive API
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials

from app.core.config import settings
from app.core.database import get_supabase
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document processing and Google Drive integration"""
    
    SUPPORTED_FORMATS = {
        'pdf': 'application/pdf',
        'txt': 'text/plain',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'html': 'text/html',
        'md': 'text/markdown',
        'markdown': 'text/markdown'
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    CHUNK_SIZE = 1000  # Characters per chunk for embeddings
    CHUNK_OVERLAP = 200  # Overlap between chunks
    
    def __init__(self):
        self.supabase = get_supabase()
        self.drive_service = self._initialize_drive_service()
    
    def _initialize_drive_service(self):
        """Initialize Google Drive API service"""
        try:
            if not os.path.exists(settings.GOOGLE_DRIVE_CREDENTIALS_PATH):
                logger.warning("Google Drive credentials not found, Google Drive features will be disabled")
                return None
                
            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_DRIVE_CREDENTIALS_PATH,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive API service initialized successfully")
            return service
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {str(e)}")
            return None
    
    async def upload_document(
        self, 
        file: BinaryIO, 
        filename: str, 
        chatbot_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Upload and process a document
        
        Args:
            file: File object to upload
            filename: Original filename
            chatbot_id: ID of chatbot to associate with
            user_id: ID of user uploading
            
        Returns:
            Document metadata and processing status
        """
        try:
            # Validate file
            file_info = await self._validate_file(file, filename)
            
            # Calculate content hash
            file.seek(0)
            content_hash = self._calculate_hash(file.read())
            file.seek(0)
            
            # Check if document already exists
            existing = await self._check_existing_document(chatbot_id, content_hash)
            if existing:
                logger.info(f"Document with hash {content_hash} already exists")
                return existing
            
            # Upload to Google Drive (optional)
            google_drive_id = None
            if self.drive_service:
                google_drive_id = await self._upload_to_drive(file, filename)
                file.seek(0)
            
            # Extract text content
            text_content = await self._extract_text(file, file_info['file_type'])
            
            # Create document record
            document_data = {
                "chatbot_id": chatbot_id,
                "filename": filename,
                "file_type": file_info['file_type'],
                "file_size": file_info['size'],
                "google_drive_id": google_drive_id,
                "content_hash": content_hash,
                "processed": False
            }
            
            response = self.supabase.table("documents").insert(document_data).execute()
            document = response.data[0]
            document_id = document["id"]
            
            # Process document asynchronously (create embeddings)
            await self._process_document_content(document_id, text_content)
            
            # Update processed status
            self.supabase.table("documents") \
                .update({"processed": True}) \
                .eq("id", document_id) \
                .execute()
            
            logger.info(f"Document {filename} uploaded and processed successfully")
            return {
                **document,
                "processed": True,
                "text_length": len(text_content)
            }
            
        except Exception as e:
            logger.error(f"Document upload failed: {str(e)}")
            raise Exception(f"Failed to upload document: {str(e)}")
    
    async def _validate_file(self, file: BinaryIO, filename: str) -> Dict[str, Any]:
        """Validate uploaded file"""
        # Get file extension
        file_ext = Path(filename).suffix.lower().lstrip('.')
        
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.MAX_FILE_SIZE})")
        
        if file_size == 0:
            raise ValueError("Empty file")
        
        # Normalize file type for database compatibility
        normalized_file_type = 'markdown' if file_ext == 'md' else file_ext
        
        return {
            'file_type': normalized_file_type,
            'size': file_size,
            'mime_type': self.SUPPORTED_FORMATS[file_ext]
        }
    
    def _calculate_hash(self, content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(content).hexdigest()
    
    async def _check_existing_document(self, chatbot_id: str, content_hash: str) -> Optional[Dict[str, Any]]:
        """Check if document with same hash already exists"""
        try:
            response = self.supabase.table("documents") \
                .select("*") \
                .eq("chatbot_id", chatbot_id) \
                .eq("content_hash", content_hash) \
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception:
            return None
    
    async def _upload_to_drive(self, file: BinaryIO, filename: str) -> Optional[str]:
        """Upload file to Google Drive"""
        if not self.drive_service:
            return None
            
        try:
            file_metadata = {
                'name': filename
            }
            
            # Add folder if specified
            if settings.GOOGLE_DRIVE_FOLDER_ID:
                file_metadata['parents'] = [settings.GOOGLE_DRIVE_FOLDER_ID]
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(filename)
            mime_type = mime_type or 'application/octet-stream'
            
            media = MediaIoBaseUpload(file, mimetype=mime_type, resumable=True)
            
            drive_file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            drive_id = drive_file.get('id')
            logger.info(f"File uploaded to Google Drive: {drive_id}")
            return drive_id
            
        except Exception as e:
            logger.error(f"Google Drive upload failed: {str(e)}")
            return None
    
    def create_drive_folder(self, folder_name: str) -> Optional[str]:
        """
        Create a folder in Google Drive and return its ID
        
        Args:
            folder_name: Name of the folder to create
            
        Returns:
            Folder ID if successful, None otherwise
        """
        if not self.drive_service:
            return None
            
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"Created Google Drive folder '{folder_name}': {folder_id}")
            return folder_id
            
        except Exception as e:
            logger.error(f"Failed to create Google Drive folder: {str(e)}")
            return None
    
    async def _extract_text(self, file: BinaryIO, file_type: str) -> str:
        """Extract text content from file based on type"""
        try:
            if file_type == 'pdf':
                return await self._extract_pdf_text(file)
            elif file_type == 'docx':
                return await self._extract_docx_text(file)
            elif file_type == 'html':
                return await self._extract_html_text(file)
            elif file_type == 'markdown':
                return await self._extract_markdown_text(file)
            elif file_type == 'txt':
                return await self._extract_plain_text(file)
            else:
                raise ValueError(f"Unsupported file type for text extraction: {file_type}")
                
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise Exception(f"Failed to extract text: {str(e)}")
    
    async def _extract_pdf_text(self, file: BinaryIO) -> str:
        """Extract text from PDF file"""
        text_content = []
        pdf_reader = PyPDF2.PdfReader(file)
        
        for page in pdf_reader.pages:
            text_content.append(page.extract_text())
        
        return "\n".join(text_content)
    
    async def _extract_docx_text(self, file: BinaryIO) -> str:
        """Extract text from DOCX file"""
        # Save to temporary file (python-docx requires file path)
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name
        
        try:
            doc = docx.Document(temp_file_path)
            text_content = []
            
            for paragraph in doc.paragraphs:
                text_content.append(paragraph.text)
            
            return "\n".join(text_content)
            
        finally:
            os.unlink(temp_file_path)
    
    async def _extract_html_text(self, file: BinaryIO) -> str:
        """Extract text from HTML file"""
        content = file.read().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
    
    async def _extract_markdown_text(self, file: BinaryIO) -> str:
        """Extract text from Markdown file"""
        content = file.read().decode('utf-8')
        # Convert markdown to HTML then extract text
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
    
    async def _extract_plain_text(self, file: BinaryIO) -> str:
        """Extract text from plain text file"""
        return file.read().decode('utf-8')
    
    async def _process_document_content(self, document_id: str, text_content: str):
        """Process document content into chunks and generate embeddings"""
        try:
            # Split text into chunks
            chunks = self._split_text_into_chunks(text_content)
            
            # Generate embeddings for each chunk
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                
                # Generate embedding
                embedding = await embedding_service.generate_embedding(chunk)
                
                # Store embedding with metadata
                metadata = {
                    "chunk_index": i,
                    "chunk_length": len(chunk)
                }
                
                await embedding_service.store_document_embedding(
                    document_id=document_id,
                    text_chunk=chunk,
                    embedding=embedding,
                    metadata=metadata
                )
            
            logger.info(f"Processed {len(chunks)} chunks for document {document_id}")
            
        except Exception as e:
            logger.error(f"Document content processing failed: {str(e)}")
            raise
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.CHUNK_SIZE:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.CHUNK_SIZE
            
            # If not the last chunk, try to break at word boundary
            if end < len(text):
                # Find last space within the chunk
                space_pos = text.rfind(' ', start, end)
                if space_pos > start:
                    end = space_pos
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.CHUNK_OVERLAP
            if start >= len(text):
                break
        
        return chunks
    
    async def get_document(self, document_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID with user ownership verification"""
        try:
            response = self.supabase.table("documents") \
                .select("*, chatbots!inner(user_id)") \
                .eq("id", document_id) \
                .eq("chatbots.user_id", user_id) \
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Get document failed: {str(e)}")
            return None
    
    async def list_documents(self, chatbot_id: str, user_id: str) -> List[Dict[str, Any]]:
        """List all documents for a chatbot"""
        try:
            # Verify chatbot ownership
            chatbot_response = self.supabase.table("chatbots") \
                .select("id") \
                .eq("id", chatbot_id) \
                .eq("user_id", user_id) \
                .execute()
            
            if not chatbot_response.data:
                raise ValueError("Chatbot not found or access denied")
            
            # Get documents
            response = self.supabase.table("documents") \
                .select("*") \
                .eq("chatbot_id", chatbot_id) \
                .order("created_at", desc=True) \
                .execute()
            
            return response.data
            
        except Exception as e:
            logger.error(f"List documents failed: {str(e)}")
            raise Exception(f"Failed to list documents: {str(e)}")
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document and associated embeddings"""
        try:
            # Verify ownership
            document = await self.get_document(document_id, user_id)
            if not document:
                raise ValueError("Document not found or access denied")
            
            # Delete embeddings first
            await embedding_service.delete_document_embeddings(document_id)
            
            # Delete from Google Drive if exists
            if document.get('google_drive_id') and self.drive_service:
                try:
                    self.drive_service.files().delete(fileId=document['google_drive_id']).execute()
                    logger.info(f"Deleted from Google Drive: {document['google_drive_id']}")
                except Exception as e:
                    logger.warning(f"Failed to delete from Google Drive: {str(e)}")
            
            # Delete document record
            self.supabase.table("documents").delete().eq("id", document_id).execute()
            
            logger.info(f"Document {document_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Delete document failed: {str(e)}")
            return False


# Global instance
document_service = DocumentService()