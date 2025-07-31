import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketClient, WebSocketMessage } from '@/lib/websocket/client';
import { VoiceWebSocketClient, VoiceSession } from '@/lib/websocket/voice-client';
import { useAudioRecorder } from './use-audio-recorder';

export function useWebSocket(url: string, options?: {
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  autoConnect?: boolean;
}) {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  
  const wsRef = useRef<WebSocketClient | null>(null);
  const listenersRef = useRef<Map<string, ((message: WebSocketMessage) => void)[]>>(new Map());

  const connect = useCallback(async () => {
    if (wsRef.current?.isConnected) return;

    setIsConnecting(true);
    setError(null);

    try {
      wsRef.current = new WebSocketClient({
        url,
        reconnectInterval: options?.reconnectInterval,
        maxReconnectAttempts: options?.maxReconnectAttempts,
      });

      // Set up event listeners
      wsRef.current.on('connected', () => {
        setIsConnected(true);
        setIsConnecting(false);
        setError(null);
      });

      wsRef.current.on('disconnected', () => {
        setIsConnected(false);
        setIsConnecting(false);
      });

      wsRef.current.on('error', (data) => {
        setError(data.error || 'WebSocket error');
        setIsConnecting(false);
      });

      wsRef.current.on('message', (message) => {
        setLastMessage(message);
      });

      // Add existing listeners
      listenersRef.current.forEach((callbacks, event) => {
        callbacks.forEach(callback => {
          wsRef.current!.on(event, callback);
        });
      });

      await wsRef.current.connect();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
      setIsConnecting(false);
    }
  }, [url, options]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.disconnect();
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsConnecting(false);
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (!wsRef.current?.isConnected) {
      throw new Error('WebSocket is not connected');
    }
    wsRef.current.send(message);
  }, []);

  const addEventListener = useCallback((event: string, callback: (message: WebSocketMessage) => void) => {
    if (!listenersRef.current.has(event)) {
      listenersRef.current.set(event, []);
    }
    listenersRef.current.get(event)!.push(callback);

    if (wsRef.current) {
      wsRef.current.on(event, callback);
    }
  }, []);

  const removeEventListener = useCallback((event: string, callback: (message: WebSocketMessage) => void) => {
    const listeners = listenersRef.current.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }

    if (wsRef.current) {
      wsRef.current.off(event, callback);
    }
  }, []);

  useEffect(() => {
    if (options?.autoConnect !== false) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect, options?.autoConnect]);

  return {
    isConnected,
    isConnecting,
    error,
    lastMessage,
    connect,
    disconnect,
    sendMessage,
    addEventListener,
    removeEventListener,
  };
}

