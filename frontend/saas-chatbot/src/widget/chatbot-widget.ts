import { WidgetConfig, ChatMessage, ChatbotResponse } from './types';
import { WidgetUtils } from './utils';
import { WidgetWebSocketClient } from './websocket-client';
import { WidgetVoiceHandler } from './voice-handler';

export class ChatbotWidget {
  private config: WidgetConfig;
  private container: HTMLElement | null = null;
  private chatWindow: HTMLElement | null = null;
  private toggleButton: HTMLElement | null = null;
  private messagesContainer: HTMLElement | null = null;
  private inputField: HTMLInputElement | null = null;
  private isOpen = false;
  private isLoaded = false;
  private messages: ChatMessage[] = [];
  private websocketClient: WidgetWebSocketClient | null = null;
  private voiceHandler: WidgetVoiceHandler | null = null;
  private chatbotConfig: any = null;
  private stylesInjected = false;
  private audioLevelElement: HTMLElement | null = null;

  constructor(config: WidgetConfig) {
    this.config = {
      baseUrl: 'http://localhost:8000',
      theme: 'light',
      position: 'bottom-right',
      primaryColor: '#3b82f6',
      greeting: 'Hello! How can I help you today?',
      botName: 'Assistant',
      showAvatar: true,
      enableVoice: false,
      maxWidth: 400,
      maxHeight: 600,
      zIndex: 999999,
      ...config,
    };

    this.init();
  }

  async init(): Promise<void> {
    try {
      await this.loadChatbotConfig();
      this.injectStyles();
      this.createWidget();
      this.setupEventListeners();
      
      if (this.config.enableVoice) {
        this.setupVoice();
      }
      
      this.isLoaded = true;
      console.log('🤖 Chatbot widget initialized successfully');
    } catch (error) {
      console.error('❌ Error initializing widget:', error);
      this.showError('Failed to load chatbot');
    }
  }

  private async loadChatbotConfig(): Promise<void> {
    try {
      const config = await WidgetUtils.loadChatbotConfig(this.config.baseUrl!, this.config.chatbotId);
      this.chatbotConfig = config;
      
      // Merge with provided config
      if (config.appearance_config) {
        this.config = { ...this.config, ...config.appearance_config };
      }
      
      if (config.behavior_config) {
        this.config.botName = config.behavior_config.botName || this.config.botName;
        this.config.greeting = config.behavior_config.greetingMessage || this.config.greeting;
      }
    } catch (error) {
      console.warn('⚠️ Could not load chatbot config, using defaults:', error);
    }
  }

  private injectStyles(): void {
    if (this.stylesInjected) return;

    const styles = `
      /* Chatbot Widget Styles */
      .chatbot-widget-container {
        position: fixed;
        ${this.getPositionStyles()}
        z-index: ${this.config.zIndex};
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }

      .chatbot-toggle-button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: ${this.config.primaryColor};
        color: white;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
      }

      .chatbot-toggle-button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
      }

      .chatbot-window {
        position: absolute;
        bottom: 80px;
        right: 0;
        width: ${this.config.maxWidth}px;
        height: ${this.config.maxHeight}px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        display: none;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid #e5e7eb;
      }

      .chatbot-window.open {
        display: flex;
      }

      .chatbot-header {
        background: ${this.config.primaryColor};
        color: white;
        padding: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }

      .chatbot-header h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }

      .chatbot-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 4px;
      }

      .chatbot-messages {
        flex: 1;
        padding: 16px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .chatbot-message {
        display: flex;
        align-items: flex-start;
        gap: 8px;
      }

      .chatbot-message.user {
        flex-direction: row-reverse;
      }

      .chatbot-message-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: ${this.config.primaryColor};
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 12px;
        font-weight: bold;
      }

      .chatbot-message-content {
        max-width: 80%;
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.4;
        word-wrap: break-word;
      }

      .chatbot-message.user .chatbot-message-content {
        background: ${this.config.primaryColor};
        color: white;
        border-bottom-right-radius: 4px;
      }

      .chatbot-message.bot .chatbot-message-content {
        background: #f3f4f6;
        color: #1f2937;
        border-bottom-left-radius: 4px;
      }

      .chatbot-input-container {
        padding: 16px;
        border-top: 1px solid #e5e7eb;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .chatbot-input {
        flex: 1;
        padding: 8px 12px;
        border: 1px solid #d1d5db;
        border-radius: 20px;
        font-size: 14px;
        outline: none;
      }

      .chatbot-input:focus {
        border-color: ${this.config.primaryColor};
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
      }

      .chatbot-send-button,
      .chatbot-voice-button {
        padding: 8px;
        border: none;
        background: ${this.config.primaryColor};
        color: white;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background-color 0.2s;
      }

      .chatbot-send-button:hover,
      .chatbot-voice-button:hover {
        background: ${this.config.primaryColor}dd;
      }

      .chatbot-voice-button.recording {
        background: #ef4444;
        animation: pulse 1s infinite;
      }

      @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
      }

      .chatbot-audio-level {
        height: 4px;
        background: #f3f4f6;
        border-radius: 2px;
        overflow: hidden;
        margin-top: 8px;
      }

      .chatbot-audio-level-bar {
        height: 100%;
        background: ${this.config.primaryColor};
        width: 0%;
        transition: width 0.1s ease;
      }

      /* Responsive design */
      @media (max-width: 768px) {
        .chatbot-widget-container {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          margin: 0;
          width: 100%;
          height: 100%;
          border-radius: 0;
        }

        .chatbot-window {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          width: 100%;
          height: 100%;
          max-width: none;
          max-height: none;
          border-radius: 0;
        }

        .chatbot-toggle-button {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 999999;
        }
      }
    `;

    WidgetUtils.injectCSS(styles, 'chatbot-widget-styles');
    this.stylesInjected = true;
  }

