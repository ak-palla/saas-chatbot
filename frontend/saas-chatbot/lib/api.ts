import { createClient } from '@/lib/supabase/client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Backend response doesn't wrap data in ApiResponse, it returns data directly
export interface Chatbot {
  id: string;
  name: string;
  description?: string;
  system_prompt?: string;
  appearance_config?: Record<string, any>;
  is_active: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface ChatbotCreate {
  name: string;
  description?: string;
  system_prompt?: string;
  appearance_config?: Record<string, any>;
  is_active?: boolean;
}

export interface ChatbotUpdate {
  name?: string;
  description?: string;
  system_prompt?: string;
  appearance_config?: Record<string, any>;
  is_active?: boolean;
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
  private async getAuthHeaders(): Promise<Record<string, string>> {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    
    if (session?.access_token) {
      return {
        'Authorization': `Bearer ${session.access_token}`,
      };
    }
    
    return {};
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retries = 3
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // Get auth headers
    const authHeaders = await this.getAuthHeaders();
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
        ...options.headers,
      },
    };

    // Debug logging
    console.log('🚀 API Request:', {
      url,
      method: options.method || 'GET',
      headers: config.headers,
      body: options.body ? JSON.parse(options.body as string) : null
    });

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        console.log(`📡 Attempt ${attempt + 1}/${retries + 1} - Fetching: ${url}`);
        const response = await fetch(url, config);
        
        console.log(`✅ Response received:`, {
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries())
        });

        if (!response.ok) {
          if (response.status === 401) {
            console.error('🚫 Authentication error - User not logged in');
            throw new Error('Authentication required. Please log in.');
          }
          
          let errorMessage = 'An error occurred';
          let errorData = null;
          try {
            errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
            console.error('❌ API Error Response:', errorData);
          } catch {
            errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            console.error('❌ Non-JSON Error Response:', {
              status: response.status,
              statusText: response.statusText
            });
          }
          
          throw new Error(errorMessage);
        }

        // Handle empty responses (like DELETE)
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          console.log('📦 Response data:', data);
          return data;
        } else {
          console.log('📦 Empty response (non-JSON)');
          return {} as T;
        }
      } catch (error) {
        console.error(`🔄 Attempt ${attempt + 1} failed:`, error);
        
        // If this is the last attempt or not a network error, throw
        if (attempt === retries || (error instanceof Error && !error.message.includes('fetch'))) {
          console.error('💥 Final error - giving up:', error);
          throw error;
        }
        
        // Wait before retrying (exponential backoff)
        const waitTime = Math.pow(2, attempt) * 1000;
        console.log(`⏳ Waiting ${waitTime}ms before retry...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }
    
    throw new Error('Max retries exceeded');
  }

  // Chatbot endpoints
  async getChatbots(): Promise<Chatbot[]> {
    return this.request<Chatbot[]>('/api/v1/chatbots');
  }

  async getChatbot(id: string): Promise<Chatbot> {
    return this.request<Chatbot>(`/api/v1/chatbots/${id}`);
  }

  async createChatbot(chatbot: ChatbotCreate): Promise<Chatbot> {
    return this.request<Chatbot>('/api/v1/chatbots', {
      method: 'POST',
      body: JSON.stringify(chatbot),
    });
  }

  async updateChatbot(id: string, chatbot: ChatbotUpdate): Promise<Chatbot> {
    return this.request<Chatbot>(`/api/v1/chatbots/${id}`, {
      method: 'PUT',
      body: JSON.stringify(chatbot),
    });
  }

  async deleteChatbot(id: string): Promise<{ message: string }> {
    return this.request(`/api/v1/chatbots/${id}`, {
      method: 'DELETE',
    });
  }

  // Document endpoints  
  async getDocuments(): Promise<Document[]> {
    return this.request<Document[]>('/api/v1/documents');
  }

  async uploadDocument(file: File, chatbotId: string): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('chatbot_id', chatbotId);

    // Get auth headers for FormData requests
    const authHeaders = await this.getAuthHeaders();
    
    return this.request<Document>('/api/v1/documents/upload', {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData
        ...authHeaders
      },
    });
  }

  async deleteDocument(id: string): Promise<{ message: string }> {
    return this.request(`/api/v1/documents/${id}`, {
      method: 'DELETE',
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/api/v1/health');
  }
}

export const apiService = new ApiService();