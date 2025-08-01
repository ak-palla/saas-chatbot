'use client';

import { Plus, Upload, Play, BarChart3, Settings, MessageCircle, Mic, Code, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';

const quickActions = [
  {
    title: 'Create New Chatbot',
    description: 'Build your first AI assistant',
    icon: Plus,
    href: '/dashboard/chatbots/new',
    color: 'bg-gradient-to-br from-blue-500 to-blue-600',
    hoverColor: 'hover:from-blue-600 hover:to-blue-700',
    textColor: 'text-white',
    featured: true,
  },
  {
    title: 'Upload Documents',
    description: 'Add knowledge to your bots',
    icon: Upload,
    href: '/dashboard/documents',
    color: 'bg-gradient-to-br from-purple-500 to-purple-600',
    hoverColor: 'hover:from-purple-600 hover:to-purple-700',
    textColor: 'text-white',
  },
  {
    title: 'View Analytics',
    description: 'Track performance & insights',
    icon: BarChart3,
    href: '/dashboard/analytics',
    color: 'bg-gradient-to-br from-green-500 to-green-600',
    hoverColor: 'hover:from-green-600 hover:to-green-700',
    textColor: 'text-white',
  },
];

const shortcuts = [
  {
    title: 'Text Bots',
    icon: MessageCircle,
    href: '/dashboard/chatbots?type=text',
    count: '12',
  },
  {
    title: 'Voice Bots',
    icon: Mic,
    href: '/dashboard/chatbots?type=voice',
    count: '3',
  },
  {
    title: 'Widget Code',
    icon: Code,
    href: '/dashboard/chatbots?tab=embed',
    count: '5',
  },
  {
    title: 'Test Bots',
    icon: Play,
    href: '/dashboard/chatbots?tab=test',
    count: '8',
  },
];

export function QuickActions() {
  return (
    <div className="space-y-6">
      {/* Main Quick Actions */}
      <Card className="border-2 border-dashed border-blue-200 dark:border-blue-800 bg-gradient-to-br from-blue-50/50 to-purple-50/50 dark:from-blue-950/20 dark:to-purple-950/20">
        <CardHeader className="text-center pb-4">
          <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
            <Bot className="h-8 w-8 text-white" />
          </div>
          <CardTitle className="text-2xl">Get Started</CardTitle>
          <p className="text-muted-foreground">Choose an action to begin building your chatbot</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-3 gap-4">
            {quickActions.map((action) => (
              <Link key={action.title} href={action.href}>
                <Card className={`group cursor-pointer transition-all duration-300 hover:shadow-xl ${action.featured ? 'ring-2 ring-blue-200 dark:ring-blue-800' : ''}`}>
                  <CardContent className="p-6 text-center">
                    <div className={`w-14 h-14 mx-auto mb-4 ${action.color} ${action.hoverColor} rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110`}>
                      <action.icon className={`h-7 w-7 ${action.textColor}`} />
                    </div>
                    <h3 className="font-semibold text-lg mb-2">{action.title}</h3>
                    <p className="text-sm text-muted-foreground">{action.description}</p>
                    {action.featured && (
                      <div className="mt-3 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full inline-block">
                        Recommended
                      </div>
                    )}
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Shortcuts */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Quick Shortcuts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {shortcuts.map((shortcut) => (
              <Link key={shortcut.title} href={shortcut.href}>
                <div className="group p-4 rounded-lg border-2 border-dashed border-muted hover:border-blue-300 dark:hover:border-blue-700 transition-all duration-300 hover:bg-muted/50 cursor-pointer">
                  <div className="flex flex-col items-center text-center space-y-2">
                    <shortcut.icon className="w-6 h-6 text-muted-foreground group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                    <div className="font-medium text-sm">{shortcut.title}</div>
                    <div className="text-xs text-muted-foreground">{shortcut.count} active</div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}