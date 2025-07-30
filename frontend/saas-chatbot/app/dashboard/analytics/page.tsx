'use client';

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AnalyticsChart } from "@/components/analytics/analytics-chart";
import { AnalyticsStats } from "@/components/analytics/analytics-stats";
import { TopChatbots } from "@/components/analytics/top-chatbots";
import { Download } from "lucide-react";
import { analyticsService } from "@/lib/api/analytics";
import type { GlobalAnalytics } from "@/lib/api/analytics";

export default function AnalyticsPage() {
  const [period, setPeriod] = useState("week");
  const [analytics, setAnalytics] = useState<GlobalAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [period]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await analyticsService.getGlobalAnalytics(period as any);
      setAnalytics(data);
    } catch (error) {
      console.error("Failed to load analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: "csv" | "json") => {
    try {
      const { downloadUrl } = await analyticsService.exportAnalytics(format, undefined, period);
      window.open(downloadUrl, "_blank");
    } catch (error) {
      console.error("Failed to export analytics:", error);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading analytics...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Monitor your chatbot performance and usage metrics
          </p>
        </div>
        <div className="flex items-center space-x-2">
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
          <Button variant="outline" onClick={() => handleExport("csv")}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>

      <AnalyticsStats analytics={analytics} />

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
    </div>
  );
}