'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Save, Eye, Palette, Settings, Code } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { Header } from '@/components/dashboard/header';
import Link from 'next/link';

interface Chatbot {
  id: string;
  name: string;
  description: string;
}

interface WidgetTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  css_template: string;
  config_template: Record<string, any>;
  preview_image_url?: string;
}

export default function NewWidgetConfigPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [chatbots, setChatbots] = useState<Chatbot[]>([]);
  const [templates, setTemplates] = useState<WidgetTemplate[]>([]);
  
  const [config, setConfig] = useState({
    chatbot_id: '',
    config_name: 'New Widget Configuration',
    template_id: '',
    custom_css: '',
    theme: 'light',
    position: 'bottom-right',
    primary_color: '#3b82f6',
    secondary_color: '#1f2937',
    border_radius: 12,
    auto_open: false,
    auto_open_delay: 3000,
    show_avatar: true,
    enable_sound: true,
    enable_typing_indicator: true,
    enable_file_upload: false,
    max_width: 400,
    max_height: 600,
    mobile_full_screen: true,
    z_index: 999999,
    deployment_status: 'draft'
  });

  useEffect(() => {
    fetchChatbots();
    fetchTemplates();
  }, []);

  const fetchChatbots = async () => {
    try {
      const response = await fetch('/api/chatbots');
      if (response.ok) {
        const data = await response.json();
        setChatbots(data);
        if (data.length > 0) {
          setConfig(prev => ({ ...prev, chatbot_id: data[0].id }));
        }
      }
    } catch (error) {
      console.error('Error fetching chatbots:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/widgets/templates');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const handleTemplateSelect = (templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      setConfig(prev => ({
        ...prev,
        template_id: templateId,
        custom_css: template.css_template,
        ...template.config_template
      }));
    }
  };

  const handleSave = async () => {
    if (!config.chatbot_id) {
      toast({
        title: 'Error',
        description: 'Please select a chatbot',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/widgets/${config.chatbot_id}/config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Widget configuration created successfully',
        });
        router.push('/dashboard/widgets');
      } else {
        throw new Error('Failed to create configuration');
      }
    } catch (error) {
      console.error('Error creating configuration:', error);
      toast({
        title: 'Error',
        description: 'Failed to create widget configuration',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = (key: string, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="space-y-8">
      <Header 
        title="New Widget Configuration" 
        description="Create a new widget configuration for your chatbot"
        action={
          <div className="flex items-center space-x-2">
            <Link href="/dashboard/widgets">
              <Button variant="outline">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            <Button onClick={handleSave} disabled={loading}>
              <Save className="h-4 w-4 mr-2" />
              {loading ? 'Saving...' : 'Save Configuration'}
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Configuration Form */}
        <div className="lg:col-span-2 space-y-6">
          <Tabs defaultValue="general" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="appearance">Appearance</TabsTrigger>
              <TabsTrigger value="behavior">Behavior</TabsTrigger>
              <TabsTrigger value="advanced">Advanced</TabsTrigger>
            </TabsList>

            <TabsContent value="general" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Basic Configuration</CardTitle>
                  <CardDescription>Set up the basic properties of your widget</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="chatbot">Chatbot</Label>
                    <Select value={config.chatbot_id} onValueChange={(value) => updateConfig('chatbot_id', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a chatbot" />
                      </SelectTrigger>
                      <SelectContent>
                        {chatbots.map((chatbot) => (
                          <SelectItem key={chatbot.id} value={chatbot.id}>
                            {chatbot.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="config_name">Configuration Name</Label>
                    <Input
                      id="config_name"
                      value={config.config_name}
                      onChange={(e) => updateConfig('config_name', e.target.value)}
                      placeholder="Enter configuration name"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="template">Template</Label>
                    <Select value={config.template_id} onValueChange={handleTemplateSelect}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a template (optional)" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">No Template</SelectItem>
                        {templates.map((template) => (
                          <SelectItem key={template.id} value={template.id}>
                            {template.name} - {template.category}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="deployment_status">Status</Label>
                    <Select value={config.deployment_status} onValueChange={(value) => updateConfig('deployment_status', value)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="paused">Paused</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="appearance" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Palette className="h-5 w-5 mr-2" />
                    Appearance Settings
                  </CardTitle>
                  <CardDescription>Customize the visual appearance of your widget</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="theme">Theme</Label>
                      <Select value={config.theme} onValueChange={(value) => updateConfig('theme', value)}>
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
                      <Label htmlFor="position">Position</Label>
                      <Select value={config.position} onValueChange={(value) => updateConfig('position', value)}>
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
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="primary_color">Primary Color</Label>
                      <div className="flex items-center space-x-2">
                        <Input
                          id="primary_color"
                          type="color"
                          value={config.primary_color}
                          onChange={(e) => updateConfig('primary_color', e.target.value)}
                          className="w-12 h-10 p-1"
                        />
                        <Input
                          value={config.primary_color}
                          onChange={(e) => updateConfig('primary_color', e.target.value)}
                          placeholder="#3b82f6"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="secondary_color">Secondary Color</Label>
                      <div className="flex items-center space-x-2">
                        <Input
                          id="secondary_color"
                          type="color"
                          value={config.secondary_color}
                          onChange={(e) => updateConfig('secondary_color', e.target.value)}
                          className="w-12 h-10 p-1"
                        />
                        <Input
                          value={config.secondary_color}
                          onChange={(e) => updateConfig('secondary_color', e.target.value)}
                          placeholder="#1f2937"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="border_radius">Border Radius: {config.border_radius}px</Label>
                    <Input
                      id="border_radius"
                      type="range"
                      min="0"
                      max="50"
                      value={config.border_radius}
                      onChange={(e) => updateConfig('border_radius', parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="behavior" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Settings className="h-5 w-5 mr-2" />
                    Behavior Settings
                  </CardTitle>
                  <CardDescription>Configure how your widget behaves</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Auto Open</div>
                      <div className="text-sm text-muted-foreground">Automatically open widget on page load</div>
                    </div>
                    <Switch
                      checked={config.auto_open}
                      onCheckedChange={(checked) => updateConfig('auto_open', checked)}
                    />
                  </div>

                  {config.auto_open && (
                    <div className="space-y-2">
                      <Label htmlFor="auto_open_delay">Auto Open Delay (ms)</Label>
                      <Input
                        id="auto_open_delay"
                        type="number"
                        value={config.auto_open_delay}
                        onChange={(e) => updateConfig('auto_open_delay', parseInt(e.target.value))}
                        min="0"
                        max="60000"
                      />
                    </div>
                  )}

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Show Avatar</div>
                      <div className="text-sm text-muted-foreground">Display bot avatar in messages</div>
                    </div>
                    <Switch
                      checked={config.show_avatar}
                      onCheckedChange={(checked) => updateConfig('show_avatar', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Enable Sound</div>
                      <div className="text-sm text-muted-foreground">Play notification sounds</div>
                    </div>
                    <Switch
                      checked={config.enable_sound}
                      onCheckedChange={(checked) => updateConfig('enable_sound', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Typing Indicator</div>
                      <div className="text-sm text-muted-foreground">Show typing indicator when bot is responding</div>
                    </div>
                    <Switch
                      checked={config.enable_typing_indicator}
                      onCheckedChange={(checked) => updateConfig('enable_typing_indicator', checked)}
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">File Upload</div>
                      <div className="text-sm text-muted-foreground">Allow users to upload files</div>
                    </div>
                    <Switch
                      checked={config.enable_file_upload}
                      onCheckedChange={(checked) => updateConfig('enable_file_upload', checked)}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="advanced" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Code className="h-5 w-5 mr-2" />
                    Advanced Settings
                  </CardTitle>
                  <CardDescription>Advanced configuration options</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="max_width">Max Width (px)</Label>
                      <Input
                        id="max_width"
                        type="number"
                        value={config.max_width}
                        onChange={(e) => updateConfig('max_width', parseInt(e.target.value))}
                        min="200"
                        max="800"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="max_height">Max Height (px)</Label>
                      <Input
                        id="max_height"
                        type="number"
                        value={config.max_height}
                        onChange={(e) => updateConfig('max_height', parseInt(e.target.value))}
                        min="300"
                        max="1000"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="z_index">Z-Index</Label>
                    <Input
                      id="z_index"
                      type="number"
                      value={config.z_index}
                      onChange={(e) => updateConfig('z_index', parseInt(e.target.value))}
                      min="1"
                      max="9999999"
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-1">
                      <div className="font-medium">Mobile Full Screen</div>
                      <div className="text-sm text-muted-foreground">Use full screen on mobile devices</div>
                    </div>
                    <Switch
                      checked={config.mobile_full_screen}
                      onCheckedChange={(checked) => updateConfig('mobile_full_screen', checked)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="custom_css">Custom CSS</Label>
                    <Textarea
                      id="custom_css"
                      value={config.custom_css}
                      onChange={(e) => updateConfig('custom_css', e.target.value)}
                      placeholder="/* Add your custom CSS here */"
                      rows={6}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Preview Panel */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Eye className="h-5 w-5 mr-2" />
                Live Preview
              </CardTitle>
              <CardDescription>See how your widget will look</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-100 rounded-lg p-4 min-h-[300px] relative">
                <div className="text-center text-muted-foreground">
                  <Eye className="h-8 w-8 mx-auto mb-2" />
                  <p>Widget preview will be shown here</p>
                  <p className="text-sm">Theme: {config.theme}</p>
                  <p className="text-sm">Position: {config.position}</p>
                  <div className="flex items-center justify-center mt-2">
                    <div 
                      className="w-4 h-4 rounded-full mr-2"
                      style={{ backgroundColor: config.primary_color }}
                    />
                    <span className="text-sm">{config.primary_color}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
