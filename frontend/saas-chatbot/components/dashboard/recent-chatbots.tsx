'use client';

import { Bot, MessageSquare, Eye } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const recentChatbots = [
  {
    id: 1,
    name: 'Customer Support Bot',
    type: 'text',
    lastActive: '2 hours ago',
    status: 'active',
    conversations: 1234,
  },
  {
    id: 2,
    name: 'Voice Assistant',
    type: 'voice',
    lastActive: '5 minutes ago',
    status: 'active',
    conversations: 567,
  },
  {
    id: 3,
    name: 'Sales Assistant',
    type: 'text',
    lastActive: '1 day ago',
    status: 'training',
    conversations: 89,
  },
];

export function RecentChatbots() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle>Recent Chatbots</CardTitle>
        <Button variant="ghost" size="sm">
          View All
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recentChatbots.map((chatbot) => (
            <div key={chatbot.id} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4" />
                </div>
                <div>
                  <div className="font-medium">{chatbot.name}</div>
                  <div className="text-sm text-muted-foreground">
                    {chatbot.lastActive}
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
                <Button variant="ghost" size="sm">
                  <Eye className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}