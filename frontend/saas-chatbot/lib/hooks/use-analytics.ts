import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '@/lib/api/analytics';

export function useUsageMetrics() {
  return useQuery({
    queryKey: ['analytics', 'usage'],
    queryFn: analyticsService.getRealTimeMetrics,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

export function useGlobalAnalytics(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery({
    queryKey: ['analytics', 'global', period],
    queryFn: () => analyticsService.getGlobalAnalytics(period),
  });
}

export function useConversationTrends(
  startDate?: string,
  endDate?: string,
  chatbotId?: string
) {
  return useQuery({
    queryKey: ['analytics', 'conversations', { startDate, endDate, chatbotId }],
    queryFn: () => analyticsService.getUsageHistory(chatbotId, startDate, endDate),
    enabled: true, // Always enabled, will use defaults if no dates
  });
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ['analytics', 'dashboard'],
    queryFn: analyticsService.getDashboardStats,
    refetchInterval: 60000, // Refetch every minute
  });
}

export function useChatbotAnalytics(chatbotId: string, period: 'day' | 'week' | 'month' | 'year' = 'week') {
  return useQuery({
    queryKey: ['analytics', 'chatbot', chatbotId, period],
    queryFn: () => analyticsService.getChatbotAnalytics(chatbotId, period),
    enabled: !!chatbotId,
  });
}

export function useExportAnalytics() {
  return useQuery({
    queryKey: ['analytics', 'export'],
    queryFn: (context) => {
      const { format, chatbotId, period } = context.meta as any;
      return analyticsService.exportAnalytics(format, chatbotId, period);
    },
    enabled: false, // Only run when manually triggered
  });
}