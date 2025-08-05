'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, 
  Zap, 
  Server, 
  Globe, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  TrendingUp,
  Clock,
  Database,
  Cloud
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface PerformanceMetrics {
  avg_load_time: number;
  cache_hit_rate: number;
  error_rate: number;
  uptime: number;
}

interface SystemHealth {
  status: string;
  services: Record<string, string>;
}

interface PerformanceData {
  metrics: PerformanceMetrics;
  system_health: SystemHealth;
  uptime: number;
  alerts: any[];
  time_range: {
    hours: number;
    start_time: string;
    end_time: string;
  };
  last_updated: string;
}

interface PerformanceDashboardProps {
  className?: string;
}

export function PerformanceDashboard({ className }: PerformanceDashboardProps) {
  const [data, setData] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [timeRange, setTimeRange] = useState(24);

  useEffect(() => {
    fetchPerformanceData();
    
    // Set up auto-refresh every 5 minutes
    const interval = setInterval(fetchPerformanceData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchPerformanceData = async (showRefreshing = false) => {
    if (showRefreshing) setRefreshing(true);
    
    try {
      const response = await fetch(`/api/performance/metrics?hours=${timeRange}`);
      if (response.ok) {
        const performanceData = await response.json();
        setData(performanceData);
      }
    } catch (error) {
      console.error('Error fetching performance data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'unhealthy':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'default';
      case 'degraded':
        return 'secondary';
      case 'unhealthy':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const formatUptime = (uptime: number) => {
    return `${uptime.toFixed(2)}%`;
  };

  const formatLoadTime = (time: number) => {
    return `${time}ms`;
  };

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className={`space-y-6 ${className}`}>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Server className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No Performance Data</h3>
            <p className="text-muted-foreground mb-4">Unable to load performance metrics</p>
            <Button onClick={() => fetchPerformanceData()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Performance Dashboard</h2>
          <p className="text-muted-foreground">
            System performance and health monitoring
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchPerformanceData(true)}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* System Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">System Status</p>
                <div className="flex items-center mt-2">
                  {getStatusIcon(data.system_health.status)}
                  <span className="ml-2 font-semibold capitalize">
                    {data.system_health.status}
                  </span>
                </div>
              </div>
              <Activity className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Uptime</p>
                <p className="text-2xl font-bold">{formatUptime(data.uptime)}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-500" />
            </div>
            <div className="mt-2">
              <Progress value={data.uptime} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg Load Time</p>
                <p className="text-2xl font-bold">{formatLoadTime(data.metrics.avg_load_time)}</p>
              </div>
              <Clock className="h-8 w-8 text-purple-500" />
            </div>
            <div className="mt-2">
              <Badge variant={data.metrics.avg_load_time < 500 ? "default" : "secondary"}>
                {data.metrics.avg_load_time < 500 ? "Excellent" : "Good"}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Cache Hit Rate</p>
                <p className="text-2xl font-bold">{data.metrics.cache_hit_rate.toFixed(1)}%</p>
              </div>
              <Zap className="h-8 w-8 text-orange-500" />
            </div>
            <div className="mt-2">
              <Progress value={data.metrics.cache_hit_rate} className="h-2" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Metrics Chart */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Performance Trends</CardTitle>
                <CardDescription>System performance over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={[
                      { time: '00:00', load_time: 420, cache_hit: 85 },
                      { time: '04:00', load_time: 380, cache_hit: 87 },
                      { time: '08:00', load_time: 450, cache_hit: 83 },
                      { time: '12:00', load_time: 520, cache_hit: 89 },
                      { time: '16:00', load_time: 410, cache_hit: 91 },
                      { time: '20:00', load_time: 390, cache_hit: 88 },
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Area 
                        type="monotone" 
                        dataKey="load_time" 
                        stackId="1" 
                        stroke="#3b82f6" 
                        fill="#3b82f6" 
                        fillOpacity={0.6}
                        name="Load Time (ms)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Key Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>Key Metrics</CardTitle>
                <CardDescription>Current performance indicators</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Error Rate</span>
                  <div className="flex items-center">
                    <span className="text-sm font-bold">{data.metrics.error_rate}%</span>
                    <Badge variant={data.metrics.error_rate < 1 ? "default" : "destructive"} className="ml-2">
                      {data.metrics.error_rate < 1 ? "Good" : "High"}
                    </Badge>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Response Time</span>
                  <span className="text-sm font-bold">{formatLoadTime(data.metrics.avg_load_time)}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Cache Efficiency</span>
                  <span className="text-sm font-bold">{data.metrics.cache_hit_rate.toFixed(1)}%</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">System Uptime</span>
                  <span className="text-sm font-bold">{formatUptime(data.uptime)}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(data.system_health.services).map(([service, status]) => (
              <Card key={service}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {service === 'database' && <Database className="h-5 w-5" />}
                      {service === 'cdn' && <Cloud className="h-5 w-5" />}
                      {service === 'widget_api' && <Server className="h-5 w-5" />}
                      {service === 'redis' && <Zap className="h-5 w-5" />}
                      <span className="font-medium capitalize">{service.replace('_', ' ')}</span>
                    </div>
                    <Badge variant={getStatusColor(status)}>
                      {status}
                    </Badge>
                  </div>
                  <div className="mt-2 flex items-center">
                    {getStatusIcon(status)}
                    <span className="ml-2 text-sm text-muted-foreground">
                      {status === 'healthy' ? 'Operating normally' : 
                       status === 'degraded' ? 'Performance issues detected' : 
                       'Service unavailable'}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="metrics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Detailed Metrics</CardTitle>
              <CardDescription>Comprehensive performance data</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Detailed Metrics</h3>
                <p className="text-muted-foreground">Advanced metrics dashboard coming soon</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Performance Alerts</CardTitle>
              <CardDescription>Recent alerts and notifications</CardDescription>
            </CardHeader>
            <CardContent>
              {data.alerts.length === 0 ? (
                <div className="text-center py-12">
                  <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No Active Alerts</h3>
                  <p className="text-muted-foreground">All systems are operating normally</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {data.alerts.map((alert, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <AlertTriangle className="h-5 w-5 text-yellow-500" />
                        <div>
                          <p className="font-medium">{alert.message}</p>
                          <p className="text-sm text-muted-foreground">{alert.timestamp}</p>
                        </div>
                      </div>
                      <Badge variant="secondary">{alert.severity}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <div className="text-center text-sm text-muted-foreground">
        Last updated: {new Date(data.last_updated).toLocaleString()}
      </div>
    </div>
  );
}
