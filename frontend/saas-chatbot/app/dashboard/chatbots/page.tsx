'use client';

import { Bot, Mic, MessageSquare, Settings, MoreVertical, Search, Filter, Plus, Eye, Edit, Trash2, Play } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Header } from '@/components/dashboard/header';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { apiService } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';

export default function ChatbotsPage() {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [chatbots, setChatbots] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchChatbots = async () => {
      setIsLoading(true);
      setError(null);

      try {
        console.log('📋 Fetching user chatbots...');
        const chatbotsData = await apiService.getChatbots();
        console.log('✅ Chatbots loaded:', chatbotsData);
        setChatbots(chatbotsData || []);
      } catch (err) {
        console.error('❌ Error fetching chatbots:', err);
        
        let errorMessage = 'Failed to load chatbots';
        if (err instanceof Error) {
          errorMessage = err.message;
        }
        
        // Add more specific error messages
        if (errorMessage.includes('Authentication failed')) {
          errorMessage = 'Please log in to view your chatbots';
        } else if (errorMessage.includes('Failed to fetch')) {
          errorMessage = 'Unable to connect to server. Please check if the backend is running.';
        }
        
        setError(errorMessage);
        
        toast({
          title: "Error Loading Chatbots",
          description: errorMessage,
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchChatbots();
  }, [toast]);

  const filteredChatbots = chatbots.filter(chatbot => {
    const matchesSearch = chatbot.name?.toLowerCase().includes(searchQuery.toLowerCase()) || false;
    // For now, treat all chatbots as 'text' type since we don't have voice classification yet
    const matchesType = selectedType === 'all' || selectedType === 'text';
    return matchesSearch && matchesType;
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
    
    return formatDate(dateString);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-success/10 text-success border-success/20';
      case 'training':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'inactive':
        return 'bg-muted text-muted-foreground border-border';
      default:
        return 'bg-muted text-muted-foreground border-border';
    }
  };

  return (
    <div className="space-y-8">
      <Header 
        title="Chatbots" 
        description="Manage your AI chatbots and their configurations"
      />

      <Card className="shadow-sm">
        <CardHeader className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <CardTitle className="text-lg font-semibold">All Chatbots</CardTitle>
            
            {/* Search and Filter Controls */}
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search chatbots..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 w-full sm:w-64"
                />
              </div>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="gap-2">
                    <Filter className="h-4 w-4" />
                    {selectedType === 'all' ? 'All Types' : selectedType === 'voice' ? 'Voice' : 'Text'}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setSelectedType('all')}>
                    All Types
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSelectedType('text')}>
                    Text Chatbots
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setSelectedType('voice')}>
                    Voice Chatbots
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <div className="rounded-md border border-border">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent border-border">
                  <TableHead className="font-semibold text-foreground">Name</TableHead>
                  <TableHead className="font-semibold text-foreground">Type</TableHead>
                  <TableHead className="font-semibold text-foreground">Status</TableHead>
                  <TableHead className="font-semibold text-foreground">Conversations</TableHead>
                  <TableHead className="font-semibold text-foreground">Documents</TableHead>
                  <TableHead className="font-semibold text-foreground">Last Active</TableHead>
                  <TableHead className="font-semibold text-foreground text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-12">
                      <LoadingSpinner size="lg" />
                      <div className="mt-4 text-muted-foreground">Loading chatbots...</div>
                    </TableCell>
                  </TableRow>
                ) : error ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-12">
                      <div className="text-destructive">
                        <Bot className="mx-auto h-12 w-12 text-destructive/50" />
                        <h3 className="mt-4 text-lg font-medium">Error Loading Chatbots</h3>
                        <p className="mt-2 text-sm text-muted-foreground">{error}</p>
                        <div className="mt-6">
                          <Button 
                            onClick={() => window.location.reload()} 
                            variant="outline"
                          >
                            Try Again
                          </Button>
                        </div>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : filteredChatbots.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-12">
                      <Bot className="mx-auto h-12 w-12 text-muted-foreground/50" />
                      <h3 className="mt-4 text-lg font-medium text-foreground">No chatbots found</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        {searchQuery ? 'No chatbots match your search criteria.' : 'Get started by creating your first chatbot.'}
                      </p>
                      {!searchQuery && (
                        <div className="mt-6">
                          <Link href="/dashboard/chatbots/new">
                            <Button>
                              <Plus className="w-4 h-4 mr-2" />
                              Create Chatbot
                            </Button>
                          </Link>
                        </div>
                      )}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredChatbots.map((chatbot) => (
                    <TableRow 
                      key={chatbot.id} 
                      className="hover:bg-accent/50 transition-colors border-border"
                    >
                      <TableCell className="font-medium text-foreground">
                        <Link 
                          href={`/dashboard/chatbots/${chatbot.id}`}
                          className="hover:text-primary transition-colors"
                        >
                          {chatbot.name}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <MessageSquare className="w-4 h-4 text-primary" />
                          <span className="capitalize text-muted-foreground">
                            Text
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          className={cn(
                            "font-medium",
                            getStatusColor(chatbot.is_active ? 'active' : 'inactive')
                          )}
                          variant="outline"
                        >
                          {chatbot.is_active ? 'active' : 'inactive'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        0
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        0
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {getRelativeTime(chatbot.created_at)}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center justify-end gap-2">
                          <Switch 
                            defaultChecked={chatbot.is_active} 
                            size="sm"
                          />
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                <MoreVertical className="w-4 h-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-48">
                              <DropdownMenuLabel className="text-xs font-medium text-muted-foreground">
                                Actions
                              </DropdownMenuLabel>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem asChild>
                                <Link href={`/dashboard/chatbots/${chatbot.id}`} className="gap-2">
                                  <Eye className="w-4 h-4" />
                                  View Details
                                </Link>
                              </DropdownMenuItem>
                              <DropdownMenuItem asChild>
                                <Link href={`/dashboard/chatbots/${chatbot.id}/edit`} className="gap-2">
                                  <Edit className="w-4 h-4" />
                                  Edit Configuration
                                </Link>
                              </DropdownMenuItem>
                              <DropdownMenuItem className="gap-2">
                                <Play className="w-4 h-4" />
                                Test Chatbot
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem className="text-destructive gap-2">
                                <Trash2 className="w-4 h-4" />
                                Delete Chatbot
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}