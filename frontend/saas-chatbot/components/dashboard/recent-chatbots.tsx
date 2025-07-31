'use client';

import Link from 'next/link';
import { Bot, Eye, Loader2, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useChatbotsDisplay } from '@/lib/hooks/use-chatbots';
import { formatDistanceToNow } from 'date-fns';

export function RecentChatbots() {
  const { data: chatbots = [], isLoading, error } = useChatbotsDisplay();
  
  // Get the 3 most recently updated chatbots
  const recentChatbots = chatbots
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 3);

  const formatLastActive = (updatedAt: string) => {
    try {
      return formatDistanceToNow(new Date(updatedAt), { addSuffix: true });
    } catch (error) {
      return 'Unknown';
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle>Recent Chatbots</CardTitle>
        <Button variant="ghost" size="sm" asChild>
          <Link href="/dashboard/chatbots">
            View All
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="space-y-2 text-center">
              <Loader2 className="h-6 w-6 animate-spin mx-auto" />
              <p className="text-sm text-muted-foreground">Loading recent chatbots...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-8">
            <div className="space-y-2 text-center">
              <AlertCircle className="h-6 w-6 text-destructive mx-auto" />
              <p className="text-sm text-destructive">Failed to load chatbots</p>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => window.location.reload()}
              >
                Try Again
              </Button>
            </div>
          </div>
        ) : recentChatbots.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <div className="space-y-2 text-center">
              <Bot className="h-6 w-6 text-muted-foreground mx-auto" />
              <p className="text-sm text-muted-foreground">No chatbots found</p>
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/chatbots/new">
                  Create First Chatbot
                </Link>
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {recentChatbots.map((chatbot) => (
              <div key={chatbot.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <div className="font-medium">{chatbot.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {formatLastActive(chatbot.updated_at)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={
                    chatbot.status === 'active' ? 'default' : 'secondary'
                  }>
                    {chatbot.status}
                  </Badge>
                  <div className="text-sm text-muted-foreground">
                    {chatbot.conversations.toLocaleString()} conv
                  </div>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/dashboard/chatbots/${chatbot.id}`}>
                      <Eye className="w-4 h-4" />
                    </Link>
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}