'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageSquare, Send, Bot, User, RotateCcw, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { apiService, TestChatMessage } from '@/lib/api';

interface ChatbotTestProps {
  chatbot: any;
}

interface Message {
  id: string;
  role: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

export function ChatbotTest({ chatbot }: ChatbotTestProps) {
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'bot',
      content: chatbot?.appearance_config?.greetingMessage || 'Hello! How can I help you today?',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);

  useEffect(() => {
    // Scroll to bottom when new messages are added
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  useEffect(() => {
    // Initialize voice functionality based on chatbot settings
    console.log('🔍 VOICE DEBUG: ==================== CHATBOT ANALYSIS ====================');
    console.log('🔍 VOICE DEBUG: Checking chatbot voice settings...');
    console.log('🔍 VOICE DEBUG: Full chatbot object:', JSON.stringify(chatbot, null, 2));
    console.log('🔍 VOICE DEBUG: chatbot exists:', !!chatbot);
    console.log('🔍 VOICE DEBUG: chatbot.id:', chatbot?.id);
    console.log('🔍 VOICE DEBUG: behavior_config exists:', !!chatbot?.behavior_config);
    console.log('🔍 VOICE DEBUG: behavior_config type:', typeof chatbot?.behavior_config);
    console.log('🔍 VOICE DEBUG: behavior_config content:', JSON.stringify(chatbot?.behavior_config, null, 2));
    console.log('🔍 VOICE DEBUG: enableVoice value:', chatbot?.behavior_config?.enableVoice);
    console.log('🔍 VOICE DEBUG: enableVoice type:', typeof chatbot?.behavior_config?.enableVoice);
    console.log('🔍 VOICE DEBUG: ===================================================');
    
    const isVoiceEnabled = chatbot?.behavior_config?.enableVoice || false;
    console.log('🔍 VOICE DEBUG: Final isVoiceEnabled:', isVoiceEnabled);
    
    setVoiceEnabled(isVoiceEnabled);
    
    if (isVoiceEnabled) {
      console.log('🎤 VOICE DEBUG: Voice chat enabled for this chatbot - initializing services');
      initializeVoiceServices();
    } else {
      console.log('🔇 VOICE DEBUG: Voice chat disabled for this chatbot');
      console.log('🔍 VOICE DEBUG: Possible reasons:');
      console.log('  - behavior_config is null/undefined:', !chatbot?.behavior_config);
      console.log('  - enableVoice is false:', chatbot?.behavior_config?.enableVoice === false);
      console.log('  - enableVoice is undefined:', chatbot?.behavior_config?.enableVoice === undefined);
    }
  }, [chatbot]);

  const initializeVoiceServices = () => {
    console.log('🔧 VOICE DEBUG: Starting voice services initialization...');
    
    try {
      // Initialize Speech Recognition
      console.log('🔍 VOICE DEBUG: Checking for Speech Recognition API...');
      console.log('🔍 VOICE DEBUG: webkitSpeechRecognition available:', 'webkitSpeechRecognition' in window);
      console.log('🔍 VOICE DEBUG: SpeechRecognition available:', 'SpeechRecognition' in window);
      
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        recognitionRef.current.lang = 'en-US';

        console.log('✅ VOICE DEBUG: Speech Recognition initialized with settings:', {
          continuous: recognitionRef.current.continuous,
          interimResults: recognitionRef.current.interimResults,
          lang: recognitionRef.current.lang
        });

        recognitionRef.current.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          const confidence = event.results[0][0].confidence;
          console.log('🎤 VOICE DEBUG: Speech recognized:', {
            transcript,
            confidence,
            resultsLength: event.results.length
          });
          
          setInputValue(transcript);
          setIsListening(false);
          
          // Auto-send the message after a short delay to allow user to see the transcript
          setTimeout(() => {
            if (transcript.trim()) {
              console.log('🎤 VOICE DEBUG: Auto-sending voice message after delay:', transcript);
              sendVoiceMessage(transcript);
            }
          }, 500);
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error('🎤 VOICE DEBUG: Speech recognition error:', {
            error: event.error,
            message: event.message,
            type: event.type
          });
          setIsListening(false);
          toast({
            title: "Voice Input Error",
            description: `Failed to recognize speech: ${event.error}. Please try again.`,
            variant: "destructive",
          });
        };

        recognitionRef.current.onstart = () => {
          console.log('🎤 VOICE DEBUG: Speech recognition started');
        };

        recognitionRef.current.onend = () => {
          console.log('🎤 VOICE DEBUG: Speech recognition ended');
          setIsListening(false);
        };
      } else {
        console.error('🎤 VOICE DEBUG: Speech Recognition API not available in this browser');
        toast({
          title: "Voice Input Not Supported",
          description: "Your browser doesn't support speech recognition.",
          variant: "destructive",
        });
      }

      // Initialize Speech Synthesis
      console.log('🔍 VOICE DEBUG: Checking for Speech Synthesis API...');
      console.log('🔍 VOICE DEBUG: speechSynthesis available:', 'speechSynthesis' in window);
      
      if ('speechSynthesis' in window) {
        synthRef.current = window.speechSynthesis;
        console.log('✅ VOICE DEBUG: Speech Synthesis initialized');
        
        // Log available voices
        const voices = synthRef.current.getVoices();
        console.log('🔍 VOICE DEBUG: Available voices:', voices.length);
        if (voices.length === 0) {
          // Voices might not be loaded yet, try after a delay
          setTimeout(() => {
            const delayedVoices = synthRef.current?.getVoices() || [];
            console.log('🔍 VOICE DEBUG: Available voices (delayed):', delayedVoices.length);
            delayedVoices.slice(0, 5).forEach((voice, i) => {
              console.log(`  ${i + 1}. ${voice.name} (${voice.lang}) - ${voice.localService ? 'Local' : 'Remote'}`);
            });
          }, 1000);
        } else {
          voices.slice(0, 5).forEach((voice, i) => {
            console.log(`  ${i + 1}. ${voice.name} (${voice.lang}) - ${voice.localService ? 'Local' : 'Remote'}`);
          });
        }
      } else {
        console.error('🔊 VOICE DEBUG: Speech Synthesis API not available in this browser');
        toast({
          title: "Voice Output Not Supported",
          description: "Your browser doesn't support speech synthesis.",
          variant: "destructive",
        });
      }

      console.log('✅ VOICE DEBUG: Voice services initialization completed');
    } catch (error) {
      console.error('💥 VOICE DEBUG: Failed to initialize voice services:', error);
      toast({
        title: "Voice Services Error",
        description: "Failed to initialize voice services. Check console for details.",
        variant: "destructive",
      });
    }
  };

