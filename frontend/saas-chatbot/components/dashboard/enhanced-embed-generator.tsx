'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Copy, Check, Code2, Settings, Palette, Smartphone, Monitor, 
  Eye, MessageSquare, Zap, Globe, Save, Download, RefreshCw,
  Sparkles, Crown, Layers, Brush
} from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface WidgetTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  preview_image_url?: string;
  css_template: string;
  config_template: Record<string, any>;
  is_premium: boolean;
  downloads_count: number;
  rating: number;
}

interface WidgetConfiguration {
  id: string;
  config_name: string;
  template_id?: string;
  custom_css: string;
  theme: string;
  position: string;
  primary_color: string;
  secondary_color: string;
  border_radius: number;
  auto_open: boolean;
  auto_open_delay: number;
  show_avatar: boolean;
  enable_sound: boolean;
  enable_typing_indicator: boolean;
  enable_file_upload: boolean;
  max_width: number;
  max_height: number;
  mobile_full_screen: boolean;
  z_index: number;
  custom_branding: Record<string, any>;
  conversation_starters: string[];
  operating_hours: Record<string, any>;
  language_settings: Record<string, any>;
  allowed_domains: string[];
  deployment_status: string;
}

interface EnhancedEmbedGeneratorProps {
  chatbot: {
    id: string;
    name: string;
    description?: string;
    appearance_config?: any;
    behavior_config?: any;
  };
}

