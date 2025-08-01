'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ChatbotHeader } from '@/components/dashboard/chatbot-header';
import { ChatbotTabs } from '@/components/dashboard/chatbot-tabs';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { apiService } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';

export default function ChatbotDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const [chatbot, setChatbot] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const chatbotId = params.id as string;

  useEffect(() => {
    const fetchChatbot = async () => {
      if (!chatbotId) return;

      setIsLoading(true);
      setError(null);

      try {
        console.log('🔍 Fetching chatbot details for ID:', chatbotId);
        const chatbotData = await apiService.getChatbot(chatbotId);
        console.log('✅ Chatbot data loaded:', chatbotData);
        setChatbot(chatbotData);
      } catch (err) {
        console.error('❌ Error fetching chatbot:', err);
        const errorMessage = err instanceof Error ? err.message : 'Failed to load chatbot';
        setError(errorMessage);
        
        if (errorMessage.includes('not found') || errorMessage.includes('404')) {
          toast({
            title: "Chatbot Not Found",
            description: "The chatbot you're looking for doesn't exist or you don't have access to it.",
            variant: "destructive",
          });
          router.push('/dashboard/chatbots');
        } else {
          toast({
            title: "Error Loading Chatbot",
            description: errorMessage,
            variant: "destructive",
          });
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchChatbot();
  }, [chatbotId, router, toast]);

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center space-y-4">
          <LoadingSpinner size="lg" />
          <div className="text-muted-foreground">Loading chatbot details...</div>
        </div>
      </div>
    );
  }

  if (error || !chatbot) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center space-y-4">
          <div className="text-xl font-semibold">Chatbot Not Found</div>
          <div className="text-muted-foreground">
            {error || "The chatbot you're looking for doesn't exist or you don't have access to it."}
          </div>
          <button
            onClick={() => router.push('/dashboard/chatbots')}
            className="inline-flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Back to Chatbots
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <ChatbotHeader chatbot={chatbot} />
      <ChatbotTabs chatbot={chatbot} />
    </div>
  );
}