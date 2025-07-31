'use client';

import { useState } from 'react';
import { X, Send, Mic, Paperclip, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface ChatbotConfig {
  name: string;
  appearance_config: {
    primaryColor: string;
    position: string;
    theme: string;
    greetingMessage: string;
    welcomeTitle: string;
    botName: string;
    showAvatar: boolean;
    avatarUrl: string;
  };
  behavior_config: {
    enableVoice: boolean;
    enableTypingIndicator: boolean;
    enableSuggestions: boolean;
    suggestions: string[];
    enableFileUpload: boolean;
  };
}

interface ChatbotPreviewProps {
  config: ChatbotConfig;
}

export function ChatbotPreview({ config }: ChatbotPreviewProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages] = useState([
    {
      id: 1,
      text: config.appearance_config.greetingMessage,
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);

  const getWidgetPosition = () => {
    switch (config.appearance_config.position) {
      case 'bottom-right': return 'bottom-4 right-4';
      case 'bottom-left': return 'bottom-4 left-4';
      case 'top-right': return 'top-4 right-4';
      case 'top-left': return 'top-4 left-4';
      default: return 'bottom-4 right-4';
    }
  };

  const getThemeClass = () => {
    switch (config.appearance_config.theme) {
      case 'dark': return 'bg-gray-900 text-white';
      case 'light': return 'bg-white text-gray-900';
      default: return 'bg-white text-gray-900';
    }
  };

  const ChatWidget = () => (
    <div className={cn(
      "fixed z-50 transition-all duration-300",
      getWidgetPosition()
    )}>
      <Card className={cn(
        "w-80 h-96 shadow-2xl rounded-lg overflow-hidden",
        getThemeClass()
      )}>
        <div 
          className="flex items-center justify-between p-4 border-b"
          style={{ backgroundColor: config.appearance_config.primaryColor }}
        >
          <div className="flex items-center space-x-2">
            {config.appearance_config.showAvatar && (
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                {config.appearance_config.avatarUrl ? (
                  <img src={config.appearance_config.avatarUrl} alt="Avatar" className="w-full h-full rounded-full object-cover" />
                ) : (
                  <BotIcon className="w-4 h-4 text-white" />
                )}
              </div>
            )}
            <div>
              <h3 className="font-semibold text-white">{config.appearance_config.botName}</h3>
              <Badge variant="secondary" className="text-xs">Online</Badge>
            </div>
          </div>
          
          <Button variant="ghost" size="sm" className="text-white hover:bg-white/20" onClick={() => setIsOpen(false)}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <div className="text-center mb-4">
            <h4 className="font-semibold">{config.appearance_config.welcomeTitle}</h4>
            <p className="text-sm text-muted-foreground mt-1">{config.appearance_config.greetingMessage}</p>
          </div>

          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex",
                message.sender === 'bot' ? 'justify-start' : 'justify-end'
              )}
            >
              <div
                className={cn(
                  "max-w-xs px-3 py-2 rounded-lg",
                  message.sender === 'bot'
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-white'
                )}
                style={message.sender === 'user' ? { backgroundColor: config.appearance_config.primaryColor } : {}}
              >
                {message.text}
              </div>
            </div>
          ))}

          {config.behavior_config.enableTypingIndicator && (
            <div className="flex items-center space-x-1 text-sm text-muted-foreground">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              <span>Typing...</span>
            </div>
          )}
        </div>

        <div className="border-t p-4">
          <div className="flex items-center space-x-2">
            <Input
              placeholder="Type a message..."
              className="flex-1"
              disabled
            />
            
            <Button size="sm" style={{ backgroundColor: config.appearance_config.primaryColor }}>
              <Send className="w-4 h-4" />
            </Button>
            
            {config.behavior_config.enableVoice && (
              <Button variant="outline" size="sm">
                <Mic className="w-4 h-4" />
              </Button>
            )}
            
            {config.behavior_config.enableFileUpload && (
              <Button variant="outline" size="sm">
                <Paperclip className="w-4 h-4" />
              </Button>
            )}
          </div>

          {config.behavior_config.enableSuggestions && config.behavior_config.suggestions.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {config.behavior_config.suggestions.slice(0, 3).map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="text-xs"
                  disabled
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );

  const BotIcon = ({ className }: { className?: string }) => (
    <svg
      className={className}
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.38-1 1.72V7h2a7 7 0 0 1 7 7v2h2a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h2v-2a7 7 0 0 1 7-7h2V4.72c-.6-.34-1-.98-1-1.72a2 2 0 0 1 2-2z" />
      <circle cx="9" cy="13" r="1" />
      <circle cx="15" cy="13" r="1" />
    </svg>
  );

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Eye className="w-4 h-4 mr-2" />
          Preview
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Chatbot Preview</DialogTitle>
        </DialogHeader>
        
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <h3 className="font-semibold mb-2">Widget Preview</h3>
            <div className="relative bg-gray-100 rounded-lg p-4 h-96">
              <ChatWidget />
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold mb-2">Embed Preview</h3>
            <div className="bg-gray-100 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-2">Your website content here...</p>
              <div className="mt-4 p-2 bg-white rounded border">
                <p className="text-xs text-gray-500">This shows how the chatbot widget appears on your website</p>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

