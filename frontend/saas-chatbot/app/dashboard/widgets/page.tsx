'use client';

import { useState, useEffect } from 'react';
import { Plus, Settings, BarChart3, Eye, Copy, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/lib/hooks/use-toast';
import { Header } from '@/components/dashboard/header';
import Link from 'next/link';

interface WidgetConfiguration {
  id: string;
  chatbot_id: string;
  config_name: string;
  template_id?: string;
  theme: string;
  position: string;
  primary_color: string;
  deployment_status: string;
  created_at: string;
  updated_at: string;
}

interface Chatbot {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
}

export default function WidgetsPage() {
  const [chatbots, setChatbots] = useState<Chatbot[]>([]);
  const [selectedChatbot, setSelectedChatbot] = useState<string>('');
  const [configurations, setConfigurations] = useState<WidgetConfiguration[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchChatbots();
  }, []);

  useEffect(() => {
    if (selectedChatbot) {
      fetchConfigurations(selectedChatbot);
    }
  }, [selectedChatbot]);

  const fetchChatbots = async () => {
    try {
      const response = await fetch('/api/chatbots');
      if (response.ok) {
        const data = await response.json();
        setChatbots(data);
        if (data.length > 0) {
          setSelectedChatbot(data[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching chatbots:', error);
      toast({
        title: 'Error',
        description: 'Failed to load chatbots',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchConfigurations = async (chatbotId: string) => {
    try {
      const response = await fetch(`/api/widgets/${chatbotId}/config`);
      if (response.ok) {
        const data = await response.json();
        setConfigurations(data);
      }
    } catch (error) {
      console.error('Error fetching configurations:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'default';
      case 'draft': return 'secondary';
      case 'paused': return 'outline';
      case 'archived': return 'destructive';
      default: return 'secondary';
    }
  };

  const copyEmbedCode = (chatbotId: string, configId: string) => {
    const embedCode = `<script src="${process.env.NEXT_PUBLIC_WIDGET_URL || 'http://localhost:3000/widget/embed.js'}" data-chatbot-id="${chatbotId}" data-config-id="${configId}"></script>`;
    navigator.clipboard.writeText(embedCode);
    toast({
      title: 'Copied!',
      description: 'Embed code copied to clipboard',
    });
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <Header title="Widget Management" description="Manage your chatbot widgets and configurations" />
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <Header 
        title="Widget Management" 
        description="Manage your chatbot widgets, configurations, and deployments"
        action={
          <Link href="/dashboard/widgets/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Configuration
            </Button>
          </Link>
        }
      />

      <Tabs defaultValue="configurations" className="space-y-4">
        <TabsList>
          <TabsTrigger value="configurations">Configurations</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="deployments">Deployments</TabsTrigger>
        </TabsList>

        <TabsContent value="configurations" className="space-y-4">
          {/* Chatbot Selector */}
          <Card>
            <CardHeader>
              <CardTitle>Select Chatbot</CardTitle>
              <CardDescription>Choose a chatbot to manage its widget configurations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {chatbots.map((chatbot) => (
                  <Card 
                    key={chatbot.id} 
                    className={`cursor-pointer transition-colors ${
                      selectedChatbot === chatbot.id ? 'ring-2 ring-primary' : 'hover:bg-muted/50'
                    }`}
                    onClick={() => setSelectedChatbot(chatbot.id)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-medium">{chatbot.name}</h3>
                          <p className="text-sm text-muted-foreground">{chatbot.description}</p>
                        </div>
                        <Badge variant={chatbot.is_active ? 'default' : 'secondary'}>
                          {chatbot.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Widget Configurations */}
          {selectedChatbot && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {configurations.map((config) => (
                <Card key={config.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{config.config_name}</CardTitle>
                      <Badge variant={getStatusColor(config.deployment_status)}>
                        {config.deployment_status}
                      </Badge>
                    </div>
                    <CardDescription>
                      Theme: {config.theme} • Position: {config.position}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <div 
                        className="w-4 h-4 rounded-full border"
                        style={{ backgroundColor: config.primary_color }}
                      />
                      <span className="text-sm text-muted-foreground">{config.primary_color}</span>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span>Created: {new Date(config.created_at).toLocaleDateString()}</span>
                      <span>Updated: {new Date(config.updated_at).toLocaleDateString()}</span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Link href={`/dashboard/widgets/${config.id}/edit`}>
                        <Button variant="outline" size="sm">
                          <Settings className="h-4 w-4 mr-2" />
                          Edit
                        </Button>
                      </Link>
                      <Link href={`/dashboard/widgets/${config.id}/analytics`}>
                        <Button variant="outline" size="sm">
                          <BarChart3 className="h-4 w-4 mr-2" />
                          Analytics
                        </Button>
                      </Link>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => copyEmbedCode(config.chatbot_id, config.id)}
                      >
                        <Copy className="h-4 w-4 mr-2" />
                        Copy Code
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {configurations.length === 0 && (
                <Card className="col-span-full">
                  <CardContent className="flex flex-col items-center justify-center py-12">
                    <Settings className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium mb-2">No configurations found</h3>
                    <p className="text-muted-foreground mb-4">Create your first widget configuration to get started.</p>
                    <Link href="/dashboard/widgets/new">
                      <Button>
                        <Plus className="h-4 w-4 mr-2" />
                        Create Configuration
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </TabsContent>

        <TabsContent value="templates">
          <Card>
            <CardHeader>
              <CardTitle>Widget Templates</CardTitle>
              <CardDescription>Browse and manage widget templates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Eye className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Template Gallery</h3>
                <p className="text-muted-foreground mb-4">Template gallery will be implemented here</p>
                <Link href="/dashboard/widgets/templates">
                  <Button variant="outline">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Browse Templates
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics">
          <Card>
            <CardHeader>
              <CardTitle>Widget Analytics Overview</CardTitle>
              <CardDescription>Performance metrics across all your widgets</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Analytics Dashboard</h3>
                <p className="text-muted-foreground mb-4">Comprehensive analytics dashboard will be shown here</p>
                <Link href="/dashboard/analytics">
                  <Button variant="outline">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View Full Analytics
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="deployments">
          <Card>
            <CardHeader>
              <CardTitle>Widget Deployments</CardTitle>
              <CardDescription>Track where your widgets are deployed</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <ExternalLink className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Deployment Tracking</h3>
                <p className="text-muted-foreground">Deployment monitoring will be implemented here</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