  private getPositionStyles(): string {
    const positions = {
      'bottom-right': 'bottom: 20px; right: 20px;',
      'bottom-left': 'bottom: 20px; left: 20px;',
      'top-right': 'top: 20px; right: 20px;',
      'top-left': 'top: 20px; left: 20px;',
    };

    return positions[this.config.position] || positions['bottom-right'];
  }

  private createWidget(): void {
    // Create container
    this.container = document.createElement('div');
    this.container.className = 'chatbot-widget-container';

    // Create toggle button
    this.toggleButton = document.createElement('button');
    this.toggleButton.className = 'chatbot-toggle-button';
    this.toggleButton.innerHTML = '🤖';

    // Create chat window
    this.chatWindow = document.createElement('div');
    this.chatWindow.className = 'chatbot-window';
    this.chatWindow.innerHTML = `
      <div class="chatbot-header">
        <h3>${this.config.botName}</h3>
        <button class="chatbot-close">×</button>
      </div>
      <div class="chatbot-messages">
        <div class="chatbot-message bot">
          <div class="chatbot-message-avatar">🤖</div>
          <div class="chatbot-message-content">${this.config.greeting}</div>
        </div>
      </div>
      <div class="chatbot-input-container">
        <input type="text" class="chatbot-input" placeholder="Type your message..." />
        ${this.config.enableVoice ? '<button class="chatbot-voice-button" title="Voice message">🎤</button>' : ''}
        <button class="chatbot-send-button" title="Send message">➤</button>
      </div>
      ${this.config.enableVoice ? '<div class="chatbot-audio-level"><div class="chatbot-audio-level-bar"></div></div>' : ''}
    `;

    // Get references to elements
    this.messagesContainer = this.chatWindow.querySelector('.chatbot-messages')!;
    this.inputField = this.chatWindow.querySelector('.chatbot-input')!;

    // Append to body
    document.body.appendChild(this.container);
    this.container.appendChild(this.toggleButton);
    this.container.appendChild(this.chatWindow);
  }

  private setupEventListeners(): void {
    // Toggle button
    this.toggleButton?.addEventListener('click', () => this.toggle());

    // Close button
    this.chatWindow?.querySelector('.chatbot-close')?.addEventListener('click', () => this.close());

    // Input field
    this.inputField?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Send button
    this.chatWindow?.querySelector('.chatbot-send-button')?.addEventListener('click', () => this.sendMessage());

    // Voice button
    if (this.config.enableVoice) {
      this.setupVoiceEvents();
    }
  }

  private setupVoice(): void {
    if (!WidgetVoiceHandler.isSupported()) {
      console.warn('⚠️ Voice features not supported in this browser');
      return;
    }

    this.voiceHandler = new WidgetVoiceHandler(
      (session) => {
        this.updateVoiceUI(session);
      },
      (error) => {
        console.error('❌ Voice error:', error);
        this.showError('Voice feature not available');
      }
    );
  }