export function EnhancedEmbedGenerator({ chatbot }: EnhancedEmbedGeneratorProps) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('script-tag');
  const [previewMode, setPreviewMode] = useState<'desktop' | 'mobile'>('desktop');

  // Widget templates
  const [templates, setTemplates] = useState<WidgetTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');

  // Widget configurations
  const [configurations, setConfigurations] = useState<WidgetConfiguration[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<string>('');
  const [currentConfig, setCurrentConfig] = useState({
    config_name: 'Default Configuration',
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
    custom_branding: {},
    conversation_starters: [] as string[],
    operating_hours: {},
    language_settings: {},
    allowed_domains: [] as string[],
    deployment_status: 'draft'
  });

  const [advancedSettings, setAdvancedSettings] = useState({
    botName: chatbot.behavior_config?.botName || chatbot.name || 'Assistant',
    greeting: chatbot.behavior_config?.greetingMessage || 'Hello! How can I help you today?',
    enableVoice: chatbot.behavior_config?.enableVoice || false,
    companyLogo: '',
    companyName: '',
    gdprCompliant: false,
    analyticsEnabled: true,
    domainRestrictions: '',
    customCss: ''
  });

  const { toast } = useToast();

  useEffect(() => {
    fetchTemplatesAndConfigurations();
  }, [chatbot.id]);

  const fetchTemplatesAndConfigurations = async () => {
    setLoading(true);
    try {
      // Fetch widget templates
      const templatesRes = await fetch('/api/widgets/templates');
      if (templatesRes.ok) {
        const templatesData = await templatesRes.json();
        setTemplates(templatesData);
      }

      // Fetch existing configurations
      const configsRes = await fetch(`/api/widgets/${chatbot.id}/config`);
      if (configsRes.ok) {
        const configsData = await configsRes.json();
        setConfigurations(configsData);
        
        // Set default to first active configuration if available
        const activeConfig = configsData.find((c: any) => c.deployment_status === 'active') || configsData[0];
        if (activeConfig) {
          setSelectedConfig(activeConfig.id);
          setCurrentConfig(activeConfig);
        }
      }
    } catch (error) {
      console.error('Error fetching templates and configurations:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyTemplate = async (templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    if (!template) return;

    setCurrentConfig(prev => ({
      ...prev,
      template_id: templateId,
      custom_css: template.css_template,
      ...template.config_template
    }));

    toast({
      title: 'Template Applied',
      description: `${template.name} template has been applied to your widget.`,
    });
  };

  const saveConfiguration = async () => {
    setSaving(true);
    try {
      const configData = {
        ...currentConfig,
        chatbot_id: chatbot.id,
        custom_branding: {
          ...currentConfig.custom_branding,
          company_name: advancedSettings.companyName,
          company_logo: advancedSettings.companyLogo
        },
        allowed_domains: advancedSettings.domainRestrictions 
          ? advancedSettings.domainRestrictions.split(',').map(d => d.trim())
          : [],
        custom_css: advancedSettings.customCss || currentConfig.custom_css
      };

      const endpoint = selectedConfig 
        ? `/api/widgets/${chatbot.id}/config/${selectedConfig}`
        : `/api/widgets/${chatbot.id}/config`;
      
      const method = selectedConfig ? 'PUT' : 'POST';
      
      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(configData),
      });

      if (response.ok) {
        const savedConfig = await response.json();
        
        if (!selectedConfig) {
          setConfigurations(prev => [...prev, savedConfig]);
          setSelectedConfig(savedConfig.id);
        } else {
          setConfigurations(prev => 
            prev.map(c => c.id === selectedConfig ? savedConfig : c)
          );
        }

        toast({
          title: 'Configuration Saved',
          description: 'Your widget configuration has been saved successfully.',
        });
      } else {
        throw new Error('Failed to save configuration');
      }
    } catch (error) {
      toast({
        title: 'Save Failed',
        description: 'Failed to save widget configuration. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const generateScriptEmbed = () => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.chatbot-saas.com';
    const widgetUrl = process.env.NEXT_PUBLIC_WIDGET_CDN || 'https://cdn.chatbot-saas.com/widget.js';
    
    const dataAttributes = [
      `data-chatbot-id="${chatbot.id}"`,
      `data-base-url="${baseUrl}"`,
      `data-theme="${currentConfig.theme}"`,
      `data-position="${currentConfig.position}"`,
      `data-primary-color="${currentConfig.primary_color}"`,
      `data-secondary-color="${currentConfig.secondary_color}"`,
      `data-border-radius="${currentConfig.border_radius}"`,
      `data-bot-name="${advancedSettings.botName}"`,
      `data-greeting="${advancedSettings.greeting}"`,
      `data-enable-voice="${advancedSettings.enableVoice}"`,
      `data-auto-open="${currentConfig.auto_open}"`,
      `data-auto-open-delay="${currentConfig.auto_open_delay}"`,
      `data-max-width="${currentConfig.max_width}"`,
      `data-max-height="${currentConfig.max_height}"`,
      `data-show-avatar="${currentConfig.show_avatar}"`,
      `data-enable-typing="${currentConfig.enable_typing_indicator}"`,
      `data-enable-file-upload="${currentConfig.enable_file_upload}"`,
      `data-config-id="${selectedConfig || ''}"`,
    ];

    return `<!-- Chatbot Widget - ${chatbot.name} -->
<script 
  src="${widgetUrl}"
  ${dataAttributes.join('\n  ')}
  async>
</script>`;
  };

  const generateReactEmbed = () => {
    const props = [
      `chatbotId="${chatbot.id}"`,
      `theme="${currentConfig.theme}"`,
      `position="${currentConfig.position}"`,
      `primaryColor="${currentConfig.primary_color}"`,
      `secondaryColor="${currentConfig.secondary_color}"`,
      `borderRadius={${currentConfig.border_radius}}`,
      `botName="${advancedSettings.botName}"`,
      `greeting="${advancedSettings.greeting}"`,
      `enableVoice={${advancedSettings.enableVoice}}`,
      `autoOpen={${currentConfig.auto_open}}`,
      `autoOpenDelay={${currentConfig.auto_open_delay}}`,
      `maxWidth={${currentConfig.max_width}}`,
      `maxHeight={${currentConfig.max_height}}`,
      `showAvatar={${currentConfig.show_avatar}}`,
      `enableTyping={${currentConfig.enable_typing_indicator}}`,
      `enableFileUpload={${currentConfig.enable_file_upload}}`,
      selectedConfig ? `configId="${selectedConfig}"` : ''
    ].filter(Boolean);

    return `import { ChatbotWidget } from '@chatbot-saas/react';

function MyApp() {
  return (
    <div>
      {/* Your app content */}
      <ChatbotWidget
        ${props.join('\n        ')}
      />
    </div>
  );
}

export default MyApp;`;
  };

  const generateVueEmbed = () => {
    const props = [
      `:chatbot-id="'${chatbot.id}'"`,
      `theme="${currentConfig.theme}"`,
      `position="${currentConfig.position}"`,
      `:primary-color="'${currentConfig.primary_color}'"`,
      `:secondary-color="'${currentConfig.secondary_color}'"`,
      `:border-radius="${currentConfig.border_radius}"`,
      `:bot-name="'${advancedSettings.botName}'"`,
      `:greeting="'${advancedSettings.greeting}'"`,
      `:enable-voice="${advancedSettings.enableVoice}"`,
      `:auto-open="${currentConfig.auto_open}"`,
      `:auto-open-delay="${currentConfig.auto_open_delay}"`,
      `:max-width="${currentConfig.max_width}"`,
      `:max-height="${currentConfig.max_height}"`,
      `:show-avatar="${currentConfig.show_avatar}"`,
      `:enable-typing="${currentConfig.enable_typing_indicator}"`,
      `:enable-file-upload="${currentConfig.enable_file_upload}"`,
      selectedConfig ? `:config-id="'${selectedConfig}'"` : ''
    ].filter(Boolean);

    return `<template>
  <div>
    <!-- Your app content -->
    <ChatbotWidget
      ${props.join('\n      ')}
    />
  </div>
</template>

<script>
import { ChatbotWidget } from '@chatbot-saas/vue';

export default {
  components: {
    ChatbotWidget
  }
};
</script>`;
  };

  const generateWordPressCode = () => {
    return `<?php
/*
Plugin Name: ${chatbot.name} Chatbot
Description: Embed ${chatbot.name} chatbot widget
Version: 1.0
*/

function chatbot_widget_enqueue_scripts() {
    wp_enqueue_script(
        'chatbot-widget',
        'https://cdn.chatbot-saas.com/widget.js',
        array(),
        '1.0.0',
        true
    );
    
    wp_localize_script('chatbot-widget', 'chatbot_config', array(
        'chatbot_id' => '${chatbot.id}',
        'theme' => '${currentConfig.theme}',
        'position' => '${currentConfig.position}',
        'primary_color' => '${currentConfig.primary_color}',
        'bot_name' => '${advancedSettings.botName}',
        'greeting' => '${advancedSettings.greeting}',
        'auto_open' => ${currentConfig.auto_open ? 'true' : 'false'},
        'max_width' => ${currentConfig.max_width},
        'max_height' => ${currentConfig.max_height}
    ));
}
add_action('wp_enqueue_scripts', 'chatbot_widget_enqueue_scripts');

// Shortcode: [chatbot_widget]
function chatbot_widget_shortcode($atts) {
    return '<div id="chatbot-widget-container"></div>';
}
add_shortcode('chatbot_widget', 'chatbot_widget_shortcode');
?>`;
  };

  const getEmbedCode = () => {
    switch (activeTab) {
      case 'script-tag':
        return generateScriptEmbed();
      case 'react':
        return generateReactEmbed();
      case 'vue':
        return generateVueEmbed();
      case 'wordpress':
        return generateWordPressCode();
      default:
        return generateScriptEmbed();
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast({
        title: 'Copied!',
        description: 'Code copied to clipboard',
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast({
        title: 'Copy Failed',
        description: 'Failed to copy to clipboard',
        variant: 'destructive',
      });
    }
  };

  const updateConfig = (key: string, value: any) => {
    setCurrentConfig(prev => ({ ...prev, [key]: value }));
  };

  const updateAdvancedSettings = (key: string, value: any) => {
    setAdvancedSettings(prev => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-32 bg-gray-200 rounded mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Code2 className="h-6 w-6" />
            Enhanced Widget Builder
          </h2>
          <p className="text-muted-foreground">
            Professional widget customization with templates and advanced features
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button 
            onClick={() => setPreviewMode(previewMode === 'desktop' ? 'mobile' : 'desktop')}
            variant="outline"
            size="sm"
          >
            {previewMode === 'desktop' ? <Monitor className="h-4 w-4" /> : <Smartphone className="h-4 w-4" />}
            {previewMode === 'desktop' ? 'Desktop' : 'Mobile'}
          </Button>
          <Button onClick={saveConfiguration} disabled={saving} size="sm">
            {saving ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
            {saving ? 'Saving...' : 'Save Config'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Template Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Widget Templates
              </CardTitle>
              <CardDescription>
                Choose from professional templates or start with a custom design
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templates.slice(0, 6).map((template) => (
                  <div
                    key={template.id}
                    className={`relative p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedTemplate === template.id 
                        ? 'border-primary bg-primary/5' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => {
                      setSelectedTemplate(template.id);
                      applyTemplate(template.id);
                    }}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium">{template.name}</h4>
                          {template.is_premium && <Crown className="h-4 w-4 text-yellow-500" />}
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {template.description}
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="secondary">{template.category}</Badge>
                          <span className="text-xs text-muted-foreground">
                            {template.downloads_count} downloads
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Basic Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Basic Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Configuration Name</Label>
                  <Input
                    value={currentConfig.config_name}
                    onChange={(e) => updateConfig('config_name', e.target.value)}
                    placeholder="My Widget Config"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Deployment Status</Label>
                  <Select value={currentConfig.deployment_status} onValueChange={(value) => updateConfig('deployment_status', value)}>
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
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Theme</Label>
                  <Select value={currentConfig.theme} onValueChange={(value) => updateConfig('theme', value)}>
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
                  <Label>Position</Label>
                  <Select value={currentConfig.position} onValueChange={(value) => updateConfig('position', value)}>
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
                  <Label>Primary Color</Label>
                  <div className="flex gap-2">
                    <Input
                      type="color"
                      value={currentConfig.primary_color}
                      onChange={(e) => updateConfig('primary_color', e.target.value)}
                      className="w-16 h-10"
                    />
                    <Input
                      type="text"
                      value={currentConfig.primary_color}
                      onChange={(e) => updateConfig('primary_color', e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Secondary Color</Label>
                  <div className="flex gap-2">
                    <Input
                      type="color"
                      value={currentConfig.secondary_color}
                      onChange={(e) => updateConfig('secondary_color', e.target.value)}
                      className="w-16 h-10"
                    />
                    <Input
                      type="text"
                      value={currentConfig.secondary_color}
                      onChange={(e) => updateConfig('secondary_color', e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Border Radius: {currentConfig.border_radius}px</Label>
                <Slider
                  value={[currentConfig.border_radius]}
                  onValueChange={(value) => updateConfig('border_radius', value[0])}
                  max={50}
                  min={0}
                  step={1}
                  className="w-full"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Max Width: {currentConfig.max_width}px</Label>
                  <Slider
                    value={[currentConfig.max_width]}
                    onValueChange={(value) => updateConfig('max_width', value[0])}
                    max={800}
                    min={300}
                    step={10}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Max Height: {currentConfig.max_height}px</Label>
                  <Slider
                    value={[currentConfig.max_height]}
                    onValueChange={(value) => updateConfig('max_height', value[0])}
                    max={1000}
                    min={400}
                    step={10}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Advanced Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                Advanced Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Bot Name</Label>
                  <Input
                    value={advancedSettings.botName}
                    onChange={(e) => updateAdvancedSettings('botName', e.target.value)}
                    placeholder="Assistant"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Company Name</Label>
                  <Input
                    value={advancedSettings.companyName}
                    onChange={(e) => updateAdvancedSettings('companyName', e.target.value)}
                    placeholder="Your Company"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Welcome Message</Label>
                <Textarea
                  value={advancedSettings.greeting}
                  onChange={(e) => updateAdvancedSettings('greeting', e.target.value)}
                  placeholder="Hello! How can I help you today?"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label>Domain Restrictions (comma-separated)</Label>
                <Input
                  value={advancedSettings.domainRestrictions}
                  onChange={(e) => updateAdvancedSettings('domainRestrictions', e.target.value)}
                  placeholder="example.com, mydomain.com"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={currentConfig.auto_open}
                    onCheckedChange={(checked) => updateConfig('auto_open', checked)}
                  />
                  <Label>Auto Open Widget</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={advancedSettings.enableVoice}
                    onCheckedChange={(checked) => updateAdvancedSettings('enableVoice', checked)}
                  />
                  <Label>Enable Voice</Label>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={currentConfig.enable_file_upload}
                    onCheckedChange={(checked) => updateConfig('enable_file_upload', checked)}
                  />
                  <Label>File Upload</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={currentConfig.enable_typing_indicator}
                    onCheckedChange={(checked) => updateConfig('enable_typing_indicator', checked)}
                  />
                  <Label>Typing Indicator</Label>
                </div>
              </div>

              {currentConfig.auto_open && (
                <div className="space-y-2">
                  <Label>Auto Open Delay: {currentConfig.auto_open_delay}ms</Label>
                  <Slider
                    value={[currentConfig.auto_open_delay]}
                    onValueChange={(value) => updateConfig('auto_open_delay', value[0])}
                    max={10000}
                    min={1000}
                    step={500}
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Custom CSS */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brush className="h-5 w-5" />
                Custom CSS
              </CardTitle>
              <CardDescription>
                Add custom CSS to further customize your widget appearance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                value={advancedSettings.customCss}
                onChange={(e) => updateAdvancedSettings('customCss', e.target.value)}
                placeholder="/* Add your custom CSS here */
.chatbot-widget-container {
  /* Custom styles */
}"
                rows={8}
                className="font-mono text-sm"
              />
            </CardContent>
          </Card>
        </div>

        {/* Embed Code Panel */}
        <div className="space-y-6">
          {/* Live Preview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Live Preview
              </CardTitle>
              <CardDescription>
                Preview how your widget will appear
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className={`relative border rounded-lg overflow-hidden ${
                previewMode === 'mobile' ? 'w-full max-w-sm mx-auto' : 'w-full'
              }`}>
                <div className={`bg-gray-50 ${previewMode === 'mobile' ? 'h-96' : 'h-64'} flex items-center justify-center`}>
                  <div className="text-center">
                    <MessageSquare className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">Widget Preview</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {previewMode === 'mobile' ? 'Mobile View' : 'Desktop View'}
                    </p>
                  </div>
                </div>
                {/* Widget Button Preview */}
                <div className={`absolute ${
                  currentConfig.position === 'bottom-right' ? 'bottom-4 right-4' :
                  currentConfig.position === 'bottom-left' ? 'bottom-4 left-4' :
                  currentConfig.position === 'top-right' ? 'top-4 right-4' :
                  'top-4 left-4'
                }`}>
                  <div 
                    className="w-12 h-12 rounded-full flex items-center justify-center text-white shadow-lg cursor-pointer transform hover:scale-105 transition-transform"
                    style={{ backgroundColor: currentConfig.primary_color }}
                  >
                    <MessageSquare className="h-6 w-6" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Embed Code Generation */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code2 className="h-5 w-5" />
                Embed Code
              </CardTitle>
              <CardDescription>
                Copy and paste into your website
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid grid-cols-2 gap-0">
                  <TabsTrigger value="script-tag" className="text-xs">Script Tag</TabsTrigger>
                  <TabsTrigger value="react" className="text-xs">React</TabsTrigger>
                </TabsList>
                <TabsList className="grid grid-cols-2 gap-0 mt-2">
                  <TabsTrigger value="vue" className="text-xs">Vue.js</TabsTrigger>
                  <TabsTrigger value="wordpress" className="text-xs">WordPress</TabsTrigger>
                </TabsList>

                <div className="mt-4">
                  <Textarea
                    value={getEmbedCode()}
                    readOnly
                    className="min-h-[200px] font-mono text-xs"
                  />
                </div>
              </Tabs>

              <div className="flex gap-2">
                <Button
                  onClick={() => copyToClipboard(getEmbedCode())}
                  className="flex-1"
                  variant={copied ? "secondary" : "default"}
                >
                  {copied ? (
                    <>
                      <Check className="h-4 w-4 mr-2" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4 mr-2" />
                      Copy Code
                    </>
                  )}
                </Button>
                <Button variant="outline" size="icon">
                  <Download className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Performance
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Bundle Size</span>
                <Badge variant="secondary">~85KB</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span>Load Time</span>
                <Badge variant="secondary">~1.2s</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span>Mobile Optimized</span>
                <Badge variant={currentConfig.mobile_full_screen ? "default" : "secondary"}>
                  {currentConfig.mobile_full_screen ? "Yes" : "No"}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}