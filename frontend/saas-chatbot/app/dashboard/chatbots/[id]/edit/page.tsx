'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ChevronLeft, Bot, Mic, Save, Eye, Settings, Palette, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Slider } from '@/components/ui/slider';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useChatbot, useUpdateChatbot } from '@/lib/hooks/use-chatbots';
import { ChatbotPreview } from '@/components/chatbot/chatbot-preview';

export default function EditChatbotPage() {
  const router = useRouter();
  const params = useParams();
  const chatbotId = params.id as string;
  
  const { data: chatbot, isLoading } = useChatbot(chatbotId);
  const updateChatbot = useUpdateChatbot();
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    system_prompt: '',
    is_active: true,
    appearance_config: {
      theme: 'light',
      primaryColor: '#3b82f6',
      position: 'bottom-right',
      greetingMessage: 'Hello! How can I help you today?',
      welcomeTitle: 'Welcome',
      botName: 'Assistant',
      showAvatar: true,
      avatarUrl: '',
    },
    behavior_config: {
      enableVoice: false,
      voiceProvider: 'deepgram',
      voiceId: 'en-US-AriaNeural',
      voiceSpeed: 1.0,
      voicePitch: 1.0,
      enableTypingIndicator: true,
      typingSpeed: 50,
      maxTokens: 1000,
      temperature: 0.7,
      enableSuggestions: true,
      suggestions: ['What can you help me with?', 'Tell me about your services'],
      enableFileUpload: false,
      enableEmoji: true,
    },
  });

  useEffect(() => {
    if (chatbot) {
      setFormData({
        name: chatbot.name || '',
        description: chatbot.description || '',
        system_prompt: chatbot.system_prompt || '',
        is_active: chatbot.is_active || true,
        appearance_config: {
          theme: chatbot.appearance_config?.theme || 'light',
          primaryColor: chatbot.appearance_config?.primaryColor || '#3b82f6',
          position: chatbot.appearance_config?.position || 'bottom-right',
          greetingMessage: chatbot.appearance_config?.greetingMessage || 'Hello! How can I help you today?',
          welcomeTitle: chatbot.appearance_config?.welcomeTitle || 'Welcome',
          botName: chatbot.appearance_config?.botName || 'Assistant',
          showAvatar: chatbot.appearance_config?.showAvatar || true,
          avatarUrl: chatbot.appearance_config?.avatarUrl || '',
        },
        behavior_config: {
          enableVoice: chatbot.behavior_config?.enableVoice || false,
          voiceProvider: chatbot.behavior_config?.voiceProvider || 'deepgram',
          voiceId: chatbot.behavior_config?.voiceId || 'en-US-AriaNeural',
          voiceSpeed: chatbot.behavior_config?.voiceSpeed || 1.0,
          voicePitch: chatbot.behavior_config?.voicePitch || 1.0,
          enableTypingIndicator: chatbot.behavior_config?.enableTypingIndicator || true,
          typingSpeed: chatbot.behavior_config?.typingSpeed || 50,
          maxTokens: chatbot.behavior_config?.maxTokens || 1000,
          temperature: chatbot.behavior_config?.temperature || 0.7,
          enableSuggestions: chatbot.behavior_config?.enableSuggestions || true,
          suggestions: chatbot.behavior_config?.suggestions || ['What can you help me with?', 'Tell me about your services'],
          enableFileUpload: chatbot.behavior_config?.enableFileUpload || false,
          enableEmoji: chatbot.behavior_config?.enableEmoji || true,
        },
      });
    }
  }, [chatbot]);

  const handleSave = async () => {
    try {
      await updateChatbot.mutateAsync({
        id: chatbotId,
        chatbot: formData,
      });
      
      // Show success message
      router.push('/dashboard/chatbots');
    } catch (error) {
      console.error('Failed to update chatbot:', error);
      // Error handling is done by React Query
    }
  };

  const updateConfig = (section: string, key: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev],
        [key]: value,
      },
    }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400 animate-pulse" />
          <p>Loading chatbot...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => router.back()}>
            <ChevronLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Configure {formData.name}</h1>
            <p className="text-muted-foreground">
              Customize your chatbot's appearance, behavior, and voice settings
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <ChatbotPreview config={formData} />
          <Button onClick={handleSave} disabled={updateChatbot.isPending}>
            <Save className="w-4 h-4 mr-2" />
            {updateChatbot.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      {updateChatbot.isError && (
        <Alert variant="destructive">
          <AlertDescription>
            Failed to save changes. Please try again.
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="basic" className="space-y-4">
        <TabsList>
          <TabsTrigger value="basic">
            <Settings className="w-4 h-4 mr-2" />
            Basic
          </TabsTrigger>
          <TabsTrigger value="appearance">
            <Palette className="w-4 h-4 mr-2" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="behavior">
            <MessageSquare className="w-4 h-4 mr-2" />
            Behavior
          </TabsTrigger>
          <TabsTrigger value="voice">
            <Mic className="w-4 h-4 mr-2" />
            Voice
          </TabsTrigger>
        </TabsList>

        <TabsContent value="basic">
          <Card>
            <CardHeader>
              <CardTitle>Basic Configuration</CardTitle>
              <CardDescription>
                Set up the fundamental details for your chatbot
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Chatbot Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Customer Support Bot"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe what this chatbot does..."
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="system-prompt">System Prompt</Label>
                <Textarea
                  id="system-prompt"
                  value={formData.system_prompt}
                  onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                  placeholder="You are a helpful customer support assistant..."
                  rows={6}
                />
                <p className="text-sm text-muted-foreground">
                  This prompt defines the chatbot's personality and behavior
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  checked={formData.is_active}
                  onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                />
                <Label>Enable chatbot</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="appearance">
          <Card>
            <CardHeader>
              <CardTitle>Appearance Settings</CardTitle>
              <CardDescription>
                Customize how your chatbot looks in the widget
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Primary Color</Label>
                  <div className="flex items-center space-x-2">
                    <Input
                      type="color"
                      className="w-20 h-10"
                      value={formData.appearance_config.primaryColor}
                      onChange={(e) => updateConfig('appearance_config', 'primaryColor', e.target.value)}
                    />
                    <Input
                      type="text"
                      value={formData.appearance_config.primaryColor}
                      onChange={(e) => updateConfig('appearance_config', 'primaryColor', e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Widget Position</Label>
                  <Select
                    value={formData.appearance_config.position}
                    onValueChange={(value) => updateConfig('appearance_config', 'position', value)}
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

                <div className="space-y-2">
                  <Label>Theme</Label>
                  <Select
                    value={formData.appearance_config.theme}
                    onValueChange={(value) => updateConfig('appearance_config', 'theme', value)}
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

                <div className="space-y-2">
                  <Label>Bot Name</Label>
                  <Input
                    value={formData.appearance_config.botName}
                    onChange={(e) => updateConfig('appearance_config', 'botName', e.target.value)}
                    placeholder="Support Assistant"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Welcome Title</Label>
                <Input
                  value={formData.appearance_config.welcomeTitle}
                  onChange={(e) => updateConfig('appearance_config', 'welcomeTitle', e.target.value)}
                  placeholder="Welcome!"
                />
              </div>

              <div className="space-y-2">
                <Label>Greeting Message</Label>
                <Textarea
                  value={formData.appearance_config.greetingMessage}
                  onChange={(e) => updateConfig('appearance_config', 'greetingMessage', e.target.value)}
                  placeholder="Hello! How can I help you today?"
                  rows={2}
                />
              </div>

              <div className="space-y-2">
                <Label>Avatar URL (optional)</Label>
                <Input
                  value={formData.appearance_config.avatarUrl}
                  onChange={(e) => updateConfig('appearance_config', 'avatarUrl', e.target.value)}
                  placeholder="https://example.com/avatar.png"
                />
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  checked={formData.appearance_config.showAvatar}
                  onCheckedChange={(checked) => updateConfig('appearance_config', 'showAvatar', checked)}
                />
                <Label>Show avatar</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="behavior">
          <Card>
            <CardHeader>
              <CardTitle>Behavior Settings</CardTitle>
              <CardDescription>
                Configure how your chatbot responds and interacts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Max Response Length</Label>
                  <Input
                    type="number"
                    value={formData.behavior_config.maxTokens}
                    onChange={(e) => updateConfig('behavior_config', 'maxTokens', parseInt(e.target.value))}
                    min="100"
                    max="4000"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Creativity (Temperature)</Label>
                  <div className="space-y-2">
                    <Slider
                      value={[formData.behavior_config.temperature]}
                      onValueChange={([value]) => updateConfig('behavior_config', 'temperature', value)}
                      min={0}
                      max={2}
                      step={0.1}
                    />
                    <span className="text-sm text-muted-foreground">
                      {formData.behavior_config.temperature} - 
                      {formData.behavior_config.temperature < 0.5 ? 'Conservative' : 
                       formData.behavior_config.temperature < 1.0 ? 'Balanced' : 'Creative'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  checked={formData.behavior_config.enableTypingIndicator}
                  onCheckedChange={(checked) => updateConfig('behavior_config', 'enableTypingIndicator', checked)}
                />
                <Label>Show typing indicator</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  checked={formData.behavior_config.enableSuggestions}
                  onCheckedChange={(checked) => updateConfig('behavior_config', 'enableSuggestions', checked)}
                />
                <Label>Enable suggested responses</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  checked={formData.behavior_config.enableEmoji}
                  onCheckedChange={(checked) => updateConfig('behavior_config', 'enableEmoji', checked)}
                />
                <Label>Enable emoji support</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  checked={formData.behavior_config.enableFileUpload}
                  onCheckedChange={(checked) => updateConfig('behavior_config', 'enableFileUpload', checked)}
                />
                <Label>Allow file uploads</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="voice">
          <Card>
            <CardHeader>
              <CardTitle>Voice Settings</CardTitle>
              <CardDescription>
                Configure voice features for your chatbot
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-2">
                <Switch
                  checked={formData.behavior_config.enableVoice}
                  onCheckedChange={(checked) => updateConfig('behavior_config', 'enableVoice', checked)}
                />
                <Label>Enable voice responses</Label>
              </div>

              {formData.behavior_config.enableVoice && (
                <>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Voice Provider</Label>
                      <Select
                        value={formData.behavior_config.voiceProvider}
                        onValueChange={(value) => updateConfig('behavior_config', 'voiceProvider', value)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="deepgram">Deepgram</SelectItem>
                          <SelectItem value="groq">Groq</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Voice</Label>
                      <Select
                        value={formData.behavior_config.voiceId}
                        onValueChange={(value) => updateConfig('behavior_config', 'voiceId', value)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="en-US-AriaNeural">Aria (US)</SelectItem>
                          <SelectItem value="en-US-JennyNeural">Jenny (US)</SelectItem>
                          <SelectItem value="en-GB-SoniaNeural">Sonia (UK)</SelectItem>
                          <SelectItem value="en-AU-NatashaNeural">Natasha (AU)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Speed: {formData.behavior_config.voiceSpeed}x</Label>
                      <Slider
                        value={[formData.behavior_config.voiceSpeed]}
                        onValueChange={([value]) => updateConfig('behavior_config', 'voiceSpeed', value)}
                        min={0.5}
                        max={2}
                        step={0.1}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Pitch: {formData.behavior_config.voicePitch}x</Label>
                      <Slider
                        value={[formData.behavior_config.voicePitch]}
                        onValueChange={([value]) => updateConfig('behavior_config', 'voicePitch', value)}
                        min={0.5}
                        max={2}
                        step={0.1}
                      />
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}