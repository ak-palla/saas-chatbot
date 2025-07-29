from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "markdown"


class DocumentBase(BaseModel):
    filename: str
    file_type: DocumentType
    file_size: int
    google_drive_id: Optional[str] = None


class DocumentCreate(DocumentBase):
    chatbot_id: str
    content: str


class DocumentUpdate(BaseModel):
    filename: Optional[str] = None
    content: Optional[str] = None


class Document(DocumentBase):
    id: str
    chatbot_id: str
    content_hash: str
    processed: bool = False
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class VectorEmbedding(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    text_content: str
    embedding: List[float]
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}