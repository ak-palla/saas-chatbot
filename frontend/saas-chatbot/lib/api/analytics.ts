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
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    // Use the main API service request method for consistency
    const { apiService } = await import('../api');
    return (apiService as any).request<T>(endpoint, options);
  }

  async getGlobalAnalytics(
    period: 'day' | 'week' | 'month' | 'year' = 'month'
  ): Promise<GlobalAnalytics> {
    return this.request(`/api/v1/analytics?period=${period}`);
  }

  async getChatbotAnalytics(
    chatbotId: string,
    period: 'day' | 'week' | 'month' | 'year' = 'week'
  ): Promise<ChatbotAnalytics> {
    return this.request(`/api/v1/analytics/chatbots/${chatbotId}?period=${period}`);
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

    const url = `/api/v1/analytics/conversations?${params.toString()}`;
    return this.request(url);
  }

  async getRealTimeMetrics(): Promise<UsageMetrics> {
    return this.request('/api/v1/analytics/usage');
  }

  async getDashboardStats(): Promise<{
    total_conversations: number;
    total_chatbots: number;
    total_documents: number;
    active_sessions: number;
  }> {
    return this.request('/api/v1/analytics/dashboard');
  }

  async exportAnalytics(
    format: 'csv' | 'json' | 'pdf',
    chatbotId?: string,
    period?: string
  ): Promise<{ downloadUrl: string }> {
    const params = new URLSearchParams({ format });
    
    if (chatbotId) params.append('chatbot_id', chatbotId);
    if (period) params.append('period', period);

    return this.request(`/api/v1/analytics/export?${params.toString()}`);
  }
}

export const analyticsService = new AnalyticsService();