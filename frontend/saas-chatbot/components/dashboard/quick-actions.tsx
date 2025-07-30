'use client';

import { Plus, Upload, Settings, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const actions = [
  {
    title: 'Create Chatbot',
    description: 'Build a new AI chatbot',
    icon: Plus,
    href: '/dashboard/chatbots/new',
    variant: 'default' as const,
  },
  {
    title: 'Upload Documents',
    description: 'Add training data',
    icon: Upload,
    href: '/dashboard/documents',
    variant: 'outline' as const,
  },
  {
    title: 'Test Chatbot',
    description: 'Test your chatbot',
    icon: Play,
    href: '/dashboard/chatbots',
    variant: 'outline' as const,
  },
];

export function QuickActions() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {actions.map((action) => (
          <Button
            key={action.title}
            variant={action.variant}
            className="w-full justify-start"
            onClick={() => window.location.href = action.href}
          >
            <action.icon className="w-4 h-4 mr-2" />
            <div className="text-left">
              <div className="font-medium">{action.title}</div>
              <div className="text-xs text-muted-foreground">{action.description}</div>
            </div>
          </Button>
        ))}
      </CardContent>
    </Card>
  );
}