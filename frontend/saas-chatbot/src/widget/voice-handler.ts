import { VoiceSession } from './types';
import { WidgetUtils } from './utils';

export class WidgetVoiceHandler {
  private session: VoiceSession;
  private onStateChange?: (session: VoiceSession) => void;
  private onError?: (error: Error) => void;
  private audioLevel = 0;
  private analyserNode?: AnalyserNode;
  private animationFrame?: number;

  constructor(
    onStateChange?: (session: VoiceSession) => void,
    onError?: (error: Error) => void
  ) {
    this.session = {
      sessionId: WidgetUtils.generateId(),
      isRecording: false,
      isPlaying: false,
      audioChunks: [],
    };
    this.onStateChange = onStateChange;
    this.onError = onError;
  }

  async startRecording(): Promise<boolean> {
    try {
      if (!WidgetUtils.isMicrophoneSupported()) {
        throw new Error('Microphone not supported in this browser');
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      // Set up audio context for visualization
      this.session.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const source = this.session.audioContext.createMediaStreamSource(stream);
      this.analyserNode = this.session.audioContext.createAnalyser();
      this.analyserNode.fftSize = 256;
      source.connect(this.analyserNode);

      // Set up media recorder
      this.session.mediaRecorder = new MediaRecorder(stream, {
        mimeType: this.getSupportedMimeType(),
      });

      this.session.audioChunks = [];

      this.session.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.session.audioChunks.push(event.data);
        }
      };

      this.session.mediaRecorder.onstop = () => {
        stream.getTracks().forEach(track => track.stop());
        this.stopAudioLevelMonitoring();
      };

      this.session.mediaRecorder.start(250); // Collect data every 250ms
      this.session.isRecording = true;
      this.startAudioLevelMonitoring();
      
      this.notifyStateChange();
      return true;
    } catch (error) {
      console.error('❌ Error starting recording:', error);
      this.handleError(error as Error);
      return false;
    }
  }

  stopRecording(): Promise<Blob | null> {
    return new Promise((resolve) => {
      if (!this.session.mediaRecorder || !this.session.isRecording) {
        resolve(null);
        return;
      }

      this.session.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.session.audioChunks, {
          type: this.getSupportedMimeType(),
        });
        
        this.session.isRecording = false;
        this.session.audioChunks = [];
        this.stopAudioLevelMonitoring();
        
        this.notifyStateChange();
        resolve(audioBlob);
      };

      this.session.mediaRecorder.stop();
    });
  }

  async playAudio(audioSrc: string): Promise<boolean> {
    try {
      const audio = new Audio(audioSrc);
      
      audio.onplay = () => {
        this.session.isPlaying = true;
        this.notifyStateChange();
      };

      audio.onended = () => {
        this.session.isPlaying = false;
        this.notifyStateChange();
      };

      audio.onerror = (error) => {
        this.session.isPlaying = false;
        this.notifyStateChange();
        this.handleError(new Error('Failed to play audio'));
      };

      await audio.play();
      return true;
    } catch (error) {
      console.error('❌ Error playing audio:', error);
      this.handleError(error as Error);
      return false;
    }
  }

  private getSupportedMimeType(): string {
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/mpeg',
    ];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }

    return 'audio/webm'; // fallback
  }

  private startAudioLevelMonitoring(): void {
    if (!this.analyserNode) return;

    const bufferLength = this.analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const updateLevel = () => {
      if (!this.session.isRecording || !this.analyserNode) {
        return;
      }

      this.analyserNode.getByteFrequencyData(dataArray);
      
      // Calculate RMS level
      let sum = 0;
      for (let i = 0; i < bufferLength; i++) {
        sum += dataArray[i] * dataArray[i];
      }
      
      this.audioLevel = Math.sqrt(sum / bufferLength) / 255;
      this.animationFrame = requestAnimationFrame(updateLevel);
    };

    updateLevel();
  }

  private stopAudioLevelMonitoring(): void {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = undefined;
    }
    this.audioLevel = 0;
  }

  private notifyStateChange(): void {
    if (this.onStateChange) {
      this.onStateChange(this.session);
    }
  }

  private handleError(error: Error): void {
    if (this.onError) {
      this.onError(error);
    }
  }

  getAudioLevel(): number {
    return this.audioLevel;
  }

  getSession(): VoiceSession {
    return { ...this.session };
  }

  isRecording(): boolean {
    return this.session.isRecording;
  }

  isPlaying(): boolean {
    return this.session.isPlaying;
  }

  cleanup(): void {
    if (this.session.isRecording) {
      this.stopRecording();
    }
    
    this.stopAudioLevelMonitoring();
    
    if (this.session.audioContext) {
      this.session.audioContext.close();
    }
  }

  static isSupported(): boolean {
    return WidgetUtils.isAudioSupported() && WidgetUtils.isMicrophoneSupported();
  }
}