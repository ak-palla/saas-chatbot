'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const mockData = [
  { date: 'Jan 1', conversations: 45, messages: 120 },
  { date: 'Jan 2', conversations: 52, messages: 145 },
  { date: 'Jan 3', conversations: 38, messages: 98 },
  { date: 'Jan 4', conversations: 65, messages: 189 },
  { date: 'Jan 5', conversations: 78, messages: 234 },
  { date: 'Jan 6', conversations: 92, messages: 267 },
  { date: 'Jan 7', conversations: 87, messages: 245 },
];

export function UsageChart() {
  const [data, setData] = useState(mockData);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Usage Overview</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="conversations" 
                stroke="#3b82f6" 
                strokeWidth={2}
                name="Conversations"
              />
              <Line 
                type="monotone" 
                dataKey="messages" 
                stroke="#8b5cf6" 
                strokeWidth={2}
                name="Messages"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}