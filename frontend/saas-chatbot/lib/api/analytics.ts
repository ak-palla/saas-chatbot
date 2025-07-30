export interface UsageMetrics {
  total_conversations: number;
  total_messages: number;
  total_tokens: number;
  unique_users: number;
  average_response_time: number;
  peak_usage_hour: number;
}

export interface ConversationTrend {
  date: string;
  conversations: number;
  messages: number;
  tokens: number;
}

export interface ChatbotAnalytics {
  chatbot_id: string;
  chatbot_name: string;
  usage: UsageMetrics;
  trends: ConversationTrend[];
  top_documents: Array<{
    document_id: string;
    document_name: string;
    usage_count: number;
  }>;
}

export interface GlobalAnalytics {
  total_chatbots: number;
  total_conversations: number;
  total_messages: number;
  total_tokens: number;
  monthly_usage: ConversationTrend[];
  top_chatbots: Array<{
    chatbot_id: string;
    chatbot_name: string;
    conversations: number;
    messages: number;
  }>;
}

class AnalyticsService {
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

  async getGlobalAnalytics(
    period: 'day' | 'week' | 'month' | 'year' = 'month'
  ): Promise<GlobalAnalytics> {
    return this.fetchWithAuth(`/api/v1/analytics?period=${period}`);
  }

  async getChatbotAnalytics(
    chatbotId: string,
    period: 'day' | 'week' | 'month' | 'year' = 'week'
  ): Promise<ChatbotAnalytics> {
    return this.fetchWithAuth(`/api/v1/analytics/chatbot/${chatbotId}?period=${period}`);
  }

  async getUsageHistory(
    chatbotId?: string,
    startDate?: string,
    endDate?: string
  ): Promise<ConversationTrend[]> {
    const params = new URLSearchParams();
    
    if (chatbotId) params.append('chatbot_id', chatbotId);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const url = `/api/v1/analytics/usage?${params.toString()}`;
    return this.fetchWithAuth(url);
  }

  async getRealTimeMetrics(): Promise<UsageMetrics> {
    return this.fetchWithAuth('/api/v1/analytics/realtime');
  }

  async exportAnalytics(
    format: 'csv' | 'json' | 'pdf',
    chatbotId?: string,
    period?: string
  ): Promise<{ downloadUrl: string }> {
    const params = new URLSearchParams({ format });
    
    if (chatbotId) params.append('chatbot_id', chatbotId);
    if (period) params.append('period', period);

    return this.fetchWithAuth(`/api/v1/analytics/export?${params.toString()}`);
  }
}

export const analyticsService = new AnalyticsService();