  private setupVoiceEvents(): void {
    const voiceButton = this.chatWindow?.querySelector('.chatbot-voice-button');
    if (!voiceButton || !this.voiceHandler) return;

    let isRecording = false;

    voiceButton.addEventListener('click', async () => {
      if (isRecording) {
        // Stop recording
        const audioBlob = await this.voiceHandler?.stopRecording();
        if (audioBlob) {
          await this.sendVoiceMessage(audioBlob);
        }
        isRecording = false;
        voiceButton.classList.remove('recording');
      } else {
        // Start recording
        const success = await this.voiceHandler?.startRecording();
        if (success) {
          isRecording = true;
          voiceButton.classList.add('recording');
          this.startAudioLevelMonitoring();
        }
      }
    });
  }

  private startAudioLevelMonitoring(): void {
    if (!this.voiceHandler) return;

    const levelBar = this.chatWindow?.querySelector('.chatbot-audio-level-bar');
    if (!levelBar) return;

    const updateLevel = () => {
      if (this.voiceHandler?.isRecording()) {
        const level = this.voiceHandler.getAudioLevel();
        levelBar.style.width = `${level * 100}%`;
        requestAnimationFrame(updateLevel);
      } else {
        levelBar.style.width = '0%';
      }
    };

    updateLevel();
  }

  private updateVoiceUI(session: any): void {
    const voiceButton = this.chatWindow?.querySelector('.chatbot-voice-button');
    const levelBar = this.chatWindow?.querySelector('.chatbot-audio-level-bar');

    if (voiceButton) {
      voiceButton.classList.toggle('recording', session.isRecording);
    }

    if (levelBar && session.isRecording) {
      const level = this.voiceHandler?.getAudioLevel() || 0;
      levelBar.style.width = `${level * 100}%`;
    }
  }

  private async sendMessage(): Promise<void> {
    if (!this.inputField || !this.inputField.value.trim()) return;

    const message = this.inputField.value.trim();
    this.addMessage(message, 'user');
    this.inputField.value = '';

    try {
      const response = await fetch(`${this.config.baseUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          chatbot_id: this.config.chatbotId,
          session_id: this.sessionId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        this.addMessage(data.message, 'bot');
      } else {
        this.addMessage('Sorry, I\'m having trouble responding right now.', 'bot');
      }
    } catch (error) {
      console.error('❌ Error sending message:', error);
      this.addMessage('Sorry, I\'m having trouble connecting.', 'bot');
    }
  }

  private async sendVoiceMessage(audioBlob: Blob): Promise<void> {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('chatbot_id', this.config.chatbotId);

      const response = await fetch(`${this.config.baseUrl}/api/v1/voice/process`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        this.addMessage(data.message, 'bot');
        
        if (data.audio_url) {
          await this.voiceHandler?.playAudio(data.audio_url);
        }
      } else {
        this.addMessage('Sorry, I couldn\'t understand your voice message.', 'bot');
      }
    } catch (error) {
      console.error('❌ Error processing voice message:', error);
      this.addMessage('Sorry, I\'m having trouble processing your voice message.', 'bot');
    }
  }

  addMessage(content: string, sender: 'user' | 'bot', metadata?: any): void {
    const message: ChatMessage = {
      id: WidgetUtils.generateId(),
      content,
      sender,
      timestamp: new Date(),
      metadata,
    };

    this.messages.push(message);
    this.renderMessage(message);
  }

  private renderMessage(message: ChatMessage): void {
    if (!this.messagesContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chatbot-message chatbot-message-${message.sender}`;
    
    const avatar = this.config.showAvatar 
      ? `<div class="chatbot-message-avatar">${message.sender === 'bot' ? '🤖' : '👤'}</div>`
      : '';

    messageDiv.innerHTML = `
      ${avatar}
      <div class="chatbot-message-content">${this.sanitizeContent(message.content)}</div>
    `;

    this.messagesContainer.appendChild(messageDiv);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  private sanitizeContent(content: string): string {
    return WidgetUtils.sanitizeHtml(content);
  }

  toggle(): void {
    this.isOpen = !this.isOpen;
    this.chatWindow?.classList.toggle('open', this.isOpen);
  }

  open(): void {
    this.isOpen = true;
    this.chatWindow?.classList.add('open');
  }

  close(): void {
    this.isOpen = false;
    this.chatWindow?.classList.remove('open');
  }

  get sessionId(): string {
    return this.config.chatbotId;
  }

  destroy(): void {
    this.voiceHandler?.cleanup();
    this.container?.remove();
    WidgetUtils.removeCSS('chatbot-widget-styles');
  }
}