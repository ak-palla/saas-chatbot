'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft, 
  Settings, 
  Share2, 
  MoreVertical, 
  Power, 
  PowerOff,
  Copy,
  ExternalLink,
  Trash2
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useToast } from '@/components/ui/use-toast';

interface ChatbotHeaderProps {
  chatbot: any;
}

export function ChatbotHeader({ chatbot }: ChatbotHeaderProps) {
  const router = useRouter();
  const { toast } = useToast();
  const [isToggling, setIsToggling] = useState(false);

  const handleGoBack = () => {
    router.push('/dashboard/chatbots');
  };

  const handleToggleStatus = async () => {
    setIsToggling(true);
    try {
      // In a real app, this would call the API to toggle chatbot status
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast({
        title: `Chatbot ${chatbot.is_active ? 'Deactivated' : 'Activated'}`,
        description: `${chatbot.name} is now ${chatbot.is_active ? 'inactive' : 'active'}.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update chatbot status.",
        variant: "destructive",
      });
    } finally {
      setIsToggling(false);
    }
  };

  const handleCopyId = () => {
    navigator.clipboard.writeText(chatbot.id);
    toast({
      title: "Copied",
      description: "Chatbot ID copied to clipboard.",
    });
  };

  const handleShare = () => {
    const url = `${window.location.origin}/chat/${chatbot.id}`;
    navigator.clipboard.writeText(url);
    toast({
      title: "Link Copied",
      description: "Chatbot link copied to clipboard.",
    });
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this chatbot? This action cannot be undone.')) {
      return;
    }

    try {
      // In a real app, this would call the API to delete the chatbot
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast({
        title: "Chatbot Deleted",
        description: `${chatbot.name} has been deleted.`,
      });
      
      router.push('/dashboard/chatbots');
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete chatbot.",
        variant: "destructive",
      });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleGoBack}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Chatbots
            </Button>
            
            <div className="h-6 w-px bg-border" />
            
            <div className="space-y-1">
              <div className="flex items-center space-x-3">
                <h1 className="text-2xl font-bold">{chatbot.name}</h1>
                <Badge 
                  variant={chatbot.is_active ? "default" : "secondary"}
                  className={chatbot.is_active ? 
                    "bg-green-100 text-green-800 hover:bg-green-100" : 
                    "bg-gray-100 text-gray-800 hover:bg-gray-100"
                  }
                >
                  {chatbot.is_active ? (
                    <>
                      <Power className="h-3 w-3 mr-1" />
                      Active
                    </>
                  ) : (
                    <>
                      <PowerOff className="h-3 w-3 mr-1" />
                      Inactive
                    </>
                  )}
                </Badge>
              </div>
              <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                <span>Created {formatDate(chatbot.created_at)}</span>
                <span>•</span>
                <span>Model: {chatbot.model}</span>
                <span>•</span>
                <span>ID: {chatbot.id.slice(0, 8)}...</span>
              </div>
              {chatbot.description && (
                <p className="text-sm text-muted-foreground mt-1">
                  {chatbot.description}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleShare}
              className="flex items-center gap-2"
            >
              <Share2 className="h-4 w-4" />
              Share
            </Button>

            <Button
              variant={chatbot.is_active ? "destructive" : "default"}
              size="sm"
              onClick={handleToggleStatus}
              disabled={isToggling}
              className="flex items-center gap-2"
            >
              {chatbot.is_active ? (
                <>
                  <PowerOff className="h-4 w-4" />
                  {isToggling ? 'Deactivating...' : 'Deactivate'}
                </>
              ) : (
                <>
                  <Power className="h-4 w-4" />
                  {isToggling ? 'Activating...' : 'Activate'}
                </>
              )}
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={handleCopyId}>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy ID
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => window.open(`/chat/${chatbot.id}`, '_blank')}>
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open Chat
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => router.push(`/dashboard/chatbots/${chatbot.id}/settings`)}>
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleDelete} className="text-destructive">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Chatbot
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}