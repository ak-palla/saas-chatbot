'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  MessageSquare, 
  FileText, 
  Users, 
  Clock, 
  TrendingUp,
  Activity,
  Zap
} from 'lucide-react';

interface ChatbotDetailViewProps {
  chatbot: any;
}

export function ChatbotDetailView({ chatbot }: ChatbotDetailViewProps) {
  // Mock statistics - in a real app, these would come from analytics API
  const stats = {
    totalConversations: 142,
    totalMessages: 1284,
    documentsCount: chatbot.documents?.length || 0,
    averageResponseTime: '1.2s',
    successRate: '94%',
    activeUsers: 68,
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Conversations</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalConversations}</div>
            <p className="text-xs text-muted-foreground">+12% from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeUsers}</div>
            <p className="text-xs text-muted-foreground">+8% from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.documentsCount}</div>
            <p className="text-xs text-muted-foreground">Knowledge base size</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.successRate}</div>
            <p className="text-xs text-muted-foreground">User satisfaction</p>
          </CardContent>
        </Card>
      </div>

      {/* Chatbot Overview */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Configuration Overview</CardTitle>
            <CardDescription>Current chatbot settings and configuration</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Status</span>
              <Badge variant={chatbot.is_active ? "default" : "secondary"}>
                {chatbot.is_active ? "Active" : "Inactive"}
              </Badge>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">AI Model</span>
              <span className="text-sm text-muted-foreground">{chatbot.model}</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Created</span>
              <span className="text-sm text-muted-foreground">
                {formatDate(chatbot.created_at)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Last Updated</span>
              <span className="text-sm text-muted-foreground">
                {formatDate(chatbot.updated_at)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Theme</span>
              <span className="text-sm text-muted-foreground capitalize">
                {chatbot.appearance_config?.theme || 'Light'}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Position</span>
              <span className="text-sm text-muted-foreground">
                {chatbot.appearance_config?.position?.replace('-', ' ') || 'Bottom Right'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
            <CardDescription>Real-time performance and usage statistics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium">Response Time</span>
              </div>
              <span className="text-sm text-muted-foreground">{stats.averageResponseTime}</span>
            </div>

            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium">Total Messages</span>
              </div>
              <span className="text-sm text-muted-foreground">{stats.totalMessages}</span>
            </div>

            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-orange-500" />
                <span className="text-sm font-medium">Avg. Session</span>
              </div>
              <span className="text-sm text-muted-foreground">4.2 min</span>
            </div>

            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-purple-500" />
                <span className="text-sm font-medium">Resolution Rate</span>
              </div>
              <span className="text-sm text-muted-foreground">87%</span>
            </div>

            <div className="pt-4 border-t">
              <div className="text-xs text-muted-foreground">
                Metrics updated in real-time • Last updated: {new Date().toLocaleTimeString()}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Prompt Preview */}
      {chatbot.system_prompt && (
        <Card>
          <CardHeader>
            <CardTitle>System Prompt</CardTitle>
            <CardDescription>The instructions that guide your chatbot's behavior</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground leading-relaxed">
                {chatbot.system_prompt}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks and shortcuts for managing your chatbot</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              <span className="text-sm">Test Chat</span>
            </Button>
            
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
              <FileText className="h-5 w-5" />
              <span className="text-sm">Upload Docs</span>
            </Button>
            
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              <span className="text-sm">View Analytics</span>
            </Button>
            
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
              <Users className="h-5 w-5" />
              <span className="text-sm">Share Widget</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}