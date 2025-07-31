// Backend Chatbot model structure
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

// Frontend display format (transformed from backend data)
export interface ChatbotDisplay extends Chatbot {
  status: 'active' | 'inactive' | 'draft';
  model: string;
  conversations: number;
  documents: number;
  lastActivity: string;
}

class ChatbotService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const { apiService } = await import('../api');
    return (apiService as any).request<T>(endpoint, options);
  }

  async getChatbots(): Promise<Chatbot[]> {
    return this.request<Chatbot[]>('/api/v1/chatbots');
  }

  async getChatbot(id: string): Promise<Chatbot> {
    return this.request<Chatbot>(`/api/v1/chatbots/${id}`);
  }

  async createChatbot(data: ChatbotCreate): Promise<Chatbot> {
    return this.request<Chatbot>('/api/v1/chatbots', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateChatbot(id: string, data: ChatbotUpdate): Promise<Chatbot> {
    return this.request<Chatbot>(`/api/v1/chatbots/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteChatbot(id: string): Promise<{ message: string }> {
    return this.request(`/api/v1/chatbots/${id}`, {
      method: 'DELETE',
    });
  }

  // Transform backend data to frontend display format
  async getChatbotsDisplay(): Promise<ChatbotDisplay[]> {
    const chatbots = await this.getChatbots();
    return chatbots.map(this.transformToDisplay);
  }

  async getChatbotDisplay(id: string): Promise<ChatbotDisplay> {
    const chatbot = await this.getChatbot(id);
    return this.transformToDisplay(chatbot);
  }

  private transformToDisplay(chatbot: Chatbot): ChatbotDisplay {
    return {
      ...chatbot,
      status: chatbot.is_active ? 'active' : 'inactive',
      model: 'GPT-4', // Default model for now
      conversations: 0, // Will be populated by analytics
      documents: 0, // Will be populated by document count
      lastActivity: chatbot.updated_at,
    };
  }

  // Widget/embed functionality
  async getEmbedCode(id: string): Promise<{ 
    script: string; 
    config: Record<string, any> 
  }> {
    const chatbot = await this.getChatbot(id);
    
    // Generate embed code
    const script = `
<script>
  (function() {
    const chatbotConfig = {
      chatbotId: "${chatbot.id}",
      apiUrl: "${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}",
      appearance: ${JSON.stringify(chatbot.appearance_config || {})},
      systemPrompt: "${chatbot.system_prompt || ''}"
    };
    
    // Load chatbot widget
    const script = document.createElement('script');
    script.src = '${process.env.NEXT_PUBLIC_WIDGET_URL || 'http://localhost:3000'}/widget.js';
    script.async = true;
    script.onload = function() {
      window.ChatbotWidget.init(chatbotConfig);
    };
    document.head.appendChild(script);
  })();
</script>`;

    return {
      script,
      config: chatbot.appearance_config || {}
    };
  }
}

export const chatbotService = new ChatbotService();