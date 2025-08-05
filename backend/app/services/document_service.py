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

# LangChain for advanced text splitting
from langchain.text_splitter import RecursiveCharacterTextSplitter

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
        Upload and process a document with enhanced status tracking
        
        Args:
            file: File object to upload
            filename: Original filename
            chatbot_id: ID of chatbot to associate with
            user_id: ID of user uploading
            
        Returns:
            Document metadata and processing status
        """
        document_id = None
        try:
            print(f"🚀 RAG DEBUG: Starting document upload for '{filename}' (chatbot: {chatbot_id})")
            
            # Step 1: Create document record with 'uploading' status
            document_id = await self._create_document_record(file, filename, chatbot_id, user_id)
            await self._update_processing_status(document_id, 'uploading', 10)
            
            # Validate file
            file_info = await self._validate_file(file, filename)
            print(f"✅ RAG DEBUG: File validated - Type: {file_info['file_type']}, Size: {file_info['size']} bytes")
            
            # Calculate content hash
            file.seek(0)
            content_hash = self._calculate_hash(file.read())
            file.seek(0)
            print(f"🔐 RAG DEBUG: Content hash calculated: {content_hash[:16]}...")
            
            # Check if document already exists
            existing = await self._check_existing_document(chatbot_id, content_hash)
            if existing:
                print(f"⚠️ RAG DEBUG: Document with hash {content_hash} already exists - skipping upload")
                logger.info(f"Document with hash {content_hash} already exists")
                return existing
            
            # Upload to Google Drive (optional)
            google_drive_id = None
            if self.drive_service:
                print(f"☁️ RAG DEBUG: Uploading to Google Drive...")
                google_drive_id = await self._upload_to_drive(file, filename)
                file.seek(0)
                if google_drive_id:
                    print(f"✅ RAG DEBUG: Google Drive upload successful: {google_drive_id}")
                else:
                    print(f"❌ RAG DEBUG: Google Drive upload failed")
            else:
                print(f"⚠️ RAG DEBUG: Google Drive service not available - skipping cloud upload")
            
            # Step 2: Extract text content with 'extracting' status
            await self._update_processing_status(document_id, 'extracting', 30)
            print(f"📝 RAG DEBUG: Extracting text content from {file_info['file_type']} file...")
            text_content = await self._extract_text(file, file_info['file_type'])
            text_length = len(text_content)
            print(f"✅ RAG DEBUG: Text extraction complete - {text_length} characters extracted")
            print(f"📄 RAG DEBUG: Text preview (first 200 chars): {text_content[:200]}...")
            
            # Store extracted text
            await self._store_extracted_text(document_id, text_content)
            await self._update_processing_status(document_id, 'extracting', 50)
            
            # Step 3: Generate embeddings with 'embedding' status
            await self._update_processing_status(document_id, 'embedding', 60)
            await self._generate_embeddings_with_status(document_id, text_content)
            
            # Step 4: Mark as completed
            await self._mark_completed(document_id)
            
            print(f"🎉 RAG DEBUG: Document upload pipeline complete for '{filename}'")
            logger.info(f"Document {filename} uploaded and processed successfully")
            
            return await self._get_document_result(document_id)
            
        except Exception as e:
            print(f"💥 RAG DEBUG: Document upload FAILED for '{filename}': {str(e)}")
            if document_id:
                await self._mark_failed(document_id, str(e))
            logger.error(f"Document upload failed: {str(e)}")
            raise Exception(f"Failed to upload document: {str(e)}")
            document_data = {
                "chatbot_id": chatbot_id,
                "filename": filename,
                "file_type": file_info['file_type'],
                "file_size": file_info['size'],
                "google_drive_id": google_drive_id,
                "content_hash": content_hash,
                "processed": False
            }
            
            print(f"💾 RAG DEBUG: Creating document record in Supabase...")
            response = self.supabase.table("documents").insert(document_data).execute()
            document = response.data[0]
            document_id = document["id"]
            print(f"✅ RAG DEBUG: Document record created with ID: {document_id}")
            
            # Store extracted text and process immediately
            print(f"💾 RAG DEBUG: Storing extracted text content...")
            try:
                self.supabase.table("documents") \
                    .update({"extracted_text": text_content}) \
                    .eq("id", document_id) \
                    .execute()
                print(f"✅ RAG DEBUG: Text content stored")
            except Exception as e:
                print(f"⚠️ RAG DEBUG: Could not store extracted_text: {str(e)}")
            
            # Process document content into embeddings immediately
            print(f"🔧 RAG DEBUG: Processing document content into embeddings...")
            try:
                await self._process_document_content(document_id, text_content)
                
                # Mark as processed
                self.supabase.table("documents") \
                    .update({"processed": True}) \
                    .eq("id", document_id) \
                    .execute()
                
                print(f"✅ RAG DEBUG: Document processed and marked as complete")
                processed_status = True
                
            except Exception as e:
                print(f"❌ RAG DEBUG: Document processing failed: {str(e)}")
                processed_status = False
            
            print(f"🎉 RAG DEBUG: Document upload pipeline complete for '{filename}'")
            logger.info(f"Document {filename} uploaded and processed successfully")
            return {
                **document,
                "processed": processed_status,
                "text_length": text_length,
                "text_stored": True
            }
            
        except Exception as e:
            print(f"💥 RAG DEBUG: Document upload FAILED for '{filename}': {str(e)}")
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
            print(f"✂️ RAG DEBUG: Splitting text into chunks (chunk_size: {self.CHUNK_SIZE}, overlap: {self.CHUNK_OVERLAP})")
            chunks = self._split_text_into_chunks(text_content)
            print(f"✅ RAG DEBUG: Text split into {len(chunks)} chunks")
            
            # Generate embeddings for each chunk
            processed_chunks = 0
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    print(f"⚠️ RAG DEBUG: Skipping empty chunk {i}")
                    continue
                
                print(f"🧠 RAG DEBUG: Processing chunk {i+1}/{len(chunks)} (length: {len(chunk)} chars)")
                print(f"📝 RAG DEBUG: Chunk preview: {chunk[:100]}...")
                
                # Generate embedding
                embedding = await embedding_service.generate_embedding(chunk)
                print(f"🔢 RAG DEBUG: Generated embedding vector (dimension: {len(embedding) if embedding else 'None'})")
                
                # Store embedding with metadata
                metadata = {
                    "chunk_index": i,
                    "chunk_length": len(chunk)
                }
                
                print(f"💾 RAG DEBUG: Storing embedding in Supabase with metadata: {metadata}")
                await embedding_service.store_document_embedding(
                    document_id=document_id,
                    text_chunk=chunk,
                    embedding=embedding,
                    metadata=metadata
                )
                print(f"✅ RAG DEBUG: Chunk {i+1} embedding stored successfully")
                processed_chunks += 1
            
            print(f"🎯 RAG DEBUG: Embedding processing complete - {processed_chunks}/{len(chunks)} chunks processed")
            logger.info(f"Processed {len(chunks)} chunks for document {document_id}")
            
        except Exception as e:
            print(f"💥 RAG DEBUG: Document content processing FAILED: {str(e)}")
            logger.error(f"Document content processing failed: {str(e)}")
            raise
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into semantic chunks using LangChain RecursiveCharacterTextSplitter"""
        if len(text) <= self.CHUNK_SIZE:
            return [text]
        
        try:
            # Use LangChain's RecursiveCharacterTextSplitter for semantic chunking
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.CHUNK_SIZE,
                chunk_overlap=self.CHUNK_OVERLAP,
                length_function=len,
                separators=[
                    "\n\n",  # Paragraphs
                    "\n",    # Lines
                    ". ",    # Sentences
                    "! ",    # Exclamation sentences
                    "? ",    # Question sentences
                    "; ",    # Semicolon clauses
                    ", ",    # Comma clauses
                    " ",     # Words
                    ""       # Characters (fallback)
                ],
                keep_separator=True,  # Keep separators for context
                add_start_index=False
            )
            
            chunks = text_splitter.split_text(text)
            
            # Filter out empty chunks and very short chunks
            meaningful_chunks = []
            for chunk in chunks:
                cleaned_chunk = chunk.strip()
                if cleaned_chunk and len(cleaned_chunk) > 10:  # At least 10 characters
                    meaningful_chunks.append(cleaned_chunk)
            
            logger.info(f"Semantic chunking: {len(text)} chars -> {len(meaningful_chunks)} chunks")
            return meaningful_chunks
            
        except Exception as e:
            logger.error(f"Semantic chunking failed: {e}")
            logger.info("Falling back to simple word-boundary chunking")
            
            # Fallback to simple word-boundary chunking
            return self._simple_word_boundary_chunking(text)
    
    def _simple_word_boundary_chunking(self, text: str) -> List[str]:
        """Fallback method for simple word-boundary chunking"""
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
    
    async def process_chatbot_documents(self, chatbot_id: str, user_id: str) -> Dict[str, Any]:
        """
        Process all unprocessed documents for a chatbot (generate embeddings)
        Called when chatbot settings are saved with enhanced duplicate prevention
        """
        try:
            logger.info(f"🚀 EMBEDDING: Starting batch processing for chatbot {chatbot_id}")
            
            # Get all documents for this chatbot to analyze state
            all_docs_response = self.supabase.table("documents") \
                .select("*, chatbots!inner(user_id)") \
                .eq("chatbot_id", chatbot_id) \
                .eq("chatbots.user_id", user_id) \
                .execute()
            
            all_docs = all_docs_response.data
            processed_docs = [doc for doc in all_docs if doc.get("processed", False)]
            unprocessed_docs = [doc for doc in all_docs if not doc.get("processed", False)]
            
            logger.info(f"📊 EMBEDDING: Document analysis - Total: {len(all_docs)}, Processed: {len(processed_docs)}, Pending: {len(unprocessed_docs)}")
            
            if not unprocessed_docs:
                logger.info(f"✅ EMBEDDING: No new documents to process")
                
                # Count existing embeddings
                existing_embeddings = 0
                for doc in processed_docs:
                    embedding_response = self.supabase.table("vector_embeddings") \
                        .select("id", count="exact") \
                        .eq("document_id", doc["id"]) \
                        .execute()
                    existing_embeddings += embedding_response.count or 0
                
                return {
                    "processed_count": 0,
                    "total_embeddings": existing_embeddings,
                    "existing_embeddings": existing_embeddings,
                    "success": True,
                    "message": f"All {len(processed_docs)} documents already processed"
                }
            
            total_embeddings = 0
            processed_count = 0
            errors = []
            
            logger.info(f"🔄 EMBEDDING: Processing {len(unprocessed_docs)} documents...")
            
            for i, doc in enumerate(unprocessed_docs, 1):
                document_id = doc["id"]
                filename = doc["filename"]
                content_hash = doc.get("content_hash")
                extracted_text = doc.get("extracted_text")
                
                logger.info(f"🔄 EMBEDDING: Processing document {i}/{len(unprocessed_docs)}: {filename}")
                
                # Enhanced duplicate prevention: check content hash
                if content_hash:
                    duplicate_check = self.supabase.table("documents") \
                        .select("id, processed") \
                        .eq("content_hash", content_hash) \
                        .eq("processed", True) \
                        .neq("id", document_id) \
                        .execute()
                    
                    if duplicate_check.data:
                        logger.info(f"⚠️ EMBEDDING: Duplicate content detected for {filename} (hash: {content_hash[:8]}...), marking as processed")
                        # Mark as processed without creating new embeddings
                        self.supabase.table("documents") \
                            .update({"processed": True}) \
                            .eq("id", document_id) \
                            .execute()
                        processed_count += 1
                        continue
                
                if not extracted_text:
                    logger.warning(f"⚠️ EMBEDDING: No extracted text found for {filename}, skipping")
                    errors.append(f"{filename}: No extracted text")
                    continue
                
                try:
                    # Double-check for existing embeddings (safety net)
                    existing_embeddings_check = self.supabase.table("vector_embeddings") \
                        .select("id", count="exact") \
                        .eq("document_id", document_id) \
                        .execute()
                    
                    if existing_embeddings_check.count and existing_embeddings_check.count > 0:
                        logger.info(f"⚠️ EMBEDDING: Embeddings already exist for {filename}, marking as processed")
                        self.supabase.table("documents") \
                            .update({"processed": True}) \
                            .eq("id", document_id) \
                            .execute()
                        processed_count += 1
                        total_embeddings += existing_embeddings_check.count
                        continue
                    
                    # Process document content (create embeddings)
                    logger.info(f"🔄 EMBEDDING: Generating embeddings for {filename}...")
                    await self._process_document_content(document_id, extracted_text)
                    
                    # Update processed status
                    self.supabase.table("documents") \
                        .update({"processed": True}) \
                        .eq("id", document_id) \
                        .execute()
                    
                    processed_count += 1
                    
                    # Count embeddings created
                    embedding_response = self.supabase.table("vector_embeddings") \
                        .select("id", count="exact") \
                        .eq("document_id", document_id) \
                        .execute()
                    
                    doc_embeddings = embedding_response.count or 0
                    total_embeddings += doc_embeddings
                    
                    logger.info(f"✅ EMBEDDING: Processed {filename} - created {doc_embeddings} embeddings")
                    
                except Exception as e:
                    error_msg = f"Failed to process {filename}: {str(e)}"
                    logger.error(f"💥 EMBEDDING: {error_msg}")
                    errors.append(error_msg)
                    continue
            
            logger.info(f"🎉 EMBEDDING: Batch processing complete - {processed_count} documents processed, {total_embeddings} embeddings created")
            
            if errors:
                logger.warning(f"⚠️ EMBEDDING: {len(errors)} errors occurred during processing")
            
            return {
                "processed_count": processed_count,
                "total_embeddings": total_embeddings,
                "success": True,
                "errors": errors,
                "total_documents": len(all_docs),
                "already_processed": len(processed_docs),
                "message": f"Processed {processed_count} new documents, created {total_embeddings} embeddings"
            }
            
        except Exception as e:
            print(f"💥 RAG DEBUG: Batch processing FAILED: {str(e)}")
            logger.error(f"Batch document processing failed: {str(e)}")
            return {
                "processed_count": 0,
                "total_embeddings": 0,
                "success": False,
                "error": str(e)
            }

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

    # Enhanced status tracking methods
    async def _create_document_record(self, file: BinaryIO, filename: str, chatbot_id: str, user_id: str) -> str:
        """Create initial document record with uploading status"""
        try:
            file.seek(0)
            content_hash = self._calculate_hash(file.read())
            file.seek(0)
            
            # Get file info
            file_info = await self._validate_file(file, filename)
            
            document_data = {
                "chatbot_id": chatbot_id,
                "filename": filename,
                "file_type": file_info['file_type'],
                "file_size": file_info['size'],
                "content_hash": content_hash,
                "processing_status": "uploading",
                "processing_progress": 0,
                "processed": False
            }
            
            response = self.supabase.table("documents").insert(document_data).execute()
            document_id = response.data[0]["id"]
            print(f"✅ RAG DEBUG: Document record created with ID: {document_id}")
            return document_id
            
        except Exception as e:
            print(f"💥 RAG DEBUG: Failed to create document record: {str(e)}")
            raise e

    async def _update_processing_status(self, document_id: str, status: str, progress: int = 0, error_message: str = None):
        """Update document processing status"""
        try:
            update_data = {
                "processing_status": status,
                "processing_progress": progress
            }
            if error_message:
                update_data["error_message"] = error_message
                
            self.supabase.table("documents").update(update_data).eq("id", document_id).execute()
            print(f"📊 RAG DEBUG: Updated status to '{status}' with progress {progress}%")
            
        except Exception as e:
            print(f"⚠️ RAG DEBUG: Failed to update processing status: {str(e)}")

    async def _store_extracted_text(self, document_id: str, text_content: str):
        """Store extracted text content"""
        try:
            self.supabase.table("documents") \
                .update({"extracted_text": text_content}) \
                .eq("id", document_id) \
                .execute()
            print(f"✅ RAG DEBUG: Extracted text stored")
        except Exception as e:
            print(f"⚠️ RAG DEBUG: Could not store extracted_text: {str(e)}")

    async def _generate_embeddings_with_status(self, document_id: str, text_content: str):
        """Generate embeddings with progress tracking"""
        try:
            await self._process_document_content(document_id, text_content)
            print(f"✅ RAG DEBUG: Embeddings generated successfully")
        except Exception as e:
            print(f"💥 RAG DEBUG: Embedding generation failed: {str(e)}")
            raise e

    async def _mark_completed(self, document_id: str):
        """Mark document as completed"""
        try:
            self.supabase.table("documents") \
                .update({
                    "processed": True,
                    "processing_status": "completed",
                    "processing_progress": 100
                }) \
                .eq("id", document_id) \
                .execute()
            print(f"✅ RAG DEBUG: Document marked as completed")
        except Exception as e:
            print(f"⚠️ RAG DEBUG: Failed to mark as completed: {str(e)}")

    async def _mark_failed(self, document_id: str, error_message: str):
        """Mark document as failed"""
        try:
            self.supabase.table("documents") \
                .update({
                    "processing_status": "failed",
                    "error_message": error_message
                }) \
                .eq("id", document_id) \
                .execute()
            print(f"❌ RAG DEBUG: Document marked as failed: {error_message}")
        except Exception as e:
            print(f"⚠️ RAG DEBUG: Failed to mark as failed: {str(e)}")

    async def _update_chunk_counts(self, document_id: str, total_chunks: int, processed_chunks: int):
        """Update chunk processing counts"""
        try:
            self.supabase.table("documents") \
                .update({
                    "total_chunks": total_chunks,
                    "processed_chunks": processed_chunks
                }) \
                .eq("id", document_id) \
                .execute()
        except Exception as e:
            print(f"⚠️ RAG DEBUG: Failed to update chunk counts: {str(e)}")

    async def _get_document_result(self, document_id: str) -> Dict[str, Any]:
        """Get final document result"""
        try:
            response = self.supabase.table("documents").select("*").eq("id", document_id).execute()
            if response.data:
                document = response.data[0]
                return {
                    **document,
                    "processed": document.get("processed", False),
                    "text_length": len(document.get("extracted_text", "")),
                    "text_stored": True
                }
            else:
                raise Exception("Document not found")
        except Exception as e:
            print(f"⚠️ RAG DEBUG: Failed to get document result: {str(e)}")
            raise e

    async def retry_failed_document(self, document_id: str) -> bool:
        """Retry processing for failed documents"""
        try:
            # Get document
            doc_response = self.supabase.table("documents").select("*").eq("id", document_id).execute()
            
            if not doc_response.data:
                print(f"❌ RAG DEBUG: Document {document_id} not found")
                return False
                
            doc = doc_response.data[0]
            
            if doc['processing_status'] == 'failed':
                print(f"🔄 RAG DEBUG: Retrying failed document {document_id}")
                
                # Reset status and retry
                await self._update_processing_status(document_id, 'pending', 0)
                await self._update_processing_status(document_id, 'embedding', 60)
                
                if doc.get('extracted_text'):
                    await self._process_document_content(document_id, doc['extracted_text'])
                    await self._mark_completed(document_id)
                    print(f"✅ RAG DEBUG: Document retry successful")
                    return True
                else:
                    print(f"❌ RAG DEBUG: No extracted text found for retry")
                    return False
            else:
                print(f"⚠️ RAG DEBUG: Document {document_id} is not in failed status")
                return False
                
        except Exception as e:
            print(f"💥 RAG DEBUG: Document retry failed: {str(e)}")
            await self._mark_failed(document_id, str(e))
            return False

    async def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """Get document processing status"""
        try:
            response = self.supabase.table("documents").select("*").eq("id", document_id).execute()
            if response.data:
                doc = response.data[0]
                return {
                    "status": doc.get("processing_status", "unknown"),
                    "progress": doc.get("processing_progress", 0),
                    "total_chunks": doc.get("total_chunks", 0),
                    "processed_chunks": doc.get("processed_chunks", 0),
                    "error_message": doc.get("error_message"),
                    "processed": doc.get("processed", False)
                }
            else:
                return {"status": "not_found", "progress": 0}
        except Exception as e:
            print(f"⚠️ RAG DEBUG: Failed to get document status: {str(e)}")
            return {"status": "error", "progress": 0, "error": str(e)}


# Global instance
document_service = DocumentService()