'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import { FileText, CheckCircle, Clock, AlertCircle } from "lucide-react";
import type { DocumentAnalytics } from "@/lib/api/analytics";

interface DocumentAnalyticsProps {
  data: DocumentAnalytics | null;
}

export function DocumentAnalytics({ data }: DocumentAnalyticsProps) {
  if (!data) return null;

  const statusData = [
    { name: 'Processed', value: data.processed_documents, icon: CheckCircle, color: '#10b981' },
    { name: 'Processing', value: data.processing_documents, icon: Clock, color: '#f59e0b' },
    { name: 'Failed', value: data.failed_documents, icon: AlertCircle, color: '#ef4444' },
    { name: 'Pending', value: data.pending_documents, icon: FileText, color: '#6b7280' },
  ];

  const uploadTrendData = data.upload_trend.map(item => ({
    date: new Date(item.date).toLocaleDateString(),
    uploads: item.count,
  }));

  return (
    <div className="grid gap-6">
      <div className="grid gap-4 md:grid-cols-4">
        {statusData.map((status) => (
          <Card key={status.name}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{status.name}</CardTitle>
              <status.icon className="h-4 w-4" style={{ color: status.color }} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" style={{ color: status.color }}>{status.value.toLocaleString()}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Upload Trends</CardTitle>
            <div className="text-sm text-muted-foreground">
              Documents uploaded over time
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={uploadTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(value: number) => [value.toLocaleString(), 'Documents']} />
                  <Line type="monotone" dataKey="uploads" stroke="#8b5cf6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Document Types</CardTitle>
            <div className="text-sm text-muted-foreground">
              Distribution by file type
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.file_type_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="file_type" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(value: number) => [value.toLocaleString(), 'Documents']} />
                  <Bar dataKey="count" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}