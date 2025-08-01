'use client';

import { useEffect } from 'react';
import { DashboardStats } from "@/components/dashboard/dashboard-stats";
import { RecentChatbots } from "@/components/dashboard/recent-chatbots";
import { UsageChart } from "@/components/dashboard/usage-chart";
import { Header } from "@/components/dashboard/header";
import { QuickActions } from "@/components/dashboard/quick-actions";
import { DebugUser } from "@/components/debug-user";
import { OnboardingTour } from "@/components/onboarding/onboarding-tour";
import { useOnboarding } from "@/lib/hooks/use-onboarding";

export default function DashboardPage() {
  const { 
    isOnboardingOpen, 
    hasCompletedOnboarding, 
    startOnboarding, 
    completeOnboarding, 
    closeOnboarding 
  } = useOnboarding();

  useEffect(() => {
    // Auto-start onboarding for new users after a short delay
    if (!hasCompletedOnboarding) {
      const timer = setTimeout(() => {
        startOnboarding();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [hasCompletedOnboarding, startOnboarding]);

  return (
    <div className="space-y-8">
      <DebugUser />
      <Header 
        title="Dashboard" 
        description="Welcome back! Here's what's happening with your chatbots." 
        onStartOnboarding={startOnboarding}
      />

      <div className="space-y-6">
        <DashboardStats />
      </div>

      <QuickActions />

      <div className="grid lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <UsageChart />
        </div>
        <div className="space-y-6">
          <RecentChatbots />
        </div>
      </div>

      <OnboardingTour
        isOpen={isOnboardingOpen}
        onClose={closeOnboarding}
        onComplete={completeOnboarding}
      />
    </div>
  );
}