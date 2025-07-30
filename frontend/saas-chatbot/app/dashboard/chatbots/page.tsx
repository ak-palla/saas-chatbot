'use client';

import { Bot, Mic, MessageSquare, Settings, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Chatbots</h1>
          <p className="text-muted-foreground">
            Manage your AI chatbots and their configurations
          </p>
        </div>
        <Button>
          <Bot className="w-4 h-4 mr-2" />
          Create Chatbot
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Chatbots</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Conversations</TableHead>
                <TableHead>Documents</TableHead>
                <TableHead>Last Active</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {chatbots.map((chatbot) => (
                <TableRow key={chatbot.id}>
                  <TableCell className="font-medium">{chatbot.name}</TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      {chatbot.type === 'voice' ? (
                        <Mic className="w-4 h-4 mr-2 text-purple-600" />
                      ) : (
                        <MessageSquare className="w-4 h-4 mr-2 text-blue-600" />
                      )}
                      <span className="capitalize">{chatbot.type}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        chatbot.status === 'active'
                          ? 'default'
                          : chatbot.status === 'training'
                          ? 'secondary'
                          : 'outline'
                      }
                    >
                      {chatbot.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{chatbot.conversations.toLocaleString()}</TableCell>
                  <TableCell>{chatbot.documents}</TableCell>
                  <TableCell>{chatbot.lastActive}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Switch defaultChecked={chatbot.status === 'active'} />
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem>View Details</DropdownMenuItem>
                          <DropdownMenuItem>Edit Configuration</DropdownMenuItem>
                          <DropdownMenuItem>Test Chatbot</DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-destructive">
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
        </CardContent>
      </Card>
    </div>
  );
}