  const startListening = () => {
    console.log('🎤 VOICE DEBUG: startListening called');
    console.log('🔍 VOICE DEBUG: recognitionRef.current exists:', !!recognitionRef.current);
    console.log('🔍 VOICE DEBUG: voiceEnabled:', voiceEnabled);
    
    if (!recognitionRef.current || !voiceEnabled) {
      console.warn('⚠️ VOICE DEBUG: Cannot start listening - missing requirements:', {
        hasRecognition: !!recognitionRef.current,
        voiceEnabled
      });
      return;
    }
    
    try {
      console.log('🎤 VOICE DEBUG: Setting isListening to true and starting recognition...');
      setIsListening(true);
      recognitionRef.current.start();
      console.log('✅ VOICE DEBUG: Speech recognition start() called successfully');
    } catch (error) {
      console.error('💥 VOICE DEBUG: Failed to start listening:', error);
      setIsListening(false);
      toast({
        title: "Voice Input Error",
        description: "Failed to start voice input. Please try again.",
        variant: "destructive",
      });
    }
  };

  const stopListening = () => {
    console.log('🎤 VOICE DEBUG: stopListening called');
    
    if (!recognitionRef.current) {
      console.warn('⚠️ VOICE DEBUG: Cannot stop listening - no recognition ref');
      return;
    }
    
    try {
      console.log('🎤 VOICE DEBUG: Stopping recognition and setting isListening to false...');
      recognitionRef.current.stop();
      setIsListening(false);
      console.log('✅ VOICE DEBUG: Speech recognition stopped successfully');
    } catch (error) {
      console.error('💥 VOICE DEBUG: Failed to stop listening:', error);
    }
  };

