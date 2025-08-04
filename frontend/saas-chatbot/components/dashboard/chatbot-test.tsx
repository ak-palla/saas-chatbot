'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageSquare, Send, Bot, User, RotateCcw, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { apiService, TestChatMessage } from '@/lib/api';
import { createClient } from '@/lib/supabase/client';

interface ChatbotTestProps {
  chatbot: any;
}

interface Message {
  id: string;
  role: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

// Initialize Supabase client using the same method as API service

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
      console.log('🔍 RAG DEBUG: Voice mode enabled - checking RAG impact');
      console.log('🔍 RAG DEBUG: Chatbot will use voice processing pipeline');
      console.log('🔍 RAG DEBUG: This may affect how RAG context is retrieved and processed');
      initializeVoiceServices();
    } else {
      console.log('🔇 VOICE DEBUG: Voice chat disabled for this chatbot');
      console.log('🔍 RAG DEBUG: Regular text mode - RAG should work normally');
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
      console.log('🔊 TTS DEBUG: ==================== TTS SYSTEM DETECTION ====================');
      console.log('🔊 TTS DEBUG: Checking for Speech Synthesis API...');
      console.log('🔊 TTS DEBUG: speechSynthesis available:', 'speechSynthesis' in window);
      console.log('🔊 TTS DEBUG: 🎯 CURRENT TTS SYSTEM: Browser Web Speech API (NOT Deepgram)');
      console.log('🔊 TTS DEBUG: This uses the browser\'s built-in text-to-speech engine');
      
      if ('speechSynthesis' in window) {
        synthRef.current = window.speechSynthesis;
        console.log('✅ TTS DEBUG: Browser Speech Synthesis initialized');
        console.log('🔊 TTS DEBUG: TTS Provider: Browser Web Speech API');
        console.log('🔊 TTS DEBUG: TTS Type: Client-side (no API calls to Deepgram)');
        
        // Log available voices
        const voices = synthRef.current.getVoices();
        console.log('🔊 TTS DEBUG: Available browser voices:', voices.length);
        if (voices.length === 0) {
          // Voices might not be loaded yet, try after a delay
          setTimeout(() => {
            const delayedVoices = synthRef.current?.getVoices() || [];
            console.log('🔊 TTS DEBUG: Available browser voices (delayed):', delayedVoices.length);
            console.log('🔊 TTS DEBUG: 📋 Voice List (Browser TTS):');
            delayedVoices.slice(0, 5).forEach((voice, i) => {
              console.log(`  ${i + 1}. ${voice.name} (${voice.lang}) - ${voice.localService ? 'Local' : 'Remote'} - Browser Engine`);
            });
          }, 1000);
        } else {
          console.log('🔊 TTS DEBUG: 📋 Voice List (Browser TTS):');
          voices.slice(0, 5).forEach((voice, i) => {
            console.log(`  ${i + 1}. ${voice.name} (${voice.lang}) - ${voice.localService ? 'Local' : 'Remote'} - Browser Engine`);
          });
        }
      } else {
        console.error('🔊 TTS DEBUG: Browser Speech Synthesis API not available in this browser');
        console.log('🔊 TTS DEBUG: Would need to implement Deepgram TTS as fallback');
        toast({
          title: "Voice Output Not Supported",
          description: "Your browser doesn't support speech synthesis.",
          variant: "destructive",
        });
      }

      // Check TTS implementation status
      console.log('🔊 TTS DEBUG: Checking TTS implementation status...');
      console.log('🔊 TTS DEBUG: 📋 TTS SYSTEM STATUS (TEMPORARY):');
      console.log('🔊 TTS DEBUG: ✅ Browser TTS: IMPLEMENTED and ACTIVE');
      console.log('🔊 TTS DEBUG: 🔧 Deepgram TTS: IMPLEMENTED but TEMPORARILY DISABLED');
      console.log('🔊 TTS DEBUG: 🎯 CURRENT STRATEGY: Browser TTS only');
      console.log('🔊 TTS DEBUG: 💰 COST: Browser $0.00 (free)');
      console.log('🔊 TTS DEBUG: 🔧 NOTE: Fixing Deepgram API integration (CORS + Auth issues)');
      console.log('🔊 TTS DEBUG: ===============================================================');

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


  const speakResponseWithBrowser = (text: string) => {
    console.log('🔊 TTS DEBUG: ==================== BROWSER TTS ====================');
    console.log('🔊 TTS DEBUG: 🎯 USING: Browser Web Speech API');
    console.log('🔊 TTS DEBUG: Text length:', text.length);

    if (!synthRef.current) {
      console.error('💥 TTS DEBUG: Browser TTS not available');
      throw new Error('Browser TTS not available');
    }

    return new Promise<void>((resolve, reject) => {
      try {
        // Cancel any ongoing speech
        synthRef.current!.cancel();
        
        // Small delay to ensure cancellation is processed
        setTimeout(() => {
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.rate = 1.0;
          utterance.pitch = 1.0;
          utterance.volume = 1.0;
          
          console.log('🔊 TTS DEBUG: Creating utterance with settings:', {
            rate: utterance.rate,
            pitch: utterance.pitch,
            volume: utterance.volume,
            text: text.substring(0, 50) + '...'
          });
          
          utterance.onstart = () => {
            setIsSpeaking(true);
            console.log('🔊 TTS DEBUG: ✅ BROWSER TTS STARTED');
            console.log('🔊 TTS DEBUG: Engine: Browser Web Speech API');
            console.log('🔊 TTS DEBUG: Cost: $0.00 (free)');
          };
          
          utterance.onend = () => {
            setIsSpeaking(false);
            console.log('🔊 TTS DEBUG: ✅ BROWSER TTS ENDED');
            resolve();
          };
          
          utterance.onerror = (event) => {
            setIsSpeaking(false);
            console.error('💥 TTS DEBUG: BROWSER TTS ERROR:', {
              error: event.error,
              type: event.type,
              charIndex: event.charIndex
            });
            reject(new Error(`Browser TTS error: ${event.error}`));
          };

          utterance.onpause = () => {
            console.log('⏸️ TTS DEBUG: Browser TTS paused');
          };

          utterance.onresume = () => {
            console.log('▶️ TTS DEBUG: Browser TTS resumed');
          };

          console.log('🔊 TTS DEBUG: Calling speak()...');
          synthRef.current!.speak(utterance);
          console.log('🔊 TTS DEBUG: ✅ speak() called successfully');
          
          // Additional debug after short delay
          setTimeout(() => {
            console.log('🔊 TTS DEBUG: Speech status check:', {
              speaking: synthRef.current!.speaking,
              pending: synthRef.current!.pending,
              paused: synthRef.current!.paused
            });
          }, 100);
          
        }, 10); // Small delay to ensure cancellation is processed
        
      } catch (error) {
        setIsSpeaking(false);
        console.error('💥 TTS DEBUG: Browser TTS setup failed:', error);
        reject(error);
      }
    });
  };

  // Primary Deepgram TTS function
  const speakResponseWithDeepgram = async (text: string): Promise<void> => {
    console.log('🔊 DEEPGRAM TTS: ==================== DEEPGRAM TTS SYSTEM ====================');
    console.log('🔊 DEEPGRAM TTS: Starting TTS request for text:', text?.substring(0, 100) + '...');
    console.log('🔊 DEEPGRAM TTS: Text length:', text?.length);
    
    try {
      setIsSpeaking(true);
      
      // Call our frontend API route that proxies to Deepgram
      console.log('🔊 DEEPGRAM TTS: Calling frontend TTS API route...');
      
      // Get user email for the request (using same method as API service)
      let userEmail = null;
      try {
        const supabase = createClient();
        const { data: { user }, error } = await supabase.auth.getUser();
        if (!error && user?.email) {
          userEmail = user.email;
          console.log('🔊 DEEPGRAM TTS: Got user email:', userEmail);
        } else {
          console.error('🔊 DEEPGRAM TTS: Failed to get user:', error);
        }
      } catch (error) {
        console.error('🔊 DEEPGRAM TTS: Error getting user:', error);
      }
      
      if (!userEmail) {
        throw new Error('User not authenticated - no email found');
      }
      
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          voice: 'aura-asteria-en',
          encoding: 'mp3', // Use MP3 format (supported by Deepgram)
          speed: 1.0,
          pitch: 1.0,
          user_email: userEmail
        })
      });
      
      console.log('🔊 DEEPGRAM TTS: Frontend API response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('🔊 DEEPGRAM TTS: API request failed:', {
          status: response.status,
          statusText: response.statusText,
          error: errorText
        });
        throw new Error(`TTS API failed: ${response.status} ${response.statusText}`);
      }
      
      // Get audio data as ArrayBuffer
      const audioBuffer = await response.arrayBuffer();
      console.log('🔊 DEEPGRAM TTS: Received audio buffer:', {
        size: audioBuffer.byteLength,
        type: 'ArrayBuffer'
      });
      
      if (audioBuffer.byteLength === 0) {
        throw new Error('Received empty audio buffer');
      }
      
      // Create audio blob and play it
      const audioBlob = new Blob([audioBuffer], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(audioBlob);
      
      console.log('🔊 DEEPGRAM TTS: Created audio URL:', audioUrl);
      
      // Create and play audio element
      const audio = new Audio(audioUrl);
      
      // Set up audio event handlers
      audio.onloadstart = () => {
        console.log('🔊 DEEPGRAM TTS: Audio loading started');
      };
      
      audio.oncanplay = () => {
        console.log('🔊 DEEPGRAM TTS: Audio can start playing');
      };
      
      audio.onplay = () => {
        console.log('🔊 DEEPGRAM TTS: Audio playback started');
      };
      
      audio.onended = () => {
        console.log('🔊 DEEPGRAM TTS: Audio playback ended');
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl); // Clean up
      };
      
      audio.onerror = (error) => {
        console.error('🔊 DEEPGRAM TTS: Audio playback error:', error);
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl); // Clean up
        throw new Error('Audio playback failed');
      };
      
      // Start playing
      console.log('🔊 DEEPGRAM TTS: Starting audio playback...');
      await audio.play();
      
      console.log('🔊 DEEPGRAM TTS: ✅ SUCCESS: Deepgram TTS completed successfully');
      
    } catch (error) {
      console.error('💥 DEEPGRAM TTS: Failed:', error);
      setIsSpeaking(false);
      throw error; // Re-throw for fallback handling
    }
    
    console.log('🔊 DEEPGRAM TTS: ================================================================');
  };

  const speakResponse = async (text: string) => {
    console.log('🔊 TTS DEBUG: ==================== HYBRID TTS SYSTEM ====================');
    console.log('🔊 TTS DEBUG: speakResponse called with text:', text?.substring(0, 100) + '...');
    console.log('🔊 TTS DEBUG: voiceEnabled:', voiceEnabled);
    console.log('🔊 TTS DEBUG: text length:', text?.length);
    console.log('🔊 TTS DEBUG: 🎯 Using HYBRID TTS: Deepgram (Primary) → Browser (Fallback)');

    if (!text || !text.trim()) {
      console.warn('⚠️ TTS DEBUG: Cannot speak - empty text');
      return;
    }

    try {
      // Try Deepgram TTS first
      console.log('🔊 TTS DEBUG: 🎯 TRYING: Deepgram TTS (Primary)');
      await speakResponseWithDeepgram(text);
      console.log('🔊 TTS DEBUG: ✅ SUCCESS: Deepgram TTS completed successfully');
      
    } catch (deepgramError) {
      console.warn('⚠️ TTS DEBUG: Deepgram TTS failed, falling back to Browser TTS');
      console.warn('⚠️ TTS DEBUG: Deepgram error:', deepgramError);
      
      try {
        // Fall back to Browser TTS
        console.log('🔊 TTS DEBUG: 🔄 FALLBACK: Using Browser TTS');
        await speakResponseWithBrowser(text);
        console.log('🔊 TTS DEBUG: ✅ SUCCESS: Browser TTS fallback completed successfully');
        
      } catch (browserError) {
        console.error('💥 TTS DEBUG: Both Deepgram and Browser TTS failed!');
        console.error('💥 TTS DEBUG: Deepgram error:', deepgramError);
        console.error('💥 TTS DEBUG: Browser error:', browserError);
        
        setIsSpeaking(false);
        toast({
          title: "Voice Output Error",
          description: "Both Deepgram and Browser TTS failed. Check console for details.",
          variant: "destructive",
        });
      }
    }
    
    console.log('🔊 TTS DEBUG: ================================================================');
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
    
    // Re-check voice enabled status from chatbot directly (in case state got reset)
    const currentVoiceEnabled = chatbot?.behavior_config?.enableVoice || false;
    console.log('🔍 VOICE DEBUG: Current state check:', {
      messageLength: message?.length,
      isLoading,
      chatbotId: chatbot?.id,
      voiceEnabled,
      currentVoiceEnabled,
      behaviorConfig: chatbot?.behavior_config
    });
    
    // Use the current voice status from chatbot data, not the potentially stale state
    const shouldUseVoice = currentVoiceEnabled;

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
      console.log('🔍 RAG DEBUG: This is a VOICE-based message');
      console.log('🔍 RAG DEBUG: Voice enabled for this chatbot:', voiceEnabled);
      console.log('🔍 RAG DEBUG: Backend should process this through voice service pipeline');
      console.log('🔍 RAG DEBUG: Voice service should call message service with use_rag=true');
      
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
      console.log('🔊 VOICE DEBUG: shouldUseVoice (from chatbot data):', shouldUseVoice);
      console.log('🔊 VOICE DEBUG: synthRef.current exists:', !!synthRef.current);
      
      // Use shouldUseVoice instead of voiceEnabled for voice messages
      if (shouldUseVoice && response.response) {
        console.log('🔊 VOICE DEBUG: ✅ FORCING speech synthesis for voice input (bypassing state issue)');
        console.log('🔊 VOICE DEBUG: 🎯 BYPASSING voiceEnabled state and calling Browser TTS directly');
        
        // Use the hybrid TTS system (Deepgram primary, Browser fallback)
        try {
          await speakResponse(response.response);
          console.log('🔊 VOICE DEBUG: ✅ Hybrid TTS completed successfully');
        } catch (error) {
          console.error('💥 VOICE DEBUG: Hybrid TTS failed:', error);
        }
      } else {
        console.log('🔊 VOICE DEBUG: ❌ NOT using speech synthesis:', {
          shouldUseVoice,
          hasResponse: !!response.response
        });
      }
      
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
      console.log('🔍 RAG FLOW DEBUG: ==================== TEXT MESSAGE PROCESSING ====================');
      console.log('📡 RAG FLOW DEBUG: Calling testChatbot API with message:', currentInput);
      console.log('💬 RAG FLOW DEBUG: Conversation history length:', conversationHistory.length);
      console.log('🔍 RAG FLOW DEBUG: Voice enabled for this chatbot:', voiceEnabled);
      console.log('🔍 RAG FLOW DEBUG: This is a TEXT-based message (not voice input)');
      console.log('🔍 RAG FLOW DEBUG: Chatbot behavior_config:', JSON.stringify(chatbot?.behavior_config, null, 2));
      console.log('🔍 RAG FLOW DEBUG: Expected: RAG should work normally for text messages regardless of voice setting');
      
      const response = await apiService.testChatbot(chatbot.id, {
        message: currentInput,
        conversation_history: conversationHistory,
      });

      console.log('🔍 RAG FLOW DEBUG: ==================== RESPONSE RECEIVED ====================');
      console.log('🎯 RAG FLOW DEBUG: Got chatbot response:', {
        hasResponse: !!response?.response,
        responseLength: response?.response?.length || 0,
        ragEnabled: response?.rag_enabled,
        contextCount: response?.context_count || 0,
        model: response?.model,
        responsePreview: response?.response?.substring(0, 100) + '...',
        fullResponse: response
      });
      console.log('🔍 RAG FLOW DEBUG: RAG Analysis:');
      console.log('   - RAG Enabled:', response?.rag_enabled);
      console.log('   - Context Count:', response?.context_count || 0);
      console.log('   - Contains PDF content:', response?.response?.includes('Monday') || response?.response?.includes('business hours'));
      console.log('   - Is generic response:', response?.response?.includes('24 hours') || response?.response?.includes('Walmart'));
      
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

      // Trigger voice response if voice is enabled (using shouldUseVoice for reliability)
      const shouldUseVoice = chatbot?.behavior_config?.enableVoice || false;
      console.log('🔍 RAG FLOW DEBUG: ==================== VOICE PROCESSING CHECK ====================');
      console.log('🔊 RAG FLOW DEBUG: Text message response completed:', {
        voiceEnabled,
        shouldUseVoice,
        responseLength: response.response?.length,
        behaviorConfig: chatbot?.behavior_config
      });
      console.log('🔍 RAG FLOW DEBUG: Voice processing decision:');
      console.log('   - Voice enabled in settings:', voiceEnabled);
      console.log('   - Should use voice for response:', shouldUseVoice);
      console.log('   - Will trigger TTS:', shouldUseVoice && response.response);
      
      if (shouldUseVoice && response.response) {
        console.log('🔊 TEXT DEBUG: ✅ FORCING speech synthesis for text message (bypassing state issue)');
        console.log('🔊 TEXT DEBUG: Text message response to speak:', response.response?.substring(0, 100) + '...');
        console.log('🔊 TEXT DEBUG: 🎯 Using HYBRID TTS: Deepgram (Primary) → Browser (Fallback)');
        
        try {
          await speakResponse(response.response);
          console.log('🔊 TEXT DEBUG: ✅ Hybrid TTS completed for text message');
        } catch (error) {
          console.error('💥 TEXT DEBUG: Hybrid TTS failed for text message:', error);
        }
      } else {
        console.log('🔊 TEXT DEBUG: ❌ NOT using speech synthesis for text message:', {
          shouldUseVoice,
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