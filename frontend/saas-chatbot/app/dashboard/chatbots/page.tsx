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
import { useState } from 'react';
import { cn } from '@/lib/utils';

const chatbots = [
  {
    id: 1,
    name: 'Customer Support Bot',
    type: 'text',
    status: 'active',
    conversations: 1234,
    documents: 45,
    lastActive: '2 hours ago',
    created: '2024-01-15',
  },
  {
    id: 2,
    name: 'Voice Assistant',
    type: 'voice',
    status: 'active',
    conversations: 567,
    documents: 23,
    lastActive: '5 minutes ago',
    created: '2024-01-20',
  },
  {
    id: 3,
    name: 'Sales Assistant',
    type: 'text',
    status: 'training',
    conversations: 89,
    documents: 12,
    lastActive: '1 day ago',
    created: '2024-01-25',
  },
  {
    id: 4,
    name: 'HR Helper',
    type: 'text',
    status: 'inactive',
    conversations: 234,
    documents: 8,
    lastActive: '3 days ago',
    created: '2024-01-10',
  },
];

export default function ChatbotsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');

  const filteredChatbots = chatbots.filter(chatbot => {
    const matchesSearch = chatbot.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = selectedType === 'all' || chatbot.type === selectedType;
    return matchesSearch && matchesType;
  });

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
                {filteredChatbots.map((chatbot) => (
                  <TableRow 
                    key={chatbot.id} 
                    className="hover:bg-accent/50 transition-colors border-border"
                  >
                    <TableCell className="font-medium text-foreground">
                      {chatbot.name}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {chatbot.type === 'voice' ? (
                          <Mic className="w-4 h-4 text-primary" />
                        ) : (
                          <MessageSquare className="w-4 h-4 text-primary" />
                        )}
                        <span className="capitalize text-muted-foreground">
                          {chatbot.type}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge
                        className={cn(
                          "font-medium",
                          getStatusColor(chatbot.status)
                        )}
                        variant="outline"
                      >
                        {chatbot.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {chatbot.conversations.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {chatbot.documents}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {chatbot.lastActive}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center justify-end gap-2">
                        <Switch 
                          defaultChecked={chatbot.status === 'active'} 
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
                            <DropdownMenuItem className="gap-2">
                              <Eye className="w-4 h-4" />
                              View Details
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
                ))}
              </TableBody>
            </Table>
          </div>
          
          {filteredChatbots.length === 0 && (
            <div className="text-center py-12">
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
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}