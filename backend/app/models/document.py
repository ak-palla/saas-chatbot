from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "md"


class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int
    google_drive_id: Optional[str] = None
    processed: bool = False


class DocumentCreate(BaseModel):
    chatbot_id: str
    filename: str
    file_type: str
    file_size: int
    content_hash: str
    google_drive_id: Optional[str] = None


class DocumentUpdate(BaseModel):
    processed: Optional[bool] = None
    google_drive_id: Optional[str] = None


class Document(DocumentBase):
    id: str
    chatbot_id: str
    content_hash: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    processed: bool
    text_length: Optional[int] = None
    message: str


class DocumentSearchResult(BaseModel):
    content: str
    document_id: str
    similarity: float
    metadata: Dict[str, Any]
    document_info: Dict[str, Any]


class VectorEmbedding(BaseModel):
    id: str
    document_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    created_at: datetime
    
    model_config = {"from_attributes": True}