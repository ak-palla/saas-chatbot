export interface Document {
  id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  size: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  processed_chunks?: number;
  total_chunks?: number;
  chatbot_id: string;
  created_at: string;
  updated_at: string;
}

export interface UploadDocumentRequest {
  file: File;
  chatbot_id: string;
}

export interface DocumentUploadResponse {
  document: Document;
  upload_url: string;
}

class DocumentService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  private async fetchWithAuth(url: string, options?: RequestInit) {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${this.baseUrl}${url}`, {
      ...options,
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getDocuments(chatbotId?: string): Promise<Document[]> {
    const url = chatbotId 
      ? `/api/v1/documents?chatbot_id=${chatbotId}` 
      : '/api/v1/documents';
    return this.fetchWithAuth(url);
  }

  async getDocument(id: string): Promise<Document> {
    return this.fetchWithAuth(`/api/v1/documents/${id}`);
  }

  async uploadDocument(request: UploadDocumentRequest): Promise<DocumentUploadResponse> {
    // First, get upload URL
    const response = await this.fetchWithAuth('/api/v1/documents/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        filename: request.file.name,
        file_type: request.file.type,
        size: request.file.size,
        chatbot_id: request.chatbot_id,
      }),
    });

    // Upload file to the provided URL
    const uploadResponse = await fetch(response.upload_url, {
      method: 'PUT',
      body: request.file,
      headers: {
        'Content-Type': request.file.type,
      },
    });

    if (!uploadResponse.ok) {
      throw new Error('Failed to upload file');
    }

    return response;
  }

  async deleteDocument(id: string): Promise<void> {
    return this.fetchWithAuth(`/api/v1/documents/${id}`, {
      method: 'DELETE',
    });
  }

  async reprocessDocument(id: string): Promise<Document> {
    return this.fetchWithAuth(`/api/v1/documents/${id}/reprocess`, {
      method: 'POST',
    });
  }
}

export const documentService = new DocumentService();