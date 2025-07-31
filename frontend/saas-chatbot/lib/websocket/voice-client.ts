import { WebSocketClient, WebSocketMessage } from './client';

export interface VoiceMessage extends WebSocketMessage {
  type: 'audio_start' | 'audio_chunk' | 'audio_stop' | 'text_input' | 'voice_response' | 'error' | 'status';
  session_id?: string;
  audio_data?: ArrayBuffer;
  text?: string;
  metadata?: Record<string, any>;
}

export interface VoiceSession {
  sessionId: string;
  chatbotId: string;
  isRecording: boolean;
  isProcessing: boolean;
  conversationId?: string;
}

export class VoiceWebSocketClient extends WebSocketClient {
  private currentSession: VoiceSession | null = null;
  private audioChunks: Blob[] = [];

  constructor(chatbotId: string) {
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/voice/${chatbotId}`;
    
    super({
      url: wsUrl,
      reconnectInterval: 5000,
      maxReconnectAttempts: 3,
    });

    this.setupVoiceHandlers();
  }

  private setupVoiceHandlers(): void {
    this.on('connected', () => {
      console.log('Voice WebSocket connected');
    });

    this.on('voice_session_started', (data) => {
      this.currentSession = {
        sessionId: data.session_id,
        chatbotId: data.chatbot_id,
        isRecording: false,
        isProcessing: false,
        conversationId: data.conversation_id,
      };
      console.log('Voice session started:', this.currentSession);
    });

    this.on('audio_chunk_received', (data) => {
      console.log('Audio chunk received:', data.size, 'bytes');
    });

    this.on('voice_processing_started', () => {
      if (this.currentSession) {
        this.currentSession.isProcessing = true;
      }
    });

    this.on('voice_processing_complete', (data) => {
      if (this.currentSession) {
        this.currentSession.isProcessing = false;
      }
      console.log('Voice processing complete:', data);
    });

    this.on('voice_response', (data) => {
      if (data.audio_url) {
        this.playAudioResponse(data.audio_url);
      }
    });

    this.on('error', (data) => {
      console.error('Voice WebSocket error:', data.error);
      if (this.currentSession) {
        this.currentSession.isProcessing = false;
        this.currentSession.isRecording = false;
      }
    });
  }

  async startVoiceSession(chatbotId: string): Promise<void> {
    if (!this.isConnected) {
      await this.connect();
    }

    this.send({
      type: 'voice_session_start',
      data: { chatbot_id: chatbotId }
    });
  }

  startRecording(): void {
    if (!this.currentSession) {
      throw new Error('No active voice session');
    }

    this.currentSession.isRecording = true;
    this.audioChunks = [];

    this.send({
      type: 'audio_start',
      data: {
        session_id: this.currentSession.sessionId,
        format: 'webm',
        sample_rate: 44100
      }
    });
  }

  sendAudioChunk(audioData: Blob): void {
    if (!this.currentSession || !this.currentSession.isRecording) {
      throw new Error('Not currently recording');
    }

    this.audioChunks.push(audioData);

    // Convert Blob to ArrayBuffer and send as binary
    audioData.arrayBuffer().then(arrayBuffer => {
      this.sendBinary(arrayBuffer);
    });
  }

  stopRecording(): void {
    if (!this.currentSession || !this.currentSession.isRecording) {
      return;
    }

    this.currentSession.isRecording = false;

    this.send({
      type: 'audio_stop',
      data: {
        session_id: this.currentSession.sessionId,
        chunk_count: this.audioChunks.length
      }
    });
  }

  sendTextInput(text: string): void {
    if (!this.currentSession) {
      throw new Error('No active voice session');
    }

    this.send({
      type: 'text_input',
      data: {
        session_id: this.currentSession.sessionId,
        content: text
      }
    });
  }

  private async playAudioResponse(audioUrl: string): Promise<void> {
    try {
      const audio = new Audio(audioUrl);
      await audio.play();
    } catch (error) {
      console.error('Failed to play audio response:', error);
    }
  }

  endSession(): void {
    if (this.currentSession) {
      this.send({
        type: 'voice_session_end',
        data: { session_id: this.currentSession.sessionId }
      });
      this.currentSession = null;
    }
  }

  get session(): VoiceSession | null {
    return this.currentSession;
  }

  get isRecording(): boolean {
    return this.currentSession?.isRecording || false;
  }

  get isProcessing(): boolean {
    return this.currentSession?.isProcessing || false;
  }
}