'use client';

import { Bot, MessageSquare, FileText, Users, TrendingUp, TrendingDown, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { useDashboardStats } from '@/lib/hooks/use-analytics';

interface StatCardProps {
  title: string;
  value: number;
  change?: string;
  changeText: string;
  trend: 'up' | 'down' | 'neutral';
  icon: React.ElementType;
  color: string;
  bgColor: string;
  isPrimary: boolean;
  isLoading?: boolean;
}

function StatCard({
  title,
  value,
  change,
  changeText,
  trend,
  icon: Icon,
  color,
  bgColor,
  isPrimary,
  isLoading,
}: StatCardProps) {
  return (
    <Card 
      className={cn(
        "transition-all duration-200 hover:shadow-sm",
        isPrimary ? "lg:col-span-2 border-primary/20" : "lg:col-span-1"
      )}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className={cn(
          "font-medium text-foreground/80",
          isPrimary ? "text-base" : "text-sm"
        )}>
          {title}
        </CardTitle>
        <div className={cn('p-2 rounded-lg transition-colors', bgColor)}>
          <Icon className={cn(
            color,
            isPrimary ? 'h-5 w-5' : 'h-4 w-4'
          )} />
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className={cn(
          "font-bold text-foreground",
          isPrimary ? "text-3xl" : "text-2xl"
        )}>
          {isLoading ? (
            <Loader2 className="h-6 w-6 animate-spin" />
          ) : (
            value.toLocaleString()
          )}
        </div>
        <div className="flex items-center space-x-1">
          {trend === 'up' && change && (
            <TrendingUp className="h-3 w-3 text-success" />
          )}
          {trend === 'down' && change && (
            <TrendingDown className="h-3 w-3 text-destructive" />
          )}
          <p className="text-xs text-muted-foreground">
            {change && (
              <span className={cn(
                "font-medium",
                trend === 'up' ? "text-success" : 
                trend === 'down' ? "text-destructive" : "text-muted-foreground"
              )}>
                {change}
              </span>
            )}
            {change && changeText && ' '}
            <span>{changeText}</span>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export function DashboardStats() {
  const { data: stats, isLoading, error } = useDashboardStats();

  // Show loading skeleton
  if (isLoading) {
    const loadingStats = [
      { title: 'Active Conversations', isPrimary: true },
      { title: 'Total Chatbots', isPrimary: false },
      { title: 'Documents Processed', isPrimary: false },
      { title: 'Active Sessions', isPrimary: false },
    ];

    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        {loadingStats.map((stat) => (
          <StatCard
            key={stat.title}
            title={stat.title}
            value={0}
            changeText="Loading..."
            trend="neutral"
            icon={MessageSquare}
            color="text-muted-foreground"
            bgColor="bg-muted/30"
            isPrimary={stat.isPrimary}
            isLoading={true}
          />
        ))}
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        <Card className="lg:col-span-7">
          <CardContent className="p-6">
            <p className="text-center text-muted-foreground">
              Failed to load dashboard stats. Please try again later.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Real data from API
  const statsConfig = [
    {
      title: 'Active Conversations',
      value: stats?.total_conversations || 0,
      change: '+12%', // TODO: Calculate from historical data
      changeText: 'from last week',
      trend: 'up' as const,
      icon: MessageSquare,
      color: 'text-primary',
      bgColor: 'bg-primary/5',
      isPrimary: true,
    },
    {
      title: 'Total Chatbots',
      value: stats?.total_chatbots || 0,
      change: '+2', // TODO: Calculate from historical data
      changeText: 'this month',
      trend: 'up' as const,
      icon: Bot,
      color: 'text-muted-foreground',
      bgColor: 'bg-muted/30',
      isPrimary: false,
    },
    {
      title: 'Documents Processed',
      value: stats?.total_documents || 0,
      change: '+8', // TODO: Calculate from historical data
      changeText: 'this week',
      trend: 'up' as const,
      icon: FileText,
      color: 'text-muted-foreground',
      bgColor: 'bg-muted/30',
      isPrimary: false,
    },
    {
      title: 'Active Sessions',
      value: stats?.active_sessions || 0,
      change: '',
      changeText: 'right now',
      trend: 'neutral' as const,
      icon: Users,
      color: 'text-muted-foreground',
      bgColor: 'bg-muted/30',
      isPrimary: false,
    },
  ];

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
      {statsConfig.map((stat) => (
        <StatCard key={stat.title} {...stat} />
      ))}
    </div>
  );
}