'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  LayoutDashboard, 
  MessageSquare, 
  FileText, 
  BarChart3, 
  Settings, 
  PlusCircle,
  Mic,
  Bot,
  Menu,
  X,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'Chatbots',
    href: '/dashboard/chatbots',
    icon: Bot,
    children: [
      { name: 'All Chatbots', href: '/dashboard/chatbots' },
      { name: 'Create New', href: '/dashboard/chatbots/new' },
      { name: 'Voice Chatbots', href: '/dashboard/chatbots?type=voice' },
      { name: 'Text Chatbots', href: '/dashboard/chatbots?type=text' },
    ],
  },
  {
    name: 'Analytics',
    href: '/dashboard/analytics',
    icon: BarChart3,
    children: [
      { name: 'Overview', href: '/dashboard/analytics' },
      { name: 'Usage', href: '/dashboard/analytics/usage' },
      { name: 'Conversations', href: '/dashboard/analytics/conversations' },
    ],
  },
  {
    name: 'Settings',
    href: '/dashboard/settings',
    icon: Settings,
  },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [expandedItems, setExpandedItems] = useState<string[]>(['Chatbots', 'Analytics']);

  const toggleExpanded = (itemName: string) => {
    setExpandedItems(prev => 
      prev.includes(itemName) 
        ? prev.filter(name => name !== itemName)
        : [...prev, itemName]
    );
  };

  return (
    <div className={cn(
      "flex flex-col bg-card border-r border-border transition-all duration-300",
      isCollapsed ? "w-16" : "w-64",
      "fixed inset-y-0 left-0 z-50 lg:relative lg:z-auto",
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-border">
        <div className={cn(
          "flex items-center space-x-3 transition-opacity duration-200",
          isCollapsed ? "opacity-0" : "opacity-100"
        )}>
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <Bot className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="text-lg font-bold text-foreground">Chatbot SaaS</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="hidden lg:flex h-8 w-8 p-0"
        >
          <Menu className="w-4 h-4" />
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => (
          <div key={item.name}>
            <div className="flex items-center">
              <Link
                href={item.href}
                className={cn(
                  'flex items-center flex-1 px-3 py-2.5 text-sm font-medium rounded-md transition-colors',
                  pathname === item.href || pathname.startsWith(item.href + '/')
                    ? 'bg-accent text-accent-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                )}
                title={isCollapsed ? item.name : undefined}
              >
                <item.icon className={cn("h-5 w-5", isCollapsed ? "" : "mr-3")} />
                {!isCollapsed && (
                  <span className="truncate">{item.name}</span>
                )}
              </Link>
              
              {item.children && !isCollapsed && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleExpanded(item.name)}
                  className="h-8 w-8 p-0 ml-1"
                >
                  {expandedItems.includes(item.name) ? (
                    <ChevronDown className="w-3 h-3" />
                  ) : (
                    <ChevronRight className="w-3 h-3" />
                  )}
                </Button>
              )}
            </div>
            
            {item.children && !isCollapsed && expandedItems.includes(item.name) && (
              <div className="ml-8 mt-1 space-y-1">
                {item.children.map((child) => (
                  <Link
                    key={child.name}
                    href={child.href}
                    className={cn(
                      'block px-3 py-2 text-sm rounded-md transition-colors',
                      pathname === child.href
                        ? 'bg-accent text-accent-foreground'
                        : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                    )}
                  >
                    {child.name}
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>

      {/* Footer - Hidden when collapsed */}
      {!isCollapsed && (
        <div className="p-4 border-t border-border">
          <Link
            href="/dashboard/chatbots/new"
            className="flex items-center justify-center w-full px-4 py-2.5 text-sm font-medium text-primary-foreground bg-primary rounded-md hover:bg-primary/90 transition-colors"
          >
            <PlusCircle className="w-4 h-4 mr-2" />
            Create Chatbot
          </Link>
        </div>
      )}
    </div>
  );
}

// Mobile Sidebar Component
export function MobileSidebar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 h-10 w-10 p-0"
      >
        <Menu className="w-5 h-5" />
      </Button>

      {/* Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out lg:hidden",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex h-full flex-col bg-card border-r border-border">
          {/* Mobile Header */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-border">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-bold text-foreground">Chatbot SaaS</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(false)}
              className="h-8 w-8 p-0"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>

          {/* Mobile Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => (
              <div key={item.name}>
                <Link
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className="flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-colors text-muted-foreground hover:text-foreground hover:bg-accent/50"
                >
                  <item.icon className="h-5 w-5 mr-3" />
                  <span>{item.name}</span>
                </Link>
                
                {item.children && (
                  <div className="ml-8 mt-1 space-y-1">
                    {item.children.map((child) => (
                      <Link
                        key={child.name}
                        href={child.href}
                        onClick={() => setIsOpen(false)}
                        className="block px-3 py-2 text-sm rounded-md transition-colors text-muted-foreground hover:text-foreground hover:bg-accent/50"
                      >
                        {child.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>

          {/* Mobile Footer */}
          <div className="p-4 border-t border-border">
            <Link
              href="/dashboard/chatbots/new"
              onClick={() => setIsOpen(false)}
              className="flex items-center justify-center w-full px-4 py-2.5 text-sm font-medium text-primary-foreground bg-primary rounded-md hover:bg-primary/90 transition-colors"
            >
              <PlusCircle className="w-4 h-4 mr-2" />
              Create Chatbot
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}