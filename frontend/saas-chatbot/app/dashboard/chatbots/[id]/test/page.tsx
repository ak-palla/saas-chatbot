'use client';

import { useState, useEffect, useRef } from "react";
import { useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Mic, MicOff, Send, RotateCcw, Bot, User, Volume2, VolumeX, Loader2 } from "lucide-react";
import { useChatbot } from "@/lib/hooks/use-chatbots";
import { conversationService } from "@/lib/api/conversations";
import { useVoiceChat } from "@/lib/hooks/use-websocket";
import { VoiceRecordingButton } from "@/components/voice/voice-recording-button";
import type { Chatbot } from "@/lib/api/chatbots";
import type { Message, ChatRequest } from "@/lib/api/conversations";
import { useToast } from "@/components/ui/use-toast";

export default function ChatbotTestPage() {
  const params = useParams();
  const chatbotId = params.id as string;
  
  // Use hooks for data fetching
  const { data: chatbot, isLoading: chatbotLoading, error: chatbotError } = useChatbot(chatbotId);
  const { 
    session: voiceSession, 
    isRecording, 
    isProcessing: voiceProcessing,
    error: voiceError,
    isConnected: voiceConnected,
    audioLevel,
    recordingDuration,
    audioSupported,
    connect: connectVoice,
    disconnect: disconnectVoice,
    startRecording,
    stopRecording,
    sendTextInput
  } = useVoiceChat(chatbotId, { autoConnect: false });
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (chatbot) {
      startNewConversation();
    }
  }, [chatbot]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle voice WebSocket errors
  useEffect(() => {
    if (voiceError) {
      toast({
        title: "Voice Connection Error",
        description: voiceError,
        variant: "destructive",
      });
    }
  }, [voiceError, toast]);

  const startNewConversation = async () => {
    try {
      const conversation = await conversationService.createConversation({
        chatbot_id: chatbotId,
        session_id: `test-${Date.now()}`,
      });
      setCurrentConversationId(conversation.id);
      setMessages([]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start new conversation",
        variant: "destructive",
      });
    }
  };

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !chatbotId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: "user",
      type: "text",
      timestamp: new Date().toISOString(),
      conversation_id: currentConversationId || '',
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageText = inputMessage;
    setInputMessage("");
    setIsLoading(true);

    try {
      const request: ChatRequest = {
        message: messageText,
        chatbot_id: chatbotId,
        conversation_id: currentConversationId || undefined,
      };

      const response = await conversationService.sendMessage(request);

      const botMessage: Message = {
        id: Date.now().toString() + "_bot",
        content: response.message,
        role: "assistant",
        type: "text",
        timestamp: new Date().toISOString(),
        conversation_id: response.conversation_id,
        metadata: response.metadata,
      };

      setMessages((prev) => [...prev, botMessage]);
      
      // Update conversation ID if it was created
      if (!currentConversationId && response.conversation_id) {
        setCurrentConversationId(response.conversation_id);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send message",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceToggle = async () => {
    if (!isVoiceEnabled) {
      // Enable voice - connect to voice WebSocket
      setIsVoiceEnabled(true);
      try {
        await connectVoice();
        toast({
          title: "Voice Enabled",
          description: "Voice features are now active",
        });
      } catch (error) {
        setIsVoiceEnabled(false);
        toast({
          title: "Voice Connection Failed",
          description: "Could not connect to voice service",
          variant: "destructive",
        });
      }
    } else {
      // Disable voice - disconnect
      setIsVoiceEnabled(false);
      disconnectVoice();
      toast({
        title: "Voice Disabled",
        description: "Voice features disabled",
      });
    }
  };

  const handleVoiceRecording = async () => {
    if (!audioSupported) {
      toast({
        title: "Audio Not Supported",
        description: "Your browser doesn't support audio recording",
        variant: "destructive",
      });
      return;
    }

    if (!voiceConnected) {
      toast({
        title: "Voice Not Connected",
        description: "Please enable voice first",
        variant: "destructive",
      });
      return;
    }

    try {
      if (isRecording) {
        stopRecording();
      } else {
        await startRecording();
      }
    } catch (error) {
      toast({
        title: "Recording Error",
        description: error instanceof Error ? error.message : "Failed to start recording",
        variant: "destructive",
      });
    }
  };

  const handleReset = () => {
    startNewConversation();
    toast({
      title: "Conversation Reset",
      description: "Started a new conversation",
    });
  };

  // Loading state
  if (chatbotLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="space-y-4 text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto" />
          <p className="text-muted-foreground">Loading chatbot configuration...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (chatbotError || !chatbot) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="space-y-4 text-center">
          <p className="text-destructive">Failed to load chatbot</p>
          <Button onClick={() => window.location.reload()}>Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Test Chatbot</h1>
          <p className="text-muted-foreground">
            Interact with your chatbot "{chatbot.name}" in real-time
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={handleReset}>
            <RotateCcw className="mr-2 h-4 w-4" />
            Reset Conversation
          </Button>
          <Button
            variant={isVoiceEnabled ? "default" : "outline"}
            onClick={handleVoiceToggle}
          >
            {isVoiceEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card className="h-[600px]">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Live Chat</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Real-time conversation with your chatbot
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline">GPT-4</Badge>
                  {voiceConnected && <Badge variant="outline">Voice Connected</Badge>}
                  {isVoiceEnabled && <Badge variant="outline" className="bg-green-100">Voice Active</Badge>}
                </div>
              </div>
            </CardHeader>
            <CardContent className="h-[500px] flex flex-col">
              <ScrollArea className="flex-1 pr-4" ref={scrollRef}>
                <div className="space-y-4">
                  {messages.length === 0 && (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-center">
                        <Bot className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                        <p className="text-muted-foreground">Start a conversation with your chatbot</p>
                      </div>
                    </div>
                  )}
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[70%] rounded-lg px-4 py-2 ${
                          message.role === "user"
                            ? "bg-primary text-primary-foreground"
                            : "bg-secondary"
                        }`}
                      >
                        <div className="flex items-center space-x-2 mb-1">
                          {message.role === "user" ? (
                            <User className="h-4 w-4" />
                          ) : (
                            <Bot className="h-4 w-4" />
                          )}
                          <span className="text-xs font-medium">
                            {message.role === "user" ? "You" : chatbot.name}
                          </span>
                        </div>
                        <p className="text-sm">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-secondary rounded-lg px-4 py-2">
                        <div className="flex items-center space-x-2">
                          <Bot className="h-4 w-4" />
                          <span className="text-sm">{chatbot.name} is typing...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>
              <Separator className="my-4" />
              <div className="flex items-center space-x-2">
                <Input
                  placeholder="Type your message..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  disabled={isLoading}
                />
                {isVoiceEnabled && (
                  <VoiceRecordingButton
                    isRecording={isRecording}
                    isProcessing={voiceProcessing}
                    audioLevel={audioLevel}
                    duration={recordingDuration}
                    isDisabled={!voiceConnected}
                    onStartRecording={() => handleVoiceRecording()}
                    onStopRecording={() => handleVoiceRecording()}
                  />
                )}
                <Button onClick={handleSendMessage} disabled={isLoading || !inputMessage.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Chatbot Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div>
                <span className="text-sm font-medium">Name:</span>
                <p className="text-sm text-muted-foreground">{chatbot.name}</p>
              </div>
              <div>
                <span className="text-sm font-medium">Status:</span>
                <p className="text-sm text-muted-foreground">
                  {chatbot.is_active ? 'Active' : 'Inactive'}
                </p>
              </div>
              <div>
                <span className="text-sm font-medium">System Prompt:</span>
                <p className="text-sm text-muted-foreground truncate">
                  {chatbot.system_prompt || 'No system prompt configured'}
                </p>
              </div>
              <div>
                <span className="text-sm font-medium">Voice Status:</span>
                <p className="text-sm text-muted-foreground">
                  {voiceConnected ? 'Connected' : 'Disconnected'}
                </p>
              </div>
              <div>
                <span className="text-sm font-medium">Audio Support:</span>
                <p className="text-sm text-muted-foreground">
                  {audioSupported ? 'Supported' : 'Not supported'}
                </p>
              </div>
              {isRecording && (
                <div>
                  <span className="text-sm font-medium">Recording:</span>
                  <p className="text-sm text-muted-foreground">
                    {Math.floor(recordingDuration / 60)}:{(recordingDuration % 60).toString().padStart(2, '0')} 
                    {audioLevel > 0 && ` • ${Math.round(audioLevel)}% level`}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Testing Features</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Available Actions</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Send text messages</li>
                  <li>• Test system prompt responses</li>
                  {isVoiceEnabled && (
                    <>
                      <li>• Voice input with real-time recording</li>
                      <li>• Audio level monitoring during recording</li>
                      <li>• Text-to-speech output</li>
                      <li>• Speech-to-text processing</li>
                    </>
                  )}
                  <li>• Real-time conversation flow</li>
                  <li>• Reset conversation anytime</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Testing Tips</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Try different question types</li>
                  <li>• Test with uploaded documents</li>
                  <li>• Check response quality</li>
                  <li>• Verify tool integrations</li>
                  {isVoiceEnabled && (
                    <>
                      <li>• Speak clearly and avoid background noise</li>
                      <li>• Test in a quiet environment for best results</li>
                      <li>• Monitor audio levels while recording</li>
                    </>
                  )}
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}