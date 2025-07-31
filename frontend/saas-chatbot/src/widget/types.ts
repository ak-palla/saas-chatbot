// Widget Configuration Types
export interface WidgetConfig {
  chatbotId: string;
  baseUrl?: string;
  theme?: 'light' | 'dark' | 'auto';
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  primaryColor?: string;
  greeting?: string;
  botName?: string;
  showAvatar?: boolean;
  avatarUrl?: string;
  enableVoice?: boolean;
  maxWidth?: number;
  maxHeight?: number;
  zIndex?: number;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'text' | 'voice' | 'file';
  metadata?: {
    audioSrc?: string;
    fileName?: string;
    fileSize?: number;
  };
}

export interface ChatbotResponse {
  message: string;
  type?: 'text' | 'voice';
  audioUrl?: string;
  suggestions?: string[];
  metadata?: Record<string, any>;
}

export interface VoiceSession {
  sessionId: string;
  isRecording: boolean;
  isPlaying: boolean;
  audioContext?: AudioContext;
  mediaRecorder?: MediaRecorder;
  audioChunks: Blob[];
}

export interface WebSocketMessage {
  type: 'message' | 'typing' | 'voice_start' | 'voice_end' | 'config_update';
  payload: any;
  chatbotId: string;
  sessionId?: string;
}