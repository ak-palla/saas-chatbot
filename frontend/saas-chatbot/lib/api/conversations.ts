export interface Conversation {
  id: string;
  chatbot_id: string;
  session_id: string;
  status: 'active' | 'ended';
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface ConversationCreate {
  chatbot_id: string;
  session_id: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  type: 'text' | 'voice';
  metadata?: Record<string, any>;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  chatbot_id: string;
  conversation_id?: string;
  stream?: boolean;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  metadata?: Record<string, any>;
}

class ConversationService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const { apiService } = await import('../api');
    return (apiService as any).request<T>(endpoint, options);
  }

  async getConversations(chatbotId: string): Promise<Conversation[]> {
    return this.request<Conversation[]>(`/api/v1/conversations/chatbot/${chatbotId}`);
  }

  async getConversation(conversationId: string): Promise<Conversation> {
    return this.request<Conversation>(`/api/v1/conversations/${conversationId}`);
  }

  async createConversation(data: ConversationCreate): Promise<Conversation> {
    return this.request<Conversation>('/api/v1/conversations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteConversation(conversationId: string): Promise<{ message: string }> {
    return this.request(`/api/v1/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  }

  // Chat completion endpoints
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/api/v1/chat/completions', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async sendStreamingMessage(request: ChatRequest): Promise<Response> {
    const { apiService } = await import('../api');
    const authHeaders = await (apiService as any).getAuthHeaders();
    
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    return fetch(`${API_BASE_URL}/api/v1/chat/completions/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
      },
      body: JSON.stringify({ ...request, stream: true }),
    });
  }

  // Helper method for test page
  async createConversationWithMessage(chatbotId: string, message: string): Promise<{
    conversation: Conversation;
    response: ChatResponse;
  }> {
    // Create conversation
    const conversation = await this.createConversation({
      chatbot_id: chatbotId,
      session_id: `test-${Date.now()}`,
    });

    // Send initial message
    const response = await this.sendMessage({
      message,
      chatbot_id: chatbotId,
      conversation_id: conversation.id,
    });

    return { conversation, response };
  }
}

export const conversationService = new ConversationService();