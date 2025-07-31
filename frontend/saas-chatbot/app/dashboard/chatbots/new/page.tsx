'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { useCreateChatbot } from '@/lib/hooks/use-chatbots';
import { useToast } from '@/components/ui/use-toast';

export default function CreateChatbotPage() {
  const router = useRouter();
  const { toast } = useToast();
  const createChatbot = useCreateChatbot();
  const [isCreating, setIsCreating] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    system_prompt: '',
    model: 'mixtral-8x7b-32768',
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

  const handleSave = async () => {
    console.log('🔧 Starting chatbot creation process...');
    console.log('📝 Form data:', formData);

    if (!formData.name.trim()) {
      console.warn('⚠️ Validation failed: Missing chatbot name');
      toast({
        title: "Validation Error",
        description: "Please enter a chatbot name",
        variant: "destructive",
      });
      return;
    }

    if (!formData.system_prompt.trim()) {
      console.warn('⚠️ Validation failed: Missing system prompt');
      toast({
        title: "Validation Error", 
        description: "Please enter a system prompt",
        variant: "destructive",
      });
      return;
    }

    console.log('✅ Form validation passed');
    setIsCreating(true);
    
    try {
      console.log('🚀 Calling createChatbot API...');
      const newChatbot = await createChatbot.mutateAsync(formData);
      console.log('🎉 Chatbot created successfully:', newChatbot);
      
      toast({
        title: "Success",
        description: "Chatbot created successfully!",
      });
      
      console.log('🔄 Redirecting to chatbot page...');
      router.push(`/dashboard/chatbots/${newChatbot.id}`);
    } catch (error) {
      console.error('💥 Error creating chatbot:', error);
      console.error('Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : null,
        fullError: error
      });
      
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create chatbot",
        variant: "destructive",
      });
    } finally {
      console.log('🏁 Chatbot creation process completed');
      setIsCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => router.back()}>
            <ChevronLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Create New Chatbot</h1>
            <p className="text-muted-foreground">
              Set up your AI chatbot in a few simple steps
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>
              Set up the basic details for your new chatbot
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Chatbot Name</Label>
              <Input
                id="name"
                placeholder="My Customer Support Bot"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Describe what this chatbot does..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="model">AI Model</Label>
              <Select
                value={formData.model}
                onValueChange={(value) => setFormData({ ...formData, model: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mixtral-8x7b-32768">Mixtral 8x7B (Recommended)</SelectItem>
                  <SelectItem value="llama2-70b-4096">Llama 2 70B</SelectItem>
                  <SelectItem value="gemma-7b-it">Gemma 7B</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
            <CardDescription>
              Configure your chatbot's behavior and responses
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="prompt">System Prompt</Label>
              <Textarea
                id="prompt"
                placeholder="You are a helpful customer support assistant. Be friendly, professional, and provide accurate information about our services."
                value={formData.system_prompt}
                onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                rows={4}
              />
              <p className="text-sm text-muted-foreground">
                This defines your chatbot's personality and knowledge. Be specific about its role and capabilities.
              </p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="greeting">Welcome Message</Label>
              <Input
                id="greeting"
                placeholder="Hello! How can I help you today?"
                value={formData.appearance_config.greetingMessage}
                onChange={(e) => setFormData({
                  ...formData,
                  appearance_config: { ...formData.appearance_config, greetingMessage: e.target.value },
                })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="botName">Bot Name</Label>
              <Input
                id="botName"
                placeholder="Assistant"
                value={formData.appearance_config.botName}
                onChange={(e) => setFormData({
                  ...formData,
                  appearance_config: { ...formData.appearance_config, botName: e.target.value },
                })}
              />
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                checked={formData.behavior_config.enableVoice}
                onCheckedChange={(checked) => setFormData({
                  ...formData,
                  behavior_config: { ...formData.behavior_config, enableVoice: checked },
                })}
              />
              <Label>Enable voice chat</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                checked={formData.is_active}
                onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
              />
              <Label>Activate chatbot</Label>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>
              Customize how your chatbot looks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Primary Color</Label>
              <div className="flex items-center space-x-2">
                <Input
                  type="color"
                  className="w-20 h-10"
                  value={formData.appearance_config.primaryColor}
                  onChange={(e) => setFormData({
                    ...formData,
                    appearance_config: { ...formData.appearance_config, primaryColor: e.target.value },
                  })}
                />
                <Input
                  type="text"
                  value={formData.appearance_config.primaryColor}
                  onChange={(e) => setFormData({
                    ...formData,
                    appearance_config: { ...formData.appearance_config, primaryColor: e.target.value },
                  })}
                />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label>Widget Position</Label>
                <Select
                  value={formData.appearance_config.position}
                  onValueChange={(value) => setFormData({
                    ...formData,
                    appearance_config: { ...formData.appearance_config, position: value },
                  })}
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
                  onValueChange={(value) => setFormData({
                    ...formData,
                    appearance_config: { ...formData.appearance_config, theme: value },
                  })}
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
          </CardContent>
        </Card>
        
        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={isCreating}>
            <Save className="w-4 h-4 mr-2" />
            {isCreating ? 'Creating...' : 'Create Chatbot'}
          </Button>
        </div>
      </div>
    </div>
  );
}
