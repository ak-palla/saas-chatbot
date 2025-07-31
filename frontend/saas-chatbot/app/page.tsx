import { AuthButton } from "@/components/auth-button";
import { ThemeSwitcher } from "@/components/theme-switcher";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { MessageCircle, Mic, Zap, Users, BarChart3, Shield } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Navigation */}
      <nav className="w-full flex justify-center border-b border-b-foreground/10 h-16">
        <div className="w-full max-w-7xl flex justify-between items-center px-6">
          <div className="flex items-center font-bold text-xl">
            <MessageCircle className="mr-2 h-6 w-6" />
            ChatBot SaaS
          </div>
          <div className="flex items-center gap-4">
            <AuthButton />
            <ThemeSwitcher />
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Embed AI Chatbots
            <span className="text-blue-600"> Anywhere</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Create powerful text and voice chatbots with RAG capabilities. 
            Embed them on your website in minutes and provide 24/7 customer support.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link href="/auth/sign-up">
              <Button size="lg" className="px-8">
                Get Started Free
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="lg" className="px-8">
                View Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-muted/50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Everything you need to build intelligent chatbots
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <MessageCircle className="h-10 w-10 text-blue-600 mb-2" />
                <CardTitle>Text Chatbots</CardTitle>
                <CardDescription>
                  RAG-enabled conversational AI with document understanding and tool calling
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card>
              <CardHeader>
                <Mic className="h-10 w-10 text-green-600 mb-2" />
                <CardTitle>Voice Chatbots</CardTitle>
                <CardDescription>
                  Speech-to-text and text-to-speech enabled AI with natural conversations
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card>
              <CardHeader>
                <Zap className="h-10 w-10 text-yellow-600 mb-2" />
                <CardTitle>Easy Integration</CardTitle>
                <CardDescription>
                  Embed chatbots anywhere with simple JavaScript widget integration
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card>
              <CardHeader>
                <Users className="h-10 w-10 text-purple-600 mb-2" />
                <CardTitle>Multi-tenant</CardTitle>
                <CardDescription>
                  Manage multiple chatbots for different clients and use cases
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card>
              <CardHeader>
                <BarChart3 className="h-10 w-10 text-red-600 mb-2" />
                <CardTitle>Analytics</CardTitle>
                <CardDescription>
                  Track conversations, user engagement, and chatbot performance
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card>
              <CardHeader>
                <Shield className="h-10 w-10 text-indigo-600 mb-2" />
                <CardTitle>Secure & Scalable</CardTitle>
                <CardDescription>
                  Enterprise-grade security with automatic scaling and rate limiting
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">
            Ready to get started?
          </h2>
          <p className="text-xl text-muted-foreground mb-8">
            Join thousands of businesses using our chatbot platform to improve customer experience.
          </p>
          <Link href="/auth/sign-up">
            <Button size="lg" className="px-8">
              Start Building Now
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 px-6">
        <div className="max-w-7xl mx-auto text-center text-sm text-muted-foreground">
          <p>© 2024 ChatBot SaaS. Built with Next.js and Supabase.</p>
        </div>
      </footer>
    </main>
  );
}
