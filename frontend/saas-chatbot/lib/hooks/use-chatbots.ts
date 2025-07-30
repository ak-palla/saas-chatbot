import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService, Chatbot } from '@/lib/api';

export function useChatbots() {
  return useQuery({
    queryKey: ['chatbots'],
    queryFn: apiService.getChatbots,
  });
}

export function useChatbot(id: string) {
  return useQuery({
    queryKey: ['chatbot', id],
    queryFn: () => apiService.getChatbot(id),
    enabled: !!id,
  });
}

export function useCreateChatbot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (chatbot: Partial<Chatbot>) => apiService.createChatbot(chatbot),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatbots'] });
    },
  });
}

export function useUpdateChatbot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, chatbot }: { id: string; chatbot: Partial<Chatbot> }) =>
      apiService.updateChatbot(id, chatbot),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['chatbots'] });
      queryClient.invalidateQueries({ queryKey: ['chatbot', id] });
    },
  });
}

export function useDeleteChatbot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: apiService.deleteChatbot,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatbots'] });
    },
  });
}