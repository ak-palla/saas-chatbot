import { Card, CardContent } from "@/components/ui/card";
import { Bot, MessageSquare } from "lucide-react";
import type { GlobalAnalytics } from "@/lib/api/analytics";

interface TopChatbotsProps {
  chatbots: Array<{
    chatbot_id: string;
    chatbot_name: string;
    conversations: number;
    messages: number;
  }>;
}

export function TopChatbots({ chatbots }: TopChatbotsProps) {
  if (!chatbots || chatbots.length === 0) {
    return (
      <div className="flex items-center justify-center h-32">
        <p className="text-muted-foreground">No chatbots found</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {chatbots.map((chatbot, index) => (
        <Card key={chatbot.chatbot_id}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <span className="text-white text-sm font-bold">{index + 1}</span>
                </div>
                <div>
                  <p className="font-medium">{chatbot.chatbot_name}</p>
                  <p className="text-sm text-muted-foreground">{chatbot.chatbot_id}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center space-x-2 text-sm">
                  <MessageSquare className="h-4 w-4 text-blue-600" />
                  <span>{chatbot.conversations.toLocaleString()} conversations</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Bot className="h-4 w-4" />
                  <span>{chatbot.messages.toLocaleString()} messages</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}