import { DashboardStats } from "@/components/dashboard/dashboard-stats";
import { RecentChatbots } from "@/components/dashboard/recent-chatbots";
import { QuickActions } from "@/components/dashboard/quick-actions";
import { UsageChart } from "@/components/dashboard/usage-chart";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here's what's happening with your chatbots.
          </p>
        </div>
      </div>

      <DashboardStats />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <UsageChart />
        </div>
        <QuickActions />
      </div>

      <RecentChatbots />
    </div>
  );
}