  const speakResponse = (text: string) => {
    console.log('🔊 VOICE DEBUG: speakResponse called with text:', text?.substring(0, 100) + '...');
    console.log('🔍 VOICE DEBUG: synthRef.current exists:', !!synthRef.current);
    console.log('🔍 VOICE DEBUG: voiceEnabled:', voiceEnabled);
    console.log('🔍 VOICE DEBUG: text length:', text?.length);

    if (!synthRef.current || !voiceEnabled) {
      console.warn('⚠️ VOICE DEBUG: Cannot speak - missing requirements:', {
        hasSynth: !!synthRef.current,
        voiceEnabled,
        hasText: !!text
      });
      return;
    }

    if (!text || !text.trim()) {
      console.warn('⚠️ VOICE DEBUG: Cannot speak - empty text');
      return;
    }

    try {
      console.log('🔊 VOICE DEBUG: Canceling any ongoing speech...');
      synthRef.current.cancel();
      
      console.log('🔊 VOICE DEBUG: Creating speech utterance...');
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;
      
      console.log('🔊 VOICE DEBUG: Utterance created with settings:', {
        rate: utterance.rate,
        pitch: utterance.pitch,
        volume: utterance.volume,
        lang: utterance.lang,
        voice: utterance.voice?.name
      });
      
      utterance.onstart = () => {
        setIsSpeaking(true);
        console.log('🔊 VOICE DEBUG: ✅ Speech synthesis STARTED - utterance.onstart fired');
      };
      
      utterance.onend = () => {
        setIsSpeaking(false);
        console.log('🔊 VOICE DEBUG: ✅ Speech synthesis ENDED - utterance.onend fired');
      };
      
      utterance.onerror = (event) => {
        setIsSpeaking(false);
        console.error('💥 VOICE DEBUG: Speech synthesis ERROR:', {
          error: event.error,
          type: event.type,
          charIndex: event.charIndex,
          elapsedTime: event.elapsedTime
        });
      };

      utterance.onpause = () => {
        console.log('⏸️ VOICE DEBUG: Speech synthesis PAUSED');
      };

      utterance.onresume = () => {
        console.log('▶️ VOICE DEBUG: Speech synthesis RESUMED');
      };

      utterance.onboundary = (event) => {
        console.log('🔊 VOICE DEBUG: Speech boundary event:', {
          name: event.name,
          charIndex: event.charIndex,
          elapsedTime: event.elapsedTime
        });
      };

      console.log('🔊 VOICE DEBUG: Calling synthRef.current.speak()...');
      synthRef.current.speak(utterance);
      console.log('🔊 VOICE DEBUG: ✅ synthRef.current.speak() called successfully');
      
      // Additional debug info
      setTimeout(() => {
        console.log('🔊 VOICE DEBUG: Speech status after 100ms:', {
          speaking: synthRef.current?.speaking,
          pending: synthRef.current?.pending,
          paused: synthRef.current?.paused,
          isSpeaking: isSpeaking
        });
      }, 100);
      
    } catch (error) {
      console.error('💥 VOICE DEBUG: Failed to speak response:', error);
      setIsSpeaking(false);
      toast({
        title: "Voice Output Error",
        description: "Failed to speak response. Check console for details.",
        variant: "destructive",
      });
    }
  };

  const stopSpeaking = () => {
    console.log('🔊 VOICE DEBUG: stopSpeaking called');
    
    if (!synthRef.current) {
      console.warn('⚠️ VOICE DEBUG: Cannot stop speaking - no synth ref');
      return;
    }
    
    try {
      console.log('🔊 VOICE DEBUG: Canceling speech synthesis...');
      synthRef.current.cancel();
      setIsSpeaking(false);
      console.log('✅ VOICE DEBUG: Speech synthesis stopped successfully');
    } catch (error) {
      console.error('💥 VOICE DEBUG: Failed to stop speaking:', error);
    }
  };

