'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CalendarDays, TrendingUp, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useConversationTrends } from '@/lib/hooks/use-analytics';

const timeRanges = [
  { label: '7D', value: '7d', active: true },
  { label: '30D', value: '30d', active: false },
  { label: '90D', value: '90d', active: false },
  { label: 'Custom', value: 'custom', active: false },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-card border border-border rounded-lg shadow-sm p-3">
        <p className="text-sm font-medium text-foreground mb-1">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm text-muted-foreground">
            <span className="inline-block w-3 h-3 rounded-full mr-2" style={{ backgroundColor: entry.color }} />
            {entry.name}: <span className="font-medium text-foreground">{entry.value.toLocaleString()}</span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export function UsageChart() {
  const [selectedRange, setSelectedRange] = useState('7d');
  
  // Calculate date range based on selection
  const getDateRange = (range: string) => {
    const now = new Date();
    const startDate = new Date();
    
    switch (range) {
      case '7d':
        startDate.setDate(now.getDate() - 7);
        break;
      case '30d':
        startDate.setDate(now.getDate() - 30);
        break;
      case '90d':
        startDate.setDate(now.getDate() - 90);
        break;
      default:
        startDate.setDate(now.getDate() - 7);
    }
    
    return {
      startDate: startDate.toISOString().split('T')[0],
      endDate: now.toISOString().split('T')[0]
    };
  };

  const { startDate, endDate } = getDateRange(selectedRange);
  const { data: trendsData, isLoading, error } = useConversationTrends(startDate, endDate);

  // Transform data for chart
  const chartData = trendsData?.map(trend => ({
    date: new Date(trend.date).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    }),
    conversations: trend.conversations,
    messages: trend.messages || 0,
  })) || [];

  return (
    <Card className="shadow-sm">
      <CardHeader className="space-y-0 pb-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg font-semibold text-foreground">
              Usage Analytics
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Track conversations and messages over time
            </p>
          </div>
          <div className="flex items-center space-x-1">
            {timeRanges.map((range) => (
              <Button
                key={range.value}
                variant={selectedRange === range.value ? "default" : "ghost"}
                size="sm"
                className={cn(
                  "h-8 px-3 text-sm",
                  selectedRange === range.value 
                    ? "bg-primary text-primary-foreground" 
                    : "text-muted-foreground hover:text-foreground"
                )}
                onClick={() => setSelectedRange(range.value)}
              >
                {range.label}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="h-[320px] w-full flex items-center justify-center">
            <div className="space-y-4 text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto" />
              <p className="text-muted-foreground">Loading analytics data...</p>
            </div>
          </div>
        ) : error ? (
          <div className="h-[320px] w-full flex items-center justify-center">
            <div className="space-y-4 text-center">
              <p className="text-destructive">Failed to load analytics data</p>
              <Button onClick={() => window.location.reload()} variant="outline" size="sm">
                Try Again
              </Button>
            </div>
          </div>
        ) : chartData.length === 0 ? (
          <div className="h-[320px] w-full flex items-center justify-center">
            <p className="text-muted-foreground">No data available for selected period</p>
          </div>
        ) : (
          <div className="h-[320px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart 
                data={chartData}
                margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
              >
              <defs>
                <linearGradient id="conversationsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--chart-1))" stopOpacity={0.1}/>
                  <stop offset="95%" stopColor="hsl(var(--chart-1))" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="messagesGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--chart-2))" stopOpacity={0.1}/>
                  <stop offset="95%" stopColor="hsl(var(--chart-2))" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="hsl(var(--border))" 
                strokeOpacity={0.5}
              />
              <XAxis 
                dataKey="date" 
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis 
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => value.toLocaleString()}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />
              <Line 
                type="monotone" 
                dataKey="conversations" 
                stroke="hsl(var(--chart-1))" 
                strokeWidth={2}
                name="Conversations"
                dot={{ fill: "hsl(var(--chart-1))", strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: "hsl(var(--chart-1))", strokeWidth: 2 }}
                fill="url(#conversationsGradient)"
              />
              <Line 
                type="monotone" 
                dataKey="messages" 
                stroke="hsl(var(--chart-2))" 
                strokeWidth={2}
                name="Messages"
                dot={{ fill: "hsl(var(--chart-2))", strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: "hsl(var(--chart-2))", strokeWidth: 2 }}
                fill="url(#messagesGradient)"
              />
            </LineChart>
          </ResponsiveContainer>
          </div>
        )}
        
        {/* Summary Stats - only show when we have data */}
        {!isLoading && !error && chartData.length > 0 && (
          <div className="flex items-center justify-between pt-4 border-t border-border mt-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-4 w-4 text-success" />
                <span className="text-sm text-muted-foreground">
                  <span className="font-medium text-success">+12%</span> vs last period
                </span>
              </div>
            </div>
            <div className="text-xs text-muted-foreground flex items-center space-x-1">
              <CalendarDays className="h-3 w-3" />
              <span>Last updated: 2 hours ago</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}