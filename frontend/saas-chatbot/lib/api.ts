const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface Chatbot {
  id: string;
  name: string;
  type: 'text' | 'voice';
  status: 'active' | 'inactive' | 'training';
  description: string;
  prompt: string;
  voice_config?: {
    provider: string;
    voice_id: string;
    speed: number;
    pitch: number;
  };
  appearance: {
    theme: string;
    primary_color: string;
    position: string;
  };
  behavior: {
    greeting: string;
    fallback: string;
    enable_voice: boolean;
  };
  created_at: string;
  updated_at: string;
  conversation_count: number;
  document_count: number;
}

export interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  status: 'processed' | 'processing' | 'failed';
  pages: number;
  uploaded_by: string;
  uploaded_at: string;
  chatbot_id: string;
}

export interface ApiError {
  detail: string;
  status: number;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error: ApiError = await response.json();
        throw new Error(error.detail || 'An error occurred');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error');
    }
  }

  // Chatbot endpoints
  async getChatbots(): Promise<Chatbot[]> {
    const response = await this.request<ApiResponse<Chatbot[]>>('/api/v1/chatbots');
    return response.data;
  }

  async getChatbot(id: string): Promise<Chatbot> {
    const response = await this.request<ApiResponse<Chatbot>>(`/api/v1/chatbots/${id}`);
    return response.data;
  }

  async createChatbot(chatbot: Partial<Chatbot>): Promise<Chatbot> {
    const response = await this.request<ApiResponse<Chatbot>>('/api/v1/chatbots', {
      method: 'POST',
      body: JSON.stringify(chatbot),
    });
    return response.data;
  }

  async updateChatbot(id: string, chatbot: Partial<Chatbot>): Promise<Chatbot> {
    const response = await this.request<ApiResponse<Chatbot>>(`/api/v1/chatbots/${id}`, {
      method: 'PUT',
      body: JSON.stringify(chatbot),
    });
    return response.data;
  }

  async deleteChatbot(id: string): Promise<void> {
    await this.request(`/api/v1/chatbots/${id}`, {
      method: 'DELETE',
    });
  }

  // Document endpoints
  async getDocuments(): Promise<Document[]> {
    const response = await this.request<ApiResponse<Document[]>>('/api/v1/documents');
    return response.data;
  }

  async uploadDocument(file: File, chatbotId: string): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('chatbot_id', chatbotId);

    const response = await this.request<ApiResponse<Document>>('/api/v1/documents/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type
    });
    return response.data;
  }

  async deleteDocument(id: string): Promise<void> {
    await this.request(`/api/v1/documents/${id}`, {
      method: 'DELETE',
    });
  }

  // Analytics endpoints
  async getUsageStats() {
    const response = await this.request<ApiResponse<any>>('/api/v1/analytics/usage');
    return response.data;
  }

  async getConversationStats(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await this.request<ApiResponse<any>>(
      `/api/v1/analytics/conversations?${params}`
    );
    return response.data;
  }

  async getChatbotAnalytics(chatbotId: string) {
    const response = await this.request<ApiResponse<any>>(`/api/v1/analytics/chatbots/${chatbotId}`);
    return response.data;
  }
}

export const apiService = new ApiService();