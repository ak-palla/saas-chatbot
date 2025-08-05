'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Area, AreaChart
} from 'recharts';
import {
  Activity,
  Users,
  MessageSquare,
  Clock,
  TrendingUp,
  TrendingDown,
  Globe,
  Smartphone,
  Monitor,
  Tablet,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Zap,
  Target,
  Eye,
  MousePointer
} from 'lucide-react';

interface WidgetAnalyticsProps {
  chatbotId: string;
  dateRange?: {
    from: Date;
    to: Date;
  };
}

interface AnalyticsSummary {
  total_sessions: number;
  total_interactions: number;
  average_session_duration: number;
  bounce_rate: number;
  conversion_rate: number;
  top_pages: Array<{ page: string; sessions: number }>;
  top_countries: Array<{ country: string; sessions: number }>;
  device_breakdown: Record<string, number>;
  browser_breakdown: Record<string, number>;
}

interface PerformanceMetrics {
  average_load_time: number;
  average_first_paint: number;
  average_time_to_interactive: number;
  error_rate: number;
  uptime_percentage: number;
}

interface EngagementMetrics {
  total_widget_opens: number;
  total_messages: number;
  average_messages_per_session: number;
  user_satisfaction: number;
  goal_completion_rate: number;
}

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4'];

export function WidgetAnalytics({ chatbotId, dateRange }: WidgetAnalyticsProps) {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [engagement, setEngagement] = useState<EngagementMetrics | null>(null);
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([]);
  const [recentInteractions, setRecentInteractions] = useState<any[]>([]);

  const fetchAnalytics = async (showRefreshing = false) => {
    if (showRefreshing) setRefreshing(true);
    
    try {
      const days = dateRange 
        ? Math.ceil((dateRange.to.getTime() - dateRange.from.getTime()) / (1000 * 60 * 60 * 24))
        : 30;

      // Fetch all analytics data in parallel
      const [summaryRes, performanceRes, engagementRes, reportRes] = await Promise.all([
        fetch(`/api/widget-analytics/${chatbotId}/analytics/summary?days=${days}`),
        fetch(`/api/widget-analytics/${chatbotId}/analytics/performance?days=${days}`),
        fetch(`/api/widget-analytics/${chatbotId}/analytics/engagement?days=${days}`),
        fetch(`/api/widget-analytics/${chatbotId}/analytics/report?days=${days}`)
      ]);

      if (summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setSummary(summaryData);
      }

      if (performanceRes.ok) {
        const performanceData = await performanceRes.json();
        setPerformance(performanceData);
      }

      if (engagementRes.ok) {
        const engagementData = await engagementRes.json();
        setEngagement(engagementData);
      }

      if (reportRes.ok) {
        const reportData = await reportRes.json();
        setTimeSeriesData(reportData.time_series_data || []);
        setRecentInteractions(reportData.recent_interactions || []);
      }

    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [chatbotId, dateRange]);

  if (loading && !summary) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Widget Analytics</h2>
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const deviceData = summary ? Object.entries(summary.device_breakdown).map(([device, count]) => ({
    name: device.charAt(0).toUpperCase() + device.slice(1),
    value: count,
    percentage: (count / summary.total_sessions) * 100
  })) : [];

  const browserData = summary ? Object.entries(summary.browser_breakdown).map(([browser, count]) => ({
    name: browser,
    value: count,
    percentage: (count / summary.total_sessions) * 100
  })).slice(0, 5) : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Widget Analytics</h2>
          <p className="text-muted-foreground">
            Comprehensive insights into your widget performance
          </p>
        </div>
        <Button 
          onClick={() => fetchAnalytics(true)} 
          disabled={refreshing}
          variant="outline"
          size="sm"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Sessions</p>
                <p className="text-2xl font-bold">{formatNumber(summary?.total_sessions || 0)}</p>
              </div>
              <Users className="h-8 w-8 text-blue-500" />
            </div>
            <div className="mt-2">
              <Badge variant={summary && summary.total_sessions > 100 ? "default" : "secondary"}>
                {summary && summary.total_sessions > 100 ? "Active" : "Growing"}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Widget Opens</p>
                <p className="text-2xl font-bold">{formatNumber(engagement?.total_widget_opens || 0)}</p>
              </div>
              <Eye className="h-8 w-8 text-green-500" />
            </div>
            <div className="mt-2">
              <p className="text-sm text-muted-foreground">
                {summary ? `${summary.conversion_rate.toFixed(1)}% conversion rate` : 'No data'}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Messages</p>
                <p className="text-2xl font-bold">{formatNumber(engagement?.total_messages || 0)}</p>
              </div>
              <MessageSquare className="h-8 w-8 text-purple-500" />
            </div>
            <div className="mt-2">
              <p className="text-sm text-muted-foreground">
                {engagement ? `${engagement.average_messages_per_session.toFixed(1)} avg per session` : 'No data'}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg. Session</p>
                <p className="text-2xl font-bold">
                  {summary ? formatDuration(Math.round(summary.average_session_duration)) : '0m 0s'}
                </p>
              </div>
              <Clock className="h-8 w-8 text-orange-500" />
            </div>
            <div className="mt-2">
              <Badge variant={summary && summary.bounce_rate < 50 ? "default" : "destructive"}>
                {summary ? `${summary.bounce_rate.toFixed(1)}% bounce rate` : 'No data'}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Analytics Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="engagement">Engagement</TabsTrigger>
          <TabsTrigger value="audience">Audience</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Time Series Chart */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Activity Over Time</CardTitle>
                <CardDescription>Widget sessions, opens, and messages</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={timeSeriesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="sessions" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                    <Area type="monotone" dataKey="opens" stackId="2" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
                    <Area type="monotone" dataKey="messages" stackId="3" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.6} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Top Pages */}
            <Card>
              <CardHeader>
                <CardTitle>Top Pages</CardTitle>
                <CardDescription>Pages with most widget activity</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {summary?.top_pages.slice(0, 5).map((page, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate" title={page.page}>
                        {page.page}
                      </p>
                    </div>
                    <div className="ml-2 flex items-center space-x-2">
                      <Badge variant="secondary">{page.sessions}</Badge>
                    </div>
                  </div>
                )) || <p className="text-sm text-muted-foreground">No data available</p>}
              </CardContent>
            </Card>

            {/* Top Countries */}
            <Card>
              <CardHeader>
                <CardTitle>Top Countries</CardTitle>
                <CardDescription>Geographic distribution of users</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {summary?.top_countries.slice(0, 5).map((country, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Globe className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">{country.country}</span>
                    </div>
                    <Badge variant="secondary">{country.sessions}</Badge>
                  </div>
                )) || <p className="text-sm text-muted-foreground">No data available</p>}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Performance Metrics
                </CardTitle>
                <CardDescription>Widget loading and responsiveness</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Average Load Time</span>
                    <span className="font-medium">{performance?.average_load_time.toFixed(0)}ms</span>
                  </div>
                  <Progress 
                    value={Math.min((performance?.average_load_time || 0) / 50, 100)} 
                    className="h-2"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>First Paint</span>
                    <span className="font-medium">{performance?.average_first_paint.toFixed(0)}ms</span>
                  </div>
                  <Progress 
                    value={Math.min((performance?.average_first_paint || 0) / 30, 100)} 
                    className="h-2"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Time to Interactive</span>
                    <span className="font-medium">{performance?.average_time_to_interactive.toFixed(0)}ms</span>
                  </div>
                  <Progress 
                    value={Math.min((performance?.average_time_to_interactive || 0) / 100, 100)} 
                    className="h-2"
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <span className="text-sm">Uptime</span>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="font-medium">{performance?.uptime_percentage.toFixed(1)}%</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm">Error Rate</span>
                  <div className="flex items-center space-x-2">
                    {(performance?.error_rate || 0) > 5 ? (
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                    ) : (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    )}
                    <span className="font-medium">{performance?.error_rate.toFixed(1)}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Performance Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle>Performance Insights</CardTitle>
                <CardDescription>Optimization recommendations</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {performance && performance.average_load_time > 3000 && (
                  <div className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-800">Slow Load Time</p>
                      <p className="text-xs text-red-600">Consider optimizing widget assets and enabling CDN</p>
                    </div>
                  </div>
                )}

                {performance && performance.error_rate > 5 && (
                  <div className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-800">High Error Rate</p>
                      <p className="text-xs text-red-600">Check deployment configurations and domain settings</p>
                    </div>
                  </div>
                )}

                {performance && performance.average_load_time <= 1500 && performance.error_rate <= 2 && (
                  <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-green-800">Great Performance</p>
                      <p className="text-xs text-green-600">Your widget is loading quickly and reliably</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="engagement" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Engagement Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Engagement Overview
                </CardTitle>
                <CardDescription>How users interact with your widget</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">{engagement?.total_widget_opens || 0}</p>
                    <p className="text-xs text-blue-600">Widget Opens</p>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">{engagement?.total_messages || 0}</p>
                    <p className="text-xs text-green-600">Total Messages</p>
                  </div>
                </div>

                <Separator />

                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm">Messages per Session</span>
                    <span className="font-medium">{engagement?.average_messages_per_session.toFixed(1) || 0}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm">User Satisfaction</span>
                    <div className="flex items-center space-x-1">
                      {[...Array(5)].map((_, i) => (
                        <div
                          key={i}
                          className={`w-2 h-2 rounded-full ${
                            i < Math.round(engagement?.user_satisfaction || 0) 
                              ? 'bg-yellow-400' 
                              : 'bg-gray-200'
                          }`}
                        />
                      ))}
                      <span className="ml-2 text-sm font-medium">
                        {engagement?.user_satisfaction.toFixed(1) || 0}/5
                      </span>
                    </div>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-sm">Goal Completion</span>
                    <span className="font-medium">{engagement?.goal_completion_rate.toFixed(1) || 0}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Interactions */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest widget interactions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 max-h-[400px] overflow-y-auto">
                {recentInteractions.slice(0, 10).map((interaction, index) => (
                  <div key={index} className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded">
                    <div className="flex-shrink-0">
                      {interaction.interaction_type === 'message_sent' && <MessageSquare className="h-4 w-4 text-blue-500" />}
                      {interaction.interaction_type === 'open' && <Eye className="h-4 w-4 text-green-500" />}
                      {interaction.interaction_type === 'close' && <MousePointer className="h-4 w-4 text-gray-500" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">
                        {interaction.interaction_type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                      </p>
                      <p className="text-xs text-muted-foreground truncate">
                        {interaction.page_url || 'Unknown page'}
                      </p>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(interaction.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                )) || <p className="text-sm text-muted-foreground">No recent activity</p>}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="audience" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Device Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Device Types</CardTitle>
                <CardDescription>How users access your widget</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={deviceData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {deviceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-2">
                  {deviceData.map((device, index) => (
                    <div key={device.name} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {device.name === 'Desktop' && <Monitor className="h-4 w-4" />}
                        {device.name === 'Mobile' && <Smartphone className="h-4 w-4" />}
                        {device.name === 'Tablet' && <Tablet className="h-4 w-4" />}
                        <span className="text-sm">{device.name}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <span className="text-sm font-medium">{device.percentage.toFixed(1)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Browser Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Top Browsers</CardTitle>
                <CardDescription>Browser usage statistics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {browserData.map((browser, index) => (
                  <div key={browser.name} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>{browser.name}</span>
                      <span className="font-medium">{browser.percentage.toFixed(1)}%</span>
                    </div>
                    <Progress value={browser.percentage} className="h-2" />
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}