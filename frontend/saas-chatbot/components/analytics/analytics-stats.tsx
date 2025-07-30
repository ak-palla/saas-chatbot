import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";
import type { GlobalAnalytics } from "@/lib/api/analytics";

interface AnalyticsStatsProps {
  analytics: GlobalAnalytics | null;
}

export function AnalyticsStats({ analytics }: AnalyticsStatsProps) {
  if (!analytics) return null;

  const stats = [
    {
      title: "Total Conversations",
      value: analytics.total_conversations.toLocaleString(),
      change: "+12.5%",
      isPositive: true,
    },
    {
      title: "Total Messages",
      value: analytics.total_messages.toLocaleString(),
      change: "+8.2%",
      isPositive: true,
    },
    {
      title: "Total Tokens",
      value: analytics.total_tokens.toLocaleString(),
      change: "+15.3%",
      isPositive: true,
    },
    {
      title: "Active Chatbots",
      value: analytics.total_chatbots.toString(),
      change: "+2",
      isPositive: true,
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
            {stat.isPositive ? (
              <TrendingUp className="h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stat.value}</div>
            <p className="text-xs text-muted-foreground">
              {stat.change} from last period
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}