'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft, Bot, Mic, Save, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';

export default function CreateChatbotPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [chatbot, setChatbot] = useState({
    name: '',
    type: 'text',
    description: '',
    prompt: '',
    voice: {
      provider: 'deepgram',
      voiceId: 'en-US-AriaNeural',
      speed: 1.0,
      pitch: 1.0,
    },
    appearance: {
      theme: 'light',
      primaryColor: '#3b82f6',
      position: 'bottom-right',
    },
    behavior: {
      greeting: 'Hello! How can I help you today?',
      fallback: 'I\'m sorry, I don\'t understand that. Could you please rephrase?',
      enableVoice: false,
    },
  });

  const handleNext = () => {
    if (step < 3) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSave = () => {
    // Save chatbot logic here
    router.push('/dashboard/chatbots');
  };

  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
              <CardDescription>
                Set up the basic details for your new chatbot
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Chatbot Name</Label>
                <Input
                  id="name"
                  placeholder="My Customer Support Bot"
                  value={chatbot.name}
                  onChange={(e) => setChatbot({ ...chatbot, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="type">Chatbot Type</Label>
                <Select
                  value={chatbot.type}
                  onValueChange={(value) => setChatbot({ ...chatbot, type: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="text">
                      <div className="flex items-center">
                        <Bot className="w-4 h-4 mr-2" />
                        Text Chatbot
                      </div>
                    </SelectItem>
                    <SelectItem value="voice">
                      <div className="flex items-center">
                        <Mic className="w-4 h-4 mr-2" />
                        Voice Chatbot
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe what this chatbot will do..."
                  value={chatbot.description}
                  onChange={(e) => setChatbot({ ...chatbot, description: e.target.value })}
                />
              </div>
            </CardContent>
          </Card>
        );
      case 2:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Configuration</CardTitle>
              <CardDescription>
                Configure your chatbot's behavior and responses
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="prompt">System Prompt</Label>
                <Textarea
                  id="prompt"
                  placeholder="You are a helpful assistant..."
                  value={chatbot.prompt}
                  onChange={(e) => setChatbot({ ...chatbot, prompt: e.target.value })}
                  rows={4}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="greeting">Welcome Message</Label>
                <Input
                  id="greeting"
                  placeholder="Hello! How can I help you today?"
                  value={chatbot.behavior.greeting}
                  onChange={(e) => setChatbot({
                    ...chatbot,
                    behavior: { ...chatbot.behavior, greeting: e.target.value },
                  })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="fallback">Fallback Response</Label>
                <Input
                  id="fallback"
                  placeholder="I don't understand..."
                  value={chatbot.behavior.fallback}
                  onChange={(e) => setChatbot({
                    ...chatbot,
                    behavior: { ...chatbot.behavior, fallback: e.target.value },
                  })}
                />
              </div>
              {chatbot.type === 'voice' && (
                <div className="space-y-4 border-t pt-4">
                  <Label>Voice Settings</Label>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Voice</Label>
                      <Select
                        value={chatbot.voice.voiceId}
                        onValueChange={(value) => setChatbot({
                          ...chatbot,
                          voice: { ...chatbot.voice, voiceId: value },
                        })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="en-US-AriaNeural">Aria (US)</SelectItem>
                          <SelectItem value="en-US-JennyNeural">Jenny (US)</SelectItem>
                          <SelectItem value="en-GB-SoniaNeural">Sonia (UK)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Speed</Label>
                      <Input
                        type="number"
                        min="0.5"
                        max="2"
                        step="0.1"
                        value={chatbot.voice.speed}
                        onChange={(e) => setChatbot({
                          ...chatbot,
                          voice: { ...chatbot.voice, speed: parseFloat(e.target.value) },
                        })}
                      />
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        );
      case 3:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Appearance & Widget</CardTitle>
              <CardDescription>
                Customize how your chatbot looks and behaves
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Primary Color</Label>
                <div className="flex items-center space-x-2">
                  <Input
                    type="color"
                    className="w-20 h-10"
                    value={chatbot.appearance.primaryColor}
                    onChange={(e) => setChatbot({
                      ...chatbot,
                      appearance: { ...chatbot.appearance, primaryColor: e.target.value },
                    })}
                  />
                  <Input
                    type="text"
                    value={chatbot.appearance.primaryColor}
                    onChange={(e) => setChatbot({
                      ...chatbot,
                      appearance: { ...chatbot.appearance, primaryColor: e.target.value },
                    })}
                  />
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Widget Position</Label>
                  <Select
                    value={chatbot.appearance.position}
                    onValueChange={(value) => setChatbot({
                      ...chatbot,
                      appearance: { ...chatbot.appearance, position: value },
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="bottom-right">Bottom Right</SelectItem>
                      <SelectItem value="bottom-left">Bottom Left</SelectItem>
                      <SelectItem value="top-right">Top Right</SelectItem>
                      <SelectItem value="top-left">Top Left</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Theme</Label>
                  <Select
                    value={chatbot.appearance.theme}
                    onValueChange={(value) => setChatbot({
                      ...chatbot,
                      appearance: { ...chatbot.appearance, theme: value },
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="auto">Auto</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => router.back()}>
            <ChevronLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Create New Chatbot</h1>
            <p className="text-muted-foreground">
              Set up your AI chatbot in a few simple steps
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-center mb-8">
        <div className="flex items-center space-x-4"
          <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
            step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
          }`}>
            1
          </div>
          <Separator className="w-20" />
          <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
            step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
          }`}>
            2
          </div>
          <Separator className="w-20" />
          <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
            step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
          }`}>
            3
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto">
        {renderStepContent()}
        
        <div className="flex justify-between mt-8">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={step === 1}
          >
            Previous
          </Button>
          <div className="space-x-4">
            {step < 3 ? (
              <Button onClick={handleNext}>Next</Button>
            ) : (
              <Button onClick={handleSave}>
                <Save className="w-4 h-4 mr-2" />
                Create Chatbot
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}