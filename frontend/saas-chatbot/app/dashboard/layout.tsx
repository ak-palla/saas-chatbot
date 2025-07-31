import { Sidebar, MobileSidebar } from "@/components/dashboard/sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>
      
      {/* Mobile Sidebar */}
      <MobileSidebar />
      
      {/* Main Content */}
      <div className="flex-1 lg:ml-0">
        <main className="flex-1 overflow-y-auto p-6 pt-16 lg:pt-6">
          {children}
        </main>
      </div>
    </div>
  );
}