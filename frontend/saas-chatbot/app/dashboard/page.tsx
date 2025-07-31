import { DashboardStats } from "@/components/dashboard/dashboard-stats";
import { RecentChatbots } from "@/components/dashboard/recent-chatbots";
import { UsageChart } from "@/components/dashboard/usage-chart";
import { Header } from "@/components/dashboard/header";
import { DebugUser } from "@/components/debug-user";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <DebugUser />
      <Header 
        title="Dashboard" 
        description="Welcome back! Here's what's happening with your chatbots." 
      />

      <div className="space-y-1">
        <DashboardStats />
      </div>

      <div className="space-y-6">
        <UsageChart />
      </div>

      <div className="pt-2">
        <RecentChatbots />
      </div>
    </div>
  );
}