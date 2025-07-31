'use client';

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AnalyticsChart } from "@/components/analytics/analytics-chart";
import { AnalyticsStats } from "@/components/analytics/analytics-stats";
import { TopChatbots } from "@/components/analytics/top-chatbots";
import { ConversationAnalytics } from "@/components/analytics/conversation-analytics";
import { DocumentAnalytics } from "@/components/analytics/document-analytics";
import { Download, Calendar } from "lucide-react";
import { analyticsService } from "@/lib/api/analytics";
import type { GlobalAnalytics } from "@/lib/api/analytics";
import { DateRangePicker } from "@/components/ui/date-range-picker";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Header } from "@/components/dashboard/header";

export default function AnalyticsPage() {
  const [period, setPeriod] = useState("week");
  const [chatbotId, setChatbotId] = useState<string>("all");
  const [analytics, setAnalytics] = useState<GlobalAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [period, chatbotId]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await analyticsService.getGlobalAnalytics(period as any, chatbotId === "all" ? undefined : chatbotId);
      setAnalytics(data);
    } catch (error) {
      console.error("Failed to load analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: "csv" | "json") => {
    try {
      const { downloadUrl } = await analyticsService.exportAnalytics(format, chatbotId === "all" ? undefined : chatbotId, period);
      window.open(downloadUrl, "_blank");
    } catch (error) {
      console.error("Failed to export analytics:", error);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading analytics...</div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <Header 
          title="Analytics" 
          description="Monitor your chatbot performance and usage metrics"
        />
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <div className="flex items-center gap-2">
            <Select value={period} onValueChange={setPeriod}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="day">Today</SelectItem>
                <SelectItem value="week">This Week</SelectItem>
                <SelectItem value="month">This Month</SelectItem>
                <SelectItem value="year">This Year</SelectItem>
              </SelectContent>
            </Select>
            <Select value={chatbotId} onValueChange={setChatbotId}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All Chatbots" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Chatbots</SelectItem>
                {analytics?.top_chatbots?.map((bot) => (
                  <SelectItem key={bot.chatbot_id} value={bot.chatbot_id}>
                    {bot.chatbot_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => handleExport("csv")}>
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
            <Button variant="outline" size="sm" onClick={() => handleExport("json")}>
              Export JSON
            </Button>
          </div>
        </div>
      </div>

      <AnalyticsStats analytics={analytics} />

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="conversations">Conversations</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Usage Trends</CardTitle>
                <CardDescription>
                  Conversations over the last {period}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <AnalyticsChart data={analytics?.monthly_usage || []} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Chatbots</CardTitle>
                <CardDescription>
                  Most active chatbots by conversations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TopChatbots chatbots={analytics?.top_chatbots || []} />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="conversations">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Conversation Analytics</CardTitle>
                <CardDescription>
                  Detailed analysis of conversation patterns and outcomes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ConversationAnalytics data={analytics?.conversation_analytics || null} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>User Engagement</CardTitle>
                <CardDescription>
                  User interaction patterns and session durations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{analytics?.avg_session_duration || 0}m</div>
                    <div className="text-sm text-muted-foreground">Avg Session Duration</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{analytics?.avg_messages_per_session || 0}</div>
                    <div className="text-sm text-muted-foreground">Avg Messages per Session</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{analytics?.response_time_avg || 0}s</div>
                    <div className="text-sm text-muted-foreground">Avg Response Time</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="documents">
          <Card>
            <CardHeader>
              <CardTitle>Document Analytics</CardTitle>
              <CardDescription>
                Document processing statistics and upload trends
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DocumentAnalytics data={analytics?.document_analytics || null} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>System Performance</CardTitle>
                <CardDescription>
                  Real-time system health and performance metrics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>API Uptime</span>
                    <span className="text-green-600 font-semibold">99.9%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Average Response Time</span>
                    <span className="text-blue-600 font-semibold">1.2s</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Error Rate</span>
                    <span className="text-red-600 font-semibold">0.1%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Cost Analysis</CardTitle>
                <CardDescription>
                  API usage costs and token consumption
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>Total Tokens Used</span>
                    <span className="font-semibold">{analytics?.total_tokens.toLocaleString() || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Estimated Cost</span>
                    <span className="font-semibold">${((analytics?.total_tokens || 0) * 0.001).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Cost per Conversation</span>
                    <span className="font-semibold">${((analytics?.total_tokens || 0) * 0.001 / (analytics?.total_conversations || 1)).toFixed(4)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}