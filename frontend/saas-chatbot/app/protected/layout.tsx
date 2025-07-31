import { AuthButton } from "@/components/auth-button";
import { ThemeSwitcher } from "@/components/theme-switcher";
import Link from "next/link";
import { MessageCircle } from "lucide-react";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="min-h-screen">
      <nav className="w-full flex justify-center border-b border-b-foreground/10 h-16">
        <div className="w-full max-w-7xl flex justify-between items-center px-6">
          <Link href="/" className="flex items-center font-bold text-xl">
            <MessageCircle className="mr-2 h-6 w-6" />
            ChatBot SaaS
          </Link>
          <div className="flex items-center gap-4">
            <AuthButton />
            <ThemeSwitcher />
          </div>
        </div>
      </nav>
      
      <div className="w-full">
        {children}
      </div>
    </main>
  );
}
