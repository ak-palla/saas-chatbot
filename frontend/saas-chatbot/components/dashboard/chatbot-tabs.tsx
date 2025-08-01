'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { MessageSquare, Settings, FileText, BarChart3, Code2 } from 'lucide-react';
import { ChatbotTest } from './chatbot-test';
import { ChatbotSettings } from './chatbot-settings';
import { AnalyticsView } from './analytics-view';
import { EmbedGenerator } from './embed-generator';

interface ChatbotTabsProps {
  chatbot: any;
}

export function ChatbotTabs({ chatbot }: ChatbotTabsProps) {
  const [activeTab, setActiveTab] = useState('test');

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="test" className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4" />
          Test
        </TabsTrigger>
        <TabsTrigger value="settings" className="flex items-center gap-2">
          <Settings className="h-4 w-4" />
          Settings
        </TabsTrigger>
        <TabsTrigger value="analytics" className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4" />
          Analytics
        </TabsTrigger>
        <TabsTrigger value="embed" className="flex items-center gap-2">
          <Code2 className="h-4 w-4" />
          Embed
        </TabsTrigger>
      </TabsList>

      <TabsContent value="test">
        <ChatbotTest chatbot={chatbot} />
      </TabsContent>

      <TabsContent value="settings">
        <ChatbotSettings chatbot={chatbot} />
      </TabsContent>

      <TabsContent value="analytics">
        <AnalyticsView chatbot={chatbot} />
      </TabsContent>

      <TabsContent value="embed">
        <EmbedGenerator chatbot={chatbot} />
      </TabsContent>
    </Tabs>
  );
}