  const sendVoiceMessage = async (message: string) => {
    console.log('🎤 VOICE DEBUG: sendVoiceMessage called with:', message);
    console.log('🔍 VOICE DEBUG: Current state check:', {
      messageLength: message?.length,
      isLoading,
      chatbotId: chatbot?.id,
      voiceEnabled
    });

    if (!message.trim() || isLoading || !chatbot?.id) {
      console.warn('⚠️ VOICE DEBUG: Cannot send voice message - requirements not met:', {
        hasMessage: !!message.trim(),
        isLoading,
        hasChatbotId: !!chatbot?.id
      });
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };

    console.log('🎤 VOICE DEBUG: Adding user message to chat:', userMessage);
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      console.log('🎤 VOICE DEBUG: Sending voice message to chatbot:', chatbot.id);
      
      // Convert messages to API format
      const conversationHistory: TestChatMessage[] = messages.map(msg => ({
        role: msg.role === 'bot' ? 'assistant' : msg.role,
        content: msg.content
      }));

      console.log('📡 VOICE DEBUG: Conversation history prepared:', {
        historyLength: conversationHistory.length,
        lastMessages: conversationHistory.slice(-2)
      });

      // Call real API
      console.log('📡 VOICE DEBUG: Calling testChatbot API with voice message...');
      
      const response = await apiService.testChatbot(chatbot.id, {
        message: message,
        conversation_history: conversationHistory,
      });

      console.log('🎯 VOICE DEBUG: Got chatbot response for voice:', {
        hasResponse: !!response?.response,
        responseLength: response?.response?.length || 0,
        ragEnabled: response?.rag_enabled,
        contextCount: response?.context_count || 0,
        model: response?.model,
        fullResponse: response
      });
      
      if (!response || !response.response) {
        throw new Error('Invalid response from chatbot API');
      }
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: response.response,
        timestamp: new Date(),
      };

      console.log('🎤 VOICE DEBUG: Adding bot response to chat:', botMessage);
      setMessages(prev => [...prev, botMessage]);

      // Always trigger voice response for voice messages
      console.log('🔊 VOICE DEBUG: 🎯 CRITICAL: About to call speakResponse for voice input');
      console.log('🔊 VOICE DEBUG: Response text to speak:', response.response?.substring(0, 100) + '...');
      console.log('🔊 VOICE DEBUG: Current voiceEnabled state:', voiceEnabled);
      console.log('🔊 VOICE DEBUG: synthRef.current exists:', !!synthRef.current);
      
      speakResponse(response.response);
      
