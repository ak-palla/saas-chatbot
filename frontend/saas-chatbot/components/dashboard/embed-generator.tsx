import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Copy, Check, Code2, Settings } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface EmbedGeneratorProps {
  chatbot: {
    id: string;
    name: string;
    appearance_config?: any;
    behavior_config?: any;
  };
}

export function EmbedGenerator({ chatbot }: EmbedGeneratorProps) {
  const [copied, setCopied] = useState(false);
  const [config, setConfig] = useState({
    theme: chatbot.appearance_config?.theme || 'light',
    position: chatbot.appearance_config?.position || 'bottom-right',
    primaryColor: chatbot.appearance_config?.primaryColor || '#3b82f6',
    enableVoice: chatbot.behavior_config?.enableVoice || false,
    autoOpen: false,
    maxWidth: 400,
    maxHeight: 600,
    greeting: chatbot.behavior_config?.greetingMessage || 'Hello! How can I help you today?',
    botName: chatbot.behavior_config?.botName || chatbot.name || 'Assistant'
  });

  const { toast } = useToast();

  const generateEmbedCode = () => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const widgetUrl = process.env.NEXT_PUBLIC_WIDGET_URL || 'http://localhost:3000/widget/embed.js';
    
    const params = new URLSearchParams({
      chatbotId: chatbot.id,
      baseUrl,
      theme: config.theme,
      position: config.position,
      primaryColor: config.primaryColor,
      botName: config.botName,
      greeting: config.greeting,
      enableVoice: String(config.enableVoice),
      autoOpen: String(config.autoOpen),
      maxWidth: String(config.maxWidth),
      maxHeight: String(config.maxHeight)
    });

    return `<!-- Chatbot SaaS Widget -->
<script 
  src="${widgetUrl}"
  data-chatbot-id="${chatbot.id}"
  data-base-url="${baseUrl}"
  data-theme="${config.theme}"
  data-position="${config.position}"
  data-primary-color="${config.primaryColor}"
  data-bot-name="${config.botName}"
  data-greeting="${config.greeting}"
  data-enable-voice="${config.enableVoice}"
  data-auto-open="${config.autoOpen}"></script>`;
  };

  const generateNpmCode = () => {
    return `npm install @chatbot-saas/widget`;
  };

  const generateManualCode = () => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    return `<!-- Include widget script -->
<script src="${process.env.NEXT_PUBLIC_WIDGET_URL || 'http://localhost:3000/widget/dist/widget.umd.js'}"></script>

<!-- Initialize widget -->
<script>
  ChatbotSaaS.init({
    chatbotId: '${chatbot.id}',
    baseUrl: '${baseUrl}',
    theme: '${config.theme}',
    position: '${config.position}',
    primaryColor: '${config.primaryColor}',
    botName: '${config.botName}',
    greeting: '${config.greeting}',
    enableVoice: ${config.enableVoice},
    autoOpen: ${config.autoOpen},
    maxWidth: ${config.maxWidth},
    maxHeight: ${config.maxHeight}
  });
</script>`;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast({
      title: 'Copied!',
      description: 'Code copied to clipboard',
    });
    setTimeout(() => setCopied(false), 2000);
  };

  const updateConfig = (key: string, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Code2 className="h-5 w-5" />
            Widget Embed Code
          </CardTitle>
          <CardDescription>
            Generate embeddable code for your chatbot widget
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <Tabs defaultValue="embed" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="embed">Script Tag</TabsTrigger>
              <TabsTrigger value="npm">NPM</TabsTrigger>
              <TabsTrigger value="manual">Manual</TabsTrigger>
            </TabsList>
            
            <TabsContent value="embed" className="space-y-4">
              <div className="space-y-2">
                <Label>Embed Code</Label>
                <Textarea
                  value={generateEmbedCode()}
                  readOnly
                  className="min-h-[200px] font-mono text-sm"
                />
              </div>
              <Button
                onClick={() => copyToClipboard(generateEmbedCode())}
                className="w-full"
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
            </TabsContent>
            
            <TabsContent value="npm" className="space-y-4">
              <div className="space-y-2">
                <Label>Install Package</Label>
                <Textarea
                  value={generateNpmCode()}
                  readOnly
                  className="font-mono text-sm"
                />
              </div>
              <Button
                onClick={() => copyToClipboard(generateNpmCode())}
                className="w-full"
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
                    Copy Command
                  </>
                )}
              </Button>
            </TabsContent>
            
            <TabsContent value="manual" className="space-y-4">
              <div className="space-y-2">
                <Label>Manual Integration</Label>
                <Textarea
                  value={generateManualCode()}
                  readOnly
                  className="min-h-[300px] font-mono text-sm"
                />
              </div>
              <Button
                onClick={() => copyToClipboard(generateManualCode())}
                className="w-full"
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
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Widget Configuration
          </CardTitle>
          <CardDescription>
            Customize the appearance and behavior of your widget
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="theme">Theme</Label>
              <select
                id="theme"
                value={config.theme}
                onChange={(e) => updateConfig('theme', e.target.value)}
                className="w-full p-2 border rounded-md"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="position">Position</Label>
              <select
                id="position"
                value={config.position}
                onChange={(e) => updateConfig('position', e.target.value)}
                className="w-full p-2 border rounded-md"
              >
                <option value="bottom-right">Bottom Right</option>
                <option value="bottom-left">Bottom Left</option>
                <option value="top-right">Top Right</option>
                <option value="top-left">Top Left</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="primaryColor">Primary Color</Label>
            <div className="flex gap-2">
              <Input
                id="primaryColor"
                type="color"
                value={config.primaryColor}
                onChange={(e) => updateConfig('primaryColor', e.target.value)}
                className="w-16 h-10"
              />
              <Input
                type="text"
                value={config.primaryColor}
                onChange={(e) => updateConfig('primaryColor', e.target.value)}
                className="flex-1"
                placeholder="#3b82f6"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="botName">Bot Name</Label>
            <Input
              id="botName"
              value={config.botName}
              onChange={(e) => updateConfig('botName', e.target.value)}
              placeholder="Your Assistant"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="greeting">Welcome Message</Label>
            <Textarea
              id="greeting"
              value={config.greeting}
              onChange={(e) => updateConfig('greeting', e.target.value)}
              placeholder="Hello! How can I help you today?"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="flex items-center justify-between">
                Enable Voice
                <Switch
                  checked={config.enableVoice}
                  onCheckedChange={(checked) => updateConfig('enableVoice', checked)}
                />
              </Label>
            </div>
            
            <div className="space-y-2">
              <Label className="flex items-center justify-between">
                Auto Open
                <Switch
                  checked={config.autoOpen}
                  onCheckedChange={(checked) => updateConfig('autoOpen', checked)}
                />
              </Label>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default EmbedGenerator;