import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { chatbotService } from '@/lib/api/chatbots';
import { analyticsService } from '@/lib/api/analytics';
import type { Chatbot, ChatbotCreate, ChatbotUpdate, ChatbotDisplay } from '@/lib/api/chatbots';

export function useChatbots() {
  return useQuery({
    queryKey: ['chatbots'],
    queryFn: chatbotService.getChatbots,
  });
}

export function useChatbotsDisplay() {
  return useQuery({
    queryKey: ['chatbots', 'display'],
    queryFn: chatbotService.getChatbotsDisplay,
  });
}

export function useChatbot(id: string) {
  return useQuery({
    queryKey: ['chatbot', id],
    queryFn: () => chatbotService.getChatbot(id),
    enabled: !!id,
  });
}

export function useChatbotDisplay(id: string) {
  return useQuery({
    queryKey: ['chatbot', id, 'display'],
    queryFn: () => chatbotService.getChatbotDisplay(id),
    enabled: !!id,
  });
}

export function useCreateChatbot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (chatbot: ChatbotCreate) => chatbotService.createChatbot(chatbot),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatbots'] });
    },
  });
}

export function useUpdateChatbot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, chatbot }: { id: string; chatbot: ChatbotUpdate }) =>
      chatbotService.updateChatbot(id, chatbot),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['chatbots'] });
      queryClient.invalidateQueries({ queryKey: ['chatbot', id] });
    },
  });
}

export function useDeleteChatbot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: chatbotService.deleteChatbot,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatbots'] });
    },
  });
}

export function useChatbotEmbedCode(id: string) {
  return useQuery({
    queryKey: ['chatbot', id, 'embed'],
    queryFn: () => chatbotService.getEmbedCode(id),
    enabled: !!id,
  });
}

export function useChatbotAnalytics(id: string) {
  return useQuery({
    queryKey: ['chatbot', id, 'analytics'],
    queryFn: () => analyticsService.getChatbotAnalytics(id),
    enabled: !!id,
  });
}