export function useVoiceWebSocket(chatbotId: string, options?: {
  autoConnect?: boolean;
}) {
  const [session, setSession] = useState<VoiceSession | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const voiceWsRef = useRef<VoiceWebSocketClient | null>(null);

  const connect = useCallback(async () => {
    if (voiceWsRef.current?.isConnected) return;

    try {
      setError(null);
      voiceWsRef.current = new VoiceWebSocketClient(chatbotId);

      // Set up voice-specific handlers
      voiceWsRef.current.on('voice_session_started', (data) => {
        setSession(data);
      });

      voiceWsRef.current.on('voice_processing_started', () => {
        setIsProcessing(true);
      });

      voiceWsRef.current.on('voice_processing_complete', () => {
        setIsProcessing(false);
      });

      voiceWsRef.current.on('error', (data) => {
        setError(data.error || 'Voice WebSocket error');
        setIsRecording(false);
        setIsProcessing(false);
      });

      await voiceWsRef.current.connect();
      await voiceWsRef.current.startVoiceSession(chatbotId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Voice connection failed');
    }
  }, [chatbotId]);

  const disconnect = useCallback(() => {
    if (voiceWsRef.current) {
      voiceWsRef.current.endSession();
      voiceWsRef.current.disconnect();
      voiceWsRef.current = null;
    }
    setSession(null);
    setIsRecording(false);
    setIsProcessing(false);
  }, []);

  const startRecording = useCallback(() => {
    if (!voiceWsRef.current) {
      throw new Error('Voice WebSocket not connected');
    }
    voiceWsRef.current.startRecording();
    setIsRecording(true);
  }, []);

  const stopRecording = useCallback(() => {
    if (!voiceWsRef.current) return;
    voiceWsRef.current.stopRecording();
    setIsRecording(false);
  }, []);

  const sendAudioChunk = useCallback((audioData: Blob) => {
    if (!voiceWsRef.current) {
      throw new Error('Voice WebSocket not connected');
    }
    voiceWsRef.current.sendAudioChunk(audioData);
  }, []);

  const sendTextInput = useCallback((text: string) => {
    if (!voiceWsRef.current) {
      throw new Error('Voice WebSocket not connected');
    }
    voiceWsRef.current.sendTextInput(text);
  }, []);

  useEffect(() => {
    if (options?.autoConnect !== false) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect, options?.autoConnect]);

  return {
    session,
    isRecording,
    isProcessing,
    error,
    isConnected: voiceWsRef.current?.isConnected || false,
    connect,
    disconnect,
    startRecording,
    stopRecording,
    sendAudioChunk,
    sendTextInput,
  };
}

// Enhanced voice hook with integrated audio recording
export function useVoiceChat(chatbotId: string, options?: {
  autoConnect?: boolean;
  audioConfig?: {
    mimeType?: string;
    audioBitsPerSecond?: number;
    timeslice?: number;
  };
}) {
  const voiceWs = useVoiceWebSocket(chatbotId, { autoConnect: options?.autoConnect });
  const [audioLevel, setAudioLevel] = useState(0);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [audioSupported, setAudioSupported] = useState(false);

  // Audio recorder integration
  const audioRecorder = useAudioRecorder({
    mimeType: options?.audioConfig?.mimeType || 'audio/webm;codecs=opus',
    audioBitsPerSecond: options?.audioConfig?.audioBitsPerSecond || 128000,
    timeslice: options?.audioConfig?.timeslice || 1000,
    onDataAvailable: (audioChunk) => {
      if (voiceWs.isConnected && voiceWs.isRecording) {
        voiceWs.sendAudioChunk(audioChunk);
      }
    },
    onError: (error) => {
      console.error('Audio recording error:', error);
    },
    onStart: () => {
      voiceWs.startRecording();
    },
    onStop: () => {
      voiceWs.stopRecording();
    },
  });

  // Check audio support on mount
  useEffect(() => {
    setAudioSupported(
      typeof window !== 'undefined' && 
      'mediaDevices' in navigator && 
      'getUserMedia' in navigator.mediaDevices &&
      'MediaRecorder' in window
    );
  }, []);

  // Sync audio level and duration from recorder
  useEffect(() => {
    setAudioLevel(audioRecorder.audioLevel);
  }, [audioRecorder.audioLevel]);

  useEffect(() => {
    setRecordingDuration(audioRecorder.duration);
  }, [audioRecorder.duration]);

  const startVoiceRecording = useCallback(async () => {
    if (!audioSupported) {
      throw new Error('Audio recording is not supported in this browser');
    }
    
    if (!voiceWs.isConnected) {
      throw new Error('Voice WebSocket is not connected');
    }

    await audioRecorder.startRecording();
  }, [audioSupported, voiceWs.isConnected, audioRecorder]);

  const stopVoiceRecording = useCallback(() => {
    audioRecorder.stopRecording();
  }, [audioRecorder]);

  return {
    // Voice WebSocket state
    session: voiceWs.session,
    isConnected: voiceWs.isConnected,
    isRecording: audioRecorder.isRecording,
    isProcessing: voiceWs.isProcessing,
    error: voiceWs.error,
    
    // Audio recording state
    audioLevel,
    recordingDuration,
    audioSupported,
    
    // Actions
    connect: voiceWs.connect,
    disconnect: voiceWs.disconnect,
    startRecording: startVoiceRecording,
    stopRecording: stopVoiceRecording,
    sendTextInput: voiceWs.sendTextInput,
  };
}