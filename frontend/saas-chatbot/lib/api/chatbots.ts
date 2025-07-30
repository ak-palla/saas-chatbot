export interface Chatbot {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'inactive' | 'draft';
  model: string;
  configuration: {
    system_prompt?: string;
    temperature?: number;
    max_tokens?: number;
    voice_enabled?: boolean;
    voice_id?: string;
    appearance?: {
      theme: 'light' | 'dark';
      primary_color: string;
      position: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
    };
  };
  usage: {
    conversations: number;
    messages: number;
    tokens: number;
  };
  documents: Array<{
    id: string;
    filename: string;
    size: number;
    processed: boolean;
  }>;
  created_at: string;
  updated_at: string;
}

export interface CreateChatbotRequest {
  name: string;
  description?: string;
  model?: string;
  configuration?: Partial<Chatbot['configuration']>;
}

export interface UpdateChatbotRequest {
  name?: string;
  description?: string;
  configuration?: Partial<Chatbot['configuration']>;
}

class ChatbotService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  private async fetchWithAuth(url: string, options?: RequestInit) {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${this.baseUrl}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getChatbots(): Promise<Chatbot[]> {
    return this.fetchWithAuth('/api/v1/chatbots');
  }

  async getChatbot(id: string): Promise<Chatbot> {
    return this.fetchWithAuth(`/api/v1/chatbots/${id}`);
  }

  async createChatbot(data: CreateChatbotRequest): Promise<Chatbot> {
    return this.fetchWithAuth('/api/v1/chatbots', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateChatbot(id: string, data: UpdateChatbotRequest): Promise<Chatbot> {
    return this.fetchWithAuth(`/api/v1/chatbots/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteChatbot(id: string): Promise<void> {
    return this.fetchWithAuth(`/api/v1/chatbots/${id}`, {
      method: 'DELETE',
    });
  }

  async getChatbotEmbed(id: string): Promise<{ script: string; config: any }> {
    return this.fetchWithAuth(`/api/v1/chatbots/${id}/embed`);
  }

  async getUsage(id: string, period: 'day' | 'week' | 'month' = 'week') {
    return this.fetchWithAuth(`/api/v1/chatbots/${id}/usage?period=${period}`);
  }
}

export const chatbotService = new ChatbotService();