'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Settings, Bot, Palette, Save, AlertTriangle } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { apiService } from '@/lib/api';

interface ChatbotSettingsProps {
  chatbot: any;
}

export function ChatbotSettings({ chatbot }: ChatbotSettingsProps) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  
  const [settings, setSettings] = useState({
    name: chatbot?.name || '',
    description: chatbot?.description || '',
    system_prompt: chatbot?.system_prompt || '',
    model: chatbot?.model || 'llama-3.1-8b-instant',
    is_active: chatbot?.is_active ?? true,
    appearance_config: {
      theme: chatbot?.appearance_config?.theme || 'light',
      primaryColor: chatbot?.appearance_config?.primaryColor || '#3b82f6',
      position: chatbot?.appearance_config?.position || 'bottom-right',
      greetingMessage: chatbot?.appearance_config?.greetingMessage || 'Hello! How can I help you today?',
      botName: chatbot?.appearance_config?.botName || 'Assistant',
      showAvatar: chatbot?.appearance_config?.showAvatar ?? true,
      ...chatbot?.appearance_config
    },
    behavior_config: {
      enableVoice: chatbot?.behavior_config?.enableVoice ?? false,
      enableTypingIndicator: chatbot?.behavior_config?.enableTypingIndicator ?? true,
      enableEmoji: chatbot?.behavior_config?.enableEmoji ?? true,
      maxTokens: chatbot?.behavior_config?.maxTokens || 1000,
      temperature: chatbot?.behavior_config?.temperature || 0.7,
      ...chatbot?.behavior_config
    }
  });

  const handleSave = async () => {
    setIsLoading(true);
    try {
      // Update chatbot settings via API
      const updateData = {
        name: settings.name,
        description: settings.description,
        system_prompt: settings.system_prompt,
        model: settings.model,
        is_active: settings.is_active,
        appearance_config: settings.appearance_config,
        behavior_config: settings.behavior_config
      };

      await apiService.updateChatbot(chatbot.id, updateData);
      
      toast({
        title: "Settings Updated",
        description: "Your chatbot settings have been saved successfully.",
      });
    } catch (error) {
      console.error('❌ Settings save error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update settings. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Tabs defaultValue="general" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <Bot className="h-4 w-4" />
            General
          </TabsTrigger>
          <TabsTrigger value="behavior" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Behavior
          </TabsTrigger>
          <TabsTrigger value="appearance" className="flex items-center gap-2">
            <Palette className="h-4 w-4" />
            Appearance
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
              <CardDescription>
                Configure your chatbot's basic information and behavior.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Chatbot Name</Label>
                <Input
                  id="name"
                  value={settings.name}
                  onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                  placeholder="My Chatbot"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={settings.description}
                  onChange={(e) => setSettings({ ...settings, description: e.target.value })}
                  placeholder="Describe what your chatbot does..."
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="system_prompt">System Prompt</Label>
                <Textarea
                  id="system_prompt"
                  value={settings.system_prompt}
                  onChange={(e) => setSettings({ ...settings, system_prompt: e.target.value })}
                  placeholder="You are a helpful assistant..."
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="model">AI Model</Label>
                <Select
                  value={settings.model}
                  onValueChange={(value) => setSettings({ ...settings, model: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="llama-3.1-70b-versatile">Llama 3.1 70B (Versatile)</SelectItem>
                    <SelectItem value="llama-3.1-8b-instant">Llama 3.1 8B (Instant)</SelectItem>
                    <SelectItem value="llama3-8b-8192">Llama 3 8B</SelectItem>
                    <SelectItem value="llama3-70b-8192">Llama 3 70B</SelectItem>
                    <SelectItem value="gemma2-9b-it">Gemma 2 9B</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="font-medium">Active Status</div>
                  <div className="text-sm text-muted-foreground">
                    Make chatbot available to users
                  </div>
                </div>
                <Switch
                  checked={settings.is_active}
                  onCheckedChange={(checked) => setSettings({ ...settings, is_active: checked })}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="behavior" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Behavior Configuration</CardTitle>
              <CardDescription>
                Configure how your chatbot responds and interacts with users.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="font-medium">Voice Chat</div>
                  <div className="text-sm text-muted-foreground">
                    Enable speech-to-text and text-to-speech
                  </div>
                </div>
                <Switch
                  checked={settings.behavior_config.enableVoice}
                  onCheckedChange={(checked) => 
                    setSettings({
                      ...settings,
                      behavior_config: { ...settings.behavior_config, enableVoice: checked }
                    })
                  }
                />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="font-medium">Typing Indicator</div>
                  <div className="text-sm text-muted-foreground">
                    Show typing animation when bot is responding
                  </div>
                </div>
                <Switch
                  checked={settings.behavior_config.enableTypingIndicator}
                  onCheckedChange={(checked) => 
                    setSettings({
                      ...settings,
                      behavior_config: { ...settings.behavior_config, enableTypingIndicator: checked }
                    })
                  }
                />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="font-medium">Emoji Support</div>
                  <div className="text-sm text-muted-foreground">
                    Allow emojis in responses
                  </div>
                </div>
                <Switch
                  checked={settings.behavior_config.enableEmoji}
                  onCheckedChange={(checked) => 
                    setSettings({
                      ...settings,
                      behavior_config: { ...settings.behavior_config, enableEmoji: checked }
                    })
                  }
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="maxTokens">Max Tokens</Label>
                  <Input
                    id="maxTokens"
                    type="number"
                    value={settings.behavior_config.maxTokens}
                    onChange={(e) => 
                      setSettings({
                        ...settings,
                        behavior_config: { ...settings.behavior_config, maxTokens: parseInt(e.target.value) }
                      })
                    }
                    min="100"
                    max="4000"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="temperature">Temperature</Label>
                  <Input
                    id="temperature"
                    type="number"
                    step="0.1"
                    value={settings.behavior_config.temperature}
                    onChange={(e) => 
                      setSettings({
                        ...settings,
                        behavior_config: { ...settings.behavior_config, temperature: parseFloat(e.target.value) }
                      })
                    }
                    min="0"
                    max="2"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="appearance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Appearance Settings</CardTitle>
              <CardDescription>
                Customize how your chatbot looks and feels.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="botName">Bot Name</Label>
                  <Input
                    id="botName"
                    value={settings.appearance_config.botName}
                    onChange={(e) => 
                      setSettings({
                        ...settings,
                        appearance_config: { ...settings.appearance_config, botName: e.target.value }
                      })
                    }
                    placeholder="Assistant"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="theme">Theme</Label>
                  <Select
                    value={settings.appearance_config.theme}
                    onValueChange={(value) => 
                      setSettings({
                        ...settings,
                        appearance_config: { ...settings.appearance_config, theme: value }
                      })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="auto">Auto</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="greetingMessage">Greeting Message</Label>
                <Input
                  id="greetingMessage"
                  value={settings.appearance_config.greetingMessage}
                  onChange={(e) => 
                    setSettings({
                      ...settings,
                      appearance_config: { ...settings.appearance_config, greetingMessage: e.target.value }
                    })
                  }
                  placeholder="Hello! How can I help you today?"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="primaryColor">Primary Color</Label>
                <div className="flex items-center space-x-2">
                  <Input
                    id="primaryColor"
                    type="color"
                    value={settings.appearance_config.primaryColor}
                    onChange={(e) => 
                      setSettings({
                        ...settings,
                        appearance_config: { ...settings.appearance_config, primaryColor: e.target.value }
                      })
                    }
                    className="w-16 h-10"
                  />
                  <Input
                    value={settings.appearance_config.primaryColor}
                    onChange={(e) => 
                      setSettings({
                        ...settings,
                        appearance_config: { ...settings.appearance_config, primaryColor: e.target.value }
                      })
                    }
                    className="font-mono"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="position">Widget Position</Label>
                <Select
                  value={settings.appearance_config.position}
                  onValueChange={(value) => 
                    setSettings({
                      ...settings,
                      appearance_config: { ...settings.appearance_config, position: value }
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bottom-right">Bottom Right</SelectItem>
                    <SelectItem value="bottom-left">Bottom Left</SelectItem>
                    <SelectItem value="top-right">Top Right</SelectItem>
                    <SelectItem value="top-left">Top Left</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="font-medium">Show Avatar</div>
                  <div className="text-sm text-muted-foreground">
                    Display chatbot avatar in conversations
                  </div>
                </div>
                <Switch
                  checked={settings.appearance_config.showAvatar}
                  onCheckedChange={(checked) => 
                    setSettings({
                      ...settings,
                      appearance_config: { ...settings.appearance_config, showAvatar: checked }
                    })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="flex justify-end space-x-2 pt-4 border-t">
        <Button variant="outline" disabled={isLoading}>
          Cancel
        </Button>
        <Button onClick={handleSave} disabled={isLoading} className="flex items-center gap-2">
          <Save className="h-4 w-4" />
          {isLoading ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>
    </div>
  );
}