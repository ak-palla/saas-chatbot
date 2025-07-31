import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';
import { ChatbotDetailView } from '@/components/dashboard/chatbot-detail-view';
import { ChatbotHeader } from '@/components/dashboard/chatbot-header';
import { ChatbotTabs } from '@/components/dashboard/chatbot-tabs';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

interface ChatbotDetailPageProps {
  params: Promise<{
    id: string;
  }>;
}

async function getChatbot(id: string) {
  const supabase = await createClient();
  
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return null;
  }

  const { data: chatbot, error } = await supabase
    .from('chatbots')
    .select(`
      *,
      documents(*),
      conversations(*)
    `)
    .eq('id', id)
    .eq('user_id', user.id)
    .single();

  if (error || !chatbot) {
    return null;
  }

  return chatbot;
}

export default async function ChatbotDetailPage({ params }: ChatbotDetailPageProps) {
  const { id } = await params;
  const chatbot = await getChatbot(id);

  if (!chatbot) {
    notFound();
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <Suspense fallback={<LoadingSpinner />}>
        <ChatbotHeader chatbot={chatbot} />
        <ChatbotTabs chatbot={chatbot} />
      </Suspense>
    </div>
  );
}