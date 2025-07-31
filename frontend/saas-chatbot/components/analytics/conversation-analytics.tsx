'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import type { ConversationAnalytics } from "@/lib/api/analytics";

interface ConversationAnalyticsProps {
  data: ConversationAnalytics | null;
}

export function ConversationAnalytics({ data }: ConversationAnalyticsProps) {
  if (!data) return null;

  const statusData = [
    { name: 'Completed', value: data.completed_conversations, color: '#10b981' },
    { name: 'Failed', value: data.failed_conversations, color: '#ef4444' },
    { name: 'In Progress', value: data.in_progress_conversations, color: '#f59e0b' },
  ];

  const hourlyData = data.hourly_distribution.map(hour => ({
    hour: `${hour.hour}:00`,
    conversations: hour.count,
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Conversation Status</CardTitle>
          <div className="text-sm text-muted-foreground">
            Distribution of conversation outcomes
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Hourly Activity</CardTitle>
          <div className="text-sm text-muted-foreground">
            Conversations by hour of day
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hourlyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value: number) => [value.toLocaleString(), 'Conversations']} />
                <Bar dataKey="conversations" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}