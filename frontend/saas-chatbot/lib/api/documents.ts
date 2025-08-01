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

import { createClient } from '@/lib/supabase/client';

class DocumentService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  private async getCurrentUserEmail(): Promise<string> {
    const supabase = createClient();
    
    try {
      const { data: { user }, error } = await supabase.auth.getUser();
      
      if (error || !user?.email) {
        throw new Error('User not authenticated');
      }

      return user.email;
    } catch (error) {
      console.error('🚫 Error getting user email:', error);
      throw error;
    }
  }

  private async fetchWithAuth(url: string, options?: RequestInit) {
    const userEmail = await this.getCurrentUserEmail();
    
    // Add user email as query parameter for Supabase-native approach
    const urlWithEmail = new URL(`${this.baseUrl}${url}`);
    urlWithEmail.searchParams.set('user_email', userEmail);
    
    const response = await fetch(urlWithEmail.toString(), {
      ...options,
    });

    if (!response.ok) {
      let errorMessage = `API Error: ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // Keep default error message
      }
      throw new Error(errorMessage);
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    } else {
      return {};
    }
  }

  async getDocuments(chatbotId?: string): Promise<Document[]> {
    const url = chatbotId 
      ? `/api/v1/documents/chatbot/${chatbotId}` 
      : '/api/v1/documents';
    return this.fetchWithAuth(url);
  }

  async getDocument(id: string): Promise<Document> {
    return this.fetchWithAuth(`/api/v1/documents/${id}`);
  }

  async uploadDocument(request: UploadDocumentRequest): Promise<Document> {
    const userEmail = await this.getCurrentUserEmail();
    
    // Create FormData for direct file upload
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('chatbot_id', request.chatbot_id);
    formData.append('user_email', userEmail);

    // Upload file directly to the API
    const url = new URL(`${this.baseUrl}/api/v1/documents/upload`);
    url.searchParams.set('user_email', userEmail);
    
    const response = await fetch(url.toString(), {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header - browser will set it with boundary
    });

    if (!response.ok) {
      let errorMessage = 'Upload failed';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // Keep default error message
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  async deleteDocument(id: string): Promise<void> {
    return this.fetchWithAuth(`/api/v1/documents/${id}`, {
      method: 'DELETE',
    });
  }

  async processDocuments(chatbotId: string): Promise<{message: string, processed_count: number, total_embeddings: number, success: boolean}> {
    console.log('🧠 RAG DEBUG: Triggering document processing for chatbot:', chatbotId);
    
    const result = await this.fetchWithAuth(`/api/v1/documents/process/${chatbotId}`, {
      method: 'POST',
    });
    
    console.log('✅ RAG DEBUG: Document processing completed:', result);
    return result;
  }

  async reprocessDocument(id: string): Promise<Document> {
    return this.fetchWithAuth(`/api/v1/documents/${id}/reprocess`, {
      method: 'POST',
    });
  }
}

export const documentService = new DocumentService();