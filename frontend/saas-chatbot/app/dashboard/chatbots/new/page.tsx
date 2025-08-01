'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft, Save, Bot, Settings, Palette, MessageCircle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ChatbotPreview } from '@/components/chatbot/chatbot-preview';
import { useCreateChatbot } from '@/lib/hooks/use-chatbots';
import { useToast } from '@/components/ui/use-toast';
import { apiService } from '@/lib/api';

export default function CreateChatbotPage() {
  const router = useRouter();
  const { toast } = useToast();
  const createChatbot = useCreateChatbot();
  const [isCreating, setIsCreating] = useState(false);
  const [activeTab, setActiveTab] = useState('basics');
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    system_prompt: '',
    model: 'llama-3.1-8b-instant',
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

  const isTabComplete = (tab: string) => {
    switch (tab) {
      case 'basics':
        return formData.name.trim() !== '' && formData.system_prompt.trim() !== '';
      case 'behavior':
        return true; // Optional settings
      case 'appearance':
        return true; // Optional settings
      default:
        return false;
    }
  };

  const testAuth = async () => {
    console.log('🧪 Testing authentication...');
    try {
      const result = await apiService.testAuth();
      console.log('🧪 Auth test result:', result);
      toast({
        title: "Authentication Test",
        description: "Authentication is working! Check console for details.",
      });
    } catch (error) {
      console.error('🧪 Auth test failed:', error);
      toast({
        title: "Authentication Test Failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

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

      <div className="max-w-5xl mx-auto">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[600px] mx-auto">
            <TabsTrigger value="basics" className="flex items-center gap-2">
              <Bot className="w-4 h-4" />
              <span className="hidden sm:inline">Basic Info</span>
              <span className="sm:hidden">Info</span>
              {isTabComplete('basics') && <CheckCircle className="w-3 h-3 text-green-500" />}
            </TabsTrigger>
            <TabsTrigger value="behavior" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              <span className="hidden sm:inline">Behavior</span>
              <span className="sm:hidden">Config</span>
              {isTabComplete('behavior') && <CheckCircle className="w-3 h-3 text-green-500" />}
            </TabsTrigger>
            <TabsTrigger value="appearance" className="flex items-center gap-2">
              <Palette className="w-4 h-4" />
              <span className="hidden sm:inline">Appearance</span>
              <span className="sm:hidden">Look</span>
              {isTabComplete('appearance') && <CheckCircle className="w-3 h-3 text-green-500" />}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="basics" className="space-y-6">
            <Card>
              <CardHeader className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center">
                  <Bot className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-2xl">Basic Information</CardTitle>
                <CardDescription>
                  Let's start with the essential details for your chatbot
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-base font-medium">Chatbot Name *</Label>
                  <Input
                    id="name"
                    placeholder="My Customer Support Bot"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="h-12 text-lg"
                  />
                  <p className="text-sm text-muted-foreground">Choose a memorable name for your chatbot</p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="description" className="text-base font-medium">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe what this chatbot does..."
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    className="text-base"
                  />
                  <p className="text-sm text-muted-foreground">Help users understand what your chatbot can do</p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="model" className="text-base font-medium">AI Model</Label>
                  <Select
                    value={formData.model}
                    onValueChange={(value) => setFormData({ ...formData, model: value })}
                  >
                    <SelectTrigger className="h-12 text-base">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="llama-3.1-8b-instant">
                        <div className="flex flex-col">
                          <span>Llama 3.1 8B Instant</span>
                          <span className="text-xs text-muted-foreground">Recommended - Fast & Smart</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="llama-3.1-70b-versatile">
                        <div className="flex flex-col">
                          <span>Llama 3.1 70B Versatile</span>
                          <span className="text-xs text-muted-foreground">Most Powerful</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="llama3-8b-8192">
                        <div className="flex flex-col">
                          <span>Llama 3 8B</span>
                          <span className="text-xs text-muted-foreground">Standard</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="llama3-70b-8192">
                        <div className="flex flex-col">
                          <span>Llama 3 70B</span>
                          <span className="text-xs text-muted-foreground">Large Model</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="gemma2-9b-it">
                        <div className="flex flex-col">
                          <span>Gemma 2 9B</span>
                          <span className="text-xs text-muted-foreground">Google Model</span>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="prompt" className="text-base font-medium">System Prompt *</Label>
                  <Textarea
                    id="prompt"
                    placeholder="You are a helpful customer support assistant. Be friendly, professional, and provide accurate information about our services."
                    value={formData.system_prompt}
                    onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                    rows={4}
                    className="text-base"
                  />
                  <p className="text-sm text-muted-foreground">
                    Define your chatbot's personality and knowledge. Be specific about its role and capabilities.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="behavior" className="space-y-6">
            <Card>
              <CardHeader className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center">
                  <Settings className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-2xl">Behavior Configuration</CardTitle>
                <CardDescription>
                  Configure how your chatbot responds and interacts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="greeting" className="text-base font-medium">Welcome Message</Label>
                    <Input
                      id="greeting"
                      placeholder="Hello! How can I help you today?"
                      value={formData.appearance_config.greetingMessage}
                      onChange={(e) => setFormData({
                        ...formData,
                        appearance_config: { ...formData.appearance_config, greetingMessage: e.target.value },
                      })}
                      className="h-12 text-base"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="botName" className="text-base font-medium">Bot Name</Label>
                    <Input
                      id="botName"
                      placeholder="Assistant"
                      value={formData.appearance_config.botName}
                      onChange={(e) => setFormData({
                        ...formData,
                        appearance_config: { ...formData.appearance_config, botName: e.target.value },
                      })}
                      className="h-12 text-base"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Voice Chat</div>
                      <div className="text-sm text-muted-foreground">Enable speech-to-text and text-to-speech</div>
                    </div>
                    <Switch
                      checked={formData.behavior_config.enableVoice}
                      onCheckedChange={(checked) => setFormData({
                        ...formData,
                        behavior_config: { ...formData.behavior_config, enableVoice: checked },
                      })}
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Typing Indicator</div>
                      <div className="text-sm text-muted-foreground">Show typing animation when bot is responding</div>
                    </div>
                    <Switch
                      checked={formData.behavior_config.enableTypingIndicator}
                      onCheckedChange={(checked) => setFormData({
                        ...formData,
                        behavior_config: { ...formData.behavior_config, enableTypingIndicator: checked },
                      })}
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Emoji Support</div>
                      <div className="text-sm text-muted-foreground">Allow emojis in responses</div>
                    </div>
                    <Switch
                      checked={formData.behavior_config.enableEmoji}
                      onCheckedChange={(checked) => setFormData({
                        ...formData,
                        behavior_config: { ...formData.behavior_config, enableEmoji: checked },
                      })}
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Active Status</div>
                      <div className="text-sm text-muted-foreground">Make chatbot available to users</div>
                    </div>
                    <Switch
                      checked={formData.is_active}
                      onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="appearance" className="space-y-6">
            <Card>
              <CardHeader className="text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center">
                  <Palette className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-2xl">Appearance Settings</CardTitle>
                <CardDescription>
                  Customize how your chatbot looks and feels
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label className="text-base font-medium">Primary Color</Label>
                    <div className="flex items-center space-x-4">
                      <Input
                        type="color"
                        className="w-20 h-12 cursor-pointer"
                        value={formData.appearance_config.primaryColor}
                        onChange={(e) => setFormData({
                          ...formData,
                          appearance_config: { ...formData.appearance_config, primaryColor: e.target.value },
                        })}
                      />
                      <Input
                        type="text"
                        className="h-12 text-base font-mono"
                        value={formData.appearance_config.primaryColor}
                        onChange={(e) => setFormData({
                          ...formData,
                          appearance_config: { ...formData.appearance_config, primaryColor: e.target.value },
                        })}
                      />
                      <div className="text-sm text-muted-foreground">Choose your brand color</div>
                    </div>
                  </div>

                  <div className="grid gap-6 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label className="text-base font-medium">Widget Position</Label>
                      <Select
                        value={formData.appearance_config.position}
                        onValueChange={(value) => setFormData({
                          ...formData,
                          appearance_config: { ...formData.appearance_config, position: value },
                        })}
                      >
                        <SelectTrigger className="h-12 text-base">
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
                      <Label className="text-base font-medium">Theme</Label>
                      <Select
                        value={formData.appearance_config.theme}
                        onValueChange={(value) => setFormData({
                          ...formData,
                          appearance_config: { ...formData.appearance_config, theme: value },
                        })}
                      >
                        <SelectTrigger className="h-12 text-base">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="light">Light Mode</SelectItem>
                          <SelectItem value="dark">Dark Mode</SelectItem>
                          <SelectItem value="auto">Auto (System)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="pt-6 border-t">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <Label className="text-base font-medium">Live Preview</Label>
                        <p className="text-sm text-muted-foreground">
                          See how your chatbot will appear to users
                        </p>
                      </div>
                      <ChatbotPreview 
                        config={{
                          name: formData.name || 'My Chatbot',
                          appearance_config: formData.appearance_config,
                          behavior_config: formData.behavior_config,
                        }}
                      />
                    </div>
                    
                    <div className="aspect-[16/10] bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 rounded-lg p-6 relative overflow-hidden border-2 border-dashed border-gray-200 dark:border-gray-700">
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-400/5 to-purple-400/5"></div>
                      <div className="relative z-10 h-full">
                        <div className="text-center mb-6">
                          <div className="text-lg font-semibold mb-2">Your Website Preview</div>
                          <div className="text-sm text-muted-foreground">This shows how the chatbot widget will appear</div>
                        </div>
                        
                        <div className="space-y-3 opacity-30">
                          <div className="grid grid-cols-4 gap-3">
                            <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded"></div>
                            <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded"></div>
                            <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded"></div>
                            <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded"></div>
                          </div>
                          <div className="space-y-2">
                            <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-full"></div>
                            <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-4/5"></div>
                            <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-3/5"></div>
                          </div>
                        </div>
                        
                        {/* Chatbot widget preview */}
                        <div className={`absolute transition-all duration-300 ${
                          formData.appearance_config.position === 'bottom-right' ? 'bottom-4 right-4' :
                          formData.appearance_config.position === 'bottom-left' ? 'bottom-4 left-4' :
                          formData.appearance_config.position === 'top-right' ? 'top-4 right-4' :
                          'top-4 left-4'
                        }`}>
                          <div 
                            className="w-14 h-14 rounded-full shadow-lg flex items-center justify-center cursor-pointer hover:scale-105 transition-all duration-200 pulse-ring"
                            style={{ backgroundColor: formData.appearance_config.primaryColor }}
                          >
                            <MessageCircle className="w-7 h-7 text-white" />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <div className="flex justify-between items-center pt-6">
            <div className="flex items-center gap-4">
              <div className="text-sm text-muted-foreground">
                Step {activeTab === 'basics' ? '1' : activeTab === 'behavior' ? '2' : '3'} of 3
              </div>
              <Button variant="ghost" size="sm" onClick={testAuth}>
                🧪 Test Auth
              </Button>
            </div>
            <div className="flex gap-3">
              {activeTab !== 'basics' && (
                <Button 
                  variant="outline" 
                  onClick={() => {
                    if (activeTab === 'behavior') setActiveTab('basics');
                    if (activeTab === 'appearance') setActiveTab('behavior');
                  }}
                >
                  Previous
                </Button>
              )}
              {activeTab !== 'appearance' ? (
                <Button 
                  onClick={() => {
                    if (activeTab === 'basics' && isTabComplete('basics')) setActiveTab('behavior');
                    if (activeTab === 'behavior') setActiveTab('appearance');
                  }}
                  disabled={activeTab === 'basics' && !isTabComplete('basics')}
                >
                  Next Step
                </Button>
              ) : (
                <Button 
                  onClick={handleSave} 
                  disabled={isCreating || !isTabComplete('basics')}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {isCreating ? 'Creating...' : 'Create Chatbot'}
                </Button>
              )}
            </div>
          </div>
        </Tabs>
      </div>
    </div>
  );
}