      console.log('🔊 VOICE DEBUG: ✅ speakResponse called for voice message');
    } catch (error) {
      console.error('❌ VOICE DEBUG: Voice chat error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to send voice message';
      
      toast({
        title: "Voice Chat Error",
        description: errorMessage,
        variant: "destructive",
      });

      // Add error message to chat
      const errorBotMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: `❌ Voice Error: ${errorMessage}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorBotMessage]);
    } finally {
      console.log('🎤 VOICE DEBUG: Voice message processing completed, setting isLoading to false');
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading || !chatbot?.id) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      console.log('🧪 Sending test chat message to chatbot:', chatbot.id);
      
      // Convert messages to API format
      const conversationHistory: TestChatMessage[] = messages.map(msg => ({
        role: msg.role === 'bot' ? 'assistant' : msg.role,
        content: msg.content
      }));

      // Call real API
      console.log('📡 RAG DEBUG: Calling testChatbot API with message:', currentInput);
      console.log('💬 RAG DEBUG: Conversation history length:', conversationHistory.length);
      
      const response = await apiService.testChatbot(chatbot.id, {
        message: currentInput,
        conversation_history: conversationHistory,
      });

      console.log('🎯 RAG DEBUG: Got chatbot response:', {
        hasResponse: !!response?.response,
        responseLength: response?.response?.length || 0,
        ragEnabled: response?.rag_enabled,
        contextCount: response?.context_count || 0,
        model: response?.model,
        fullResponse: response
      });
      
      if (!response || !response.response) {
        throw new Error('Invalid response from chatbot API');
      }
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: response.response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);

      // Trigger voice response if voice is enabled
      if (voiceEnabled && response.response) {
        console.log('🔊 VOICE DEBUG: 🎯 CRITICAL: Voice enabled for text message, triggering speech synthesis');
        console.log('🔊 VOICE DEBUG: Text message response to speak:', response.response?.substring(0, 100) + '...');
        console.log('🔊 VOICE DEBUG: Current voiceEnabled state:', voiceEnabled);
        console.log('🔊 VOICE DEBUG: synthRef.current exists:', !!synthRef.current);
        speakResponse(response.response);
        console.log('🔊 VOICE DEBUG: ✅ speakResponse called for text message');
      } else {
        console.log('🔊 VOICE DEBUG: NOT triggering speech synthesis for text message:', {
          voiceEnabled,
          hasResponse: !!response.response,
          responseLength: response.response?.length
        });
      }
    } catch (error) {
      console.error('❌ Test chat error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      
      toast({
        title: "Chat Error",
        description: errorMessage,
        variant: "destructive",
      });

      // Add error message to chat
      const errorBotMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: `❌ Error: ${errorMessage}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorBotMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const resetChat = () => {
    setMessages([
      {
        id: '1',
        role: 'bot',
        content: chatbot?.appearance_config?.greetingMessage || 'Hello! How can I help you today?',
        timestamp: new Date(),
      }
    ]);
    setInputValue('');
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Test Your Chatbot
              </CardTitle>
              <CardDescription>
                Test how your chatbot responds to different messages and questions.
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={resetChat}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset Chat
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg bg-muted/20">
            <ScrollArea ref={scrollAreaRef} className="h-[400px] p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex items-start space-x-2 ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.role === 'bot' && (
                      <div className="flex-shrink-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                        <Bot className="h-4 w-4 text-primary-foreground" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-lg px-3 py-2 ${
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground ml-auto'
                          : 'bg-background border'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        message.role === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'
                      }`}>
                        {formatTime(message.timestamp)}
                      </p>
                    </div>
                    {message.role === 'user' && (
                      <div className="flex-shrink-0 w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                        <User className="h-4 w-4 text-muted-foreground" />
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="flex items-start space-x-2">
                    <div className="flex-shrink-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                      <Bot className="h-4 w-4 text-primary-foreground" />
                    </div>
                    <div className="bg-background border rounded-lg px-3 py-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>
            <div className="border-t p-4">
              <div className="flex space-x-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={voiceEnabled ? "Type or click mic to speak..." : "Type your message..."}
                  disabled={isLoading}
                  className="flex-1"
                />
                
                {voiceEnabled && (
                  <>
                    <Button
                      onClick={isListening ? stopListening : startListening}
                      disabled={isLoading || isSpeaking}
                      size="sm"
                      variant={isListening ? "destructive" : "outline"}
                      className={isListening ? "animate-pulse" : ""}
                    >
                      {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                    </Button>
                    
                    <Button
                      onClick={isSpeaking ? stopSpeaking : undefined}
                      disabled={!isSpeaking}
                      size="sm"
                      variant={isSpeaking ? "destructive" : "outline"}
                      className={isSpeaking ? "animate-pulse" : ""}
                    >
                      {isSpeaking ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                    </Button>
                  </>
                )}
                
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  size="sm"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              
              {voiceEnabled && (
                <div className="mt-2 text-xs text-muted-foreground text-center">
                  {isListening && "🎤 Listening... Speak now"}
                  {isSpeaking && "🔊 Bot is speaking..."}
                  {!isListening && !isSpeaking && "Voice chat enabled - Click mic to speak"}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Testing Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>• Try asking questions that your users would typically ask</p>
            <p>• Test edge cases and unusual inputs to see how the bot responds</p>
            <p>• Check if the bot maintains context throughout the conversation</p>
            <p>• Verify that the bot's tone matches your system prompt</p>
            <p>• Test with documents you've uploaded to see if the RAG system works correctly</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}