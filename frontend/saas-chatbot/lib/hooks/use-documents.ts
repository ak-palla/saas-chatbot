import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '@/lib/api';

export function useDocuments() {
  return useQuery({
    queryKey: ['documents'],
    queryFn: apiService.getDocuments,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ file, chatbotId }: { file: File; chatbotId: string }) =>
      apiService.uploadDocument(file, chatbotId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: apiService.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
}

export function useUsageStats() {
  return useQuery({
    queryKey: ['usage-stats'],
    queryFn: apiService.getUsageStats,
  });
}

export function useConversationStats(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: ['conversation-stats', startDate, endDate],
    queryFn: () => apiService.getConversationStats(startDate, endDate),
  });
}

export function useChatbotAnalytics(chatbotId: string) {
  return useQuery({
    queryKey: ['chatbot-analytics', chatbotId],
    queryFn: () => apiService.getChatbotAnalytics(chatbotId),
    enabled: !!chatbotId,
  });
}