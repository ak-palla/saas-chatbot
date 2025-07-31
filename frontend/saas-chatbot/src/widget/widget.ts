import { WidgetConfig, ChatMessage, ChatbotResponse } from './types';
import { WidgetUtils } from './utils';
import { WidgetWebSocketClient } from './websocket-client';
import { WidgetVoiceHandler } from './voice-handler';

export class AIChatbotWidget {
  private config: WidgetConfig;
  private container: HTMLElement | null = null;
  private chatWindow: HTMLElement | null = null;
  private toggleButton: HTMLElement | null = null;
  private messagesContainer: HTMLElement | null = null;
  private inputField: HTMLInputElement | null = null;
  private sendButton: HTMLElement | null = null;
  private voiceButton: HTMLElement | null = null;
  private voiceIndicator: HTMLElement | null = null;
  
  private isOpen = false;
  private isInitialized = false;
  private messages: ChatMessage[] = [];
  private chatbotConfig: any = null;
  
  private wsClient: WidgetWebSocketClient | null = null;
  private voiceHandler: WidgetVoiceHandler | null = null;
  
  private cssId = 'ai-chatbot-widget-styles';
  private retryAttempts = 0;
  private maxRetryAttempts = 3;

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
      ...config 
    };

    this.init();
  }

  private async init(): Promise<void> {
    try {
      console.log('🚀 Initializing AI Chatbot Widget...');
      
      if (!this.config.chatbotId) {
        throw new Error('Chatbot ID is required');
      }

      // Load chatbot configuration
      await this.loadChatbotConfig();
      
      // Create widget UI
      this.createWidget();
      
      // Set up event listeners
      this.setupEventListeners();
      
      // Initialize WebSocket connection
      await this.initializeWebSocket();
      
      // Initialize voice handler if enabled
      if (this.config.enableVoice && WidgetVoiceHandler.isSupported()) {
        this.initializeVoiceHandler();
      }
      
      // Add initial greeting message
      this.addGreetingMessage();
      
      this.isInitialized = true;
      console.log('✅ AI Chatbot Widget initialized successfully');
      
      // Notify parent window
      WidgetUtils.postMessageToParent({
        type: 'widget_initialized',
        chatbotId: this.config.chatbotId,
      });
      
    } catch (error) {
      console.error('❌ Failed to initialize widget:', error);
      this.handleInitializationError(error as Error);
    }
  }

  private async loadChatbotConfig(): Promise<void> {
    try {
      this.chatbotConfig = await WidgetUtils.loadChatbotConfig(
        this.config.baseUrl!,
        this.config.chatbotId
      );
      
      // Merge chatbot config with widget config
      if (this.chatbotConfig.appearance_config) {
        this.config = {
          ...this.config,
          ...this.chatbotConfig.appearance_config,
        };
      }
    } catch (error) {
      console.warn('⚠️ Could not load chatbot config, using defaults:', error);
      // Continue with default configuration
    }
  }

  private createWidget(): void {
    // Remove existing widget
    this.removeWidget();
    
    // Create container
    this.container = document.createElement('div');
    this.container.id = 'ai-chatbot-widget';
    this.container.innerHTML = this.getWidgetHTML();
    
    // Inject CSS
    this.injectStyles();
    
    // Add to DOM
    document.body.appendChild(this.container);
    
    // Get element references
    this.chatWindow = this.container.querySelector('.chatbot-window');
    this.toggleButton = this.container.querySelector('.chatbot-toggle');
    this.messagesContainer = this.container.querySelector('.chatbot-messages');
    this.inputField = this.container.querySelector('.chatbot-input');
    this.sendButton = this.container.querySelector('.chatbot-send');
    this.voiceButton = this.container.querySelector('.chatbot-voice');
    this.voiceIndicator = this.container.querySelector('.voice-indicator');
  }

  private getWidgetHTML(): string {
    const position = this.config.position || 'bottom-right';
    const isMobile = WidgetUtils.isMobile();
    
    return `
      <div class="chatbot-container chatbot-${position}" style="z-index: ${this.config.zIndex}">
        ${this.getChatWindowHTML()}
        ${this.getToggleButtonHTML()}
      </div>
    `;
  }

  private getChatWindowHTML(): string {
    const maxWidth = WidgetUtils.isMobile() ? '100vw' : `${this.config.maxWidth}px`;
    const maxHeight = WidgetUtils.isMobile() ? '100vh' : `${this.config.maxHeight}px`;
    
    return `
      <div class="chatbot-window" style="max-width: ${maxWidth}; max-height: ${maxHeight}; display: none;">
        ${this.getHeaderHTML()}
        <div class="chatbot-messages"></div>
        ${this.getInputHTML()}
      </div>
    `;
  }

  private getHeaderHTML(): string {
    return `
      <div class="chatbot-header" style="background: ${this.config.primaryColor};">
        <div class="chatbot-header-content">
          ${this.config.showAvatar ? `
            <div class="chatbot-avatar">
              ${this.config.avatarUrl ? 
                `<img src="${this.config.avatarUrl}" alt="Bot Avatar" />` :
                '<div class="avatar-placeholder">🤖</div>'
              }
            </div>
          ` : ''}
          <div class="chatbot-info">
            <div class="chatbot-name">${this.config.botName}</div>
            <div class="chatbot-status">Online</div>
          </div>
        </div>
        <button class="chatbot-close" aria-label="Close chat">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    `;
  }

  private getInputHTML(): string {
    return `
      <div class="chatbot-input-container">
        <div class="input-wrapper">
          <input 
            type="text" 
            class="chatbot-input" 
            placeholder="Type your message..."
            aria-label="Chat message input"
          />
          ${this.config.enableVoice && WidgetVoiceHandler.isSupported() ? `
            <button class="chatbot-voice" aria-label="Voice message" title="Hold to record">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m12 1-3 3v8l3 3 3-3V4l-3-3z"></path>
                <path d="M8 9h1v6H8z"></path>
                <path d="M15 9h1v6h-1z"></path>
              </svg>
              <div class="voice-indicator"></div>
            </button>
          ` : ''}
        </div>
        <button class="chatbot-send" style="background: ${this.config.primaryColor};" aria-label="Send message">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22,2 15,22 11,13 2,9"></polygon>
          </svg>
        </button>
      </div>
    `;
  }

  private getToggleButtonHTML(): string {
    return `
      <button class="chatbot-toggle" style="background: ${this.config.primaryColor};" aria-label="Open chat">
        <svg class="chatbot-icon-chat" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
        </svg>
        <svg class="chatbot-icon-close" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: none;">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    `;
  }

  private injectStyles(): void {
    const css = this.generateCSS();
    WidgetUtils.injectCSS(css, this.cssId);
  }

  private generateCSS(): string {
    const theme = this.config.theme === 'dark' ? 'dark' : 'light';
    const colors = this.getThemeColors(theme);
    
    return `
      /* AI Chatbot Widget Styles */
      #ai-chatbot-widget {
        position: fixed;
        z-index: ${this.config.zIndex};
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        font-size: 14px;
        line-height: 1.5;
        color: ${colors.text};
        --primary-color: ${this.config.primaryColor};
      }

      .chatbot-container {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
      }

      .chatbot-bottom-right { bottom: 20px; right: 20px; }
      .chatbot-bottom-left { bottom: 20px; left: 20px; align-items: flex-start; }
      .chatbot-top-right { top: 20px; right: 20px; }
      .chatbot-top-left { top: 20px; left: 20px; align-items: flex-start; }

      .chatbot-window {
        width: ${this.config.maxWidth}px;
        height: ${this.config.maxHeight}px;
        background: ${colors.background};
        border: 1px solid ${colors.border};
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        display: flex;
        flex-direction: column;
        margin-bottom: 12px;
        animation: slideUp 0.3s ease-out;
        overflow: hidden;
      }

      @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
      }

      .chatbot-header {
        padding: 16px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-height: 60px;
      }

      .chatbot-header-content {
        display: flex;
        align-items: center;
        gap: 12px;
      }

      .chatbot-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
      }

      .chatbot-avatar img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .avatar-placeholder {
        font-size: 18px;
      }

      .chatbot-name {
        font-weight: 600;
        font-size: 15px;
      }

      .chatbot-status {
        font-size: 12px;
        opacity: 0.9;
      }

      .chatbot-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 8px;
        border-radius: 6px;
        transition: background-color 0.2s;
      }

      .chatbot-close:hover {
        background: rgba(255, 255, 255, 0.1);
      }

      .chatbot-messages {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 12px;
        scroll-behavior: smooth;
      }

      .chatbot-message {
        display: flex;
        max-width: 85%;
        animation: messageSlideIn 0.3s ease-out;
      }

      @keyframes messageSlideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }

      .chatbot-message-bot {
        justify-content: flex-start;
      }

      .chatbot-message-user {
        justify-content: flex-end;
        align-self: flex-end;
      }

      .chatbot-message-content {
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.4;
        word-wrap: break-word;
      }

      .chatbot-message-bot .chatbot-message-content {
        background: ${colors.botMessage};
        color: ${colors.botMessageText};
        border-bottom-left-radius: 6px;
      }

      .chatbot-message-user .chatbot-message-content {
        background: var(--primary-color);
        color: white;
        border-bottom-right-radius: 6px;
      }

      .chatbot-input-container {
        padding: 16px;
        border-top: 1px solid ${colors.border};
        background: ${colors.inputBackground};
      }

      .input-wrapper {
        display: flex;
        align-items: center;
        gap: 8px;
        position: relative;
      }

      .chatbot-input {
        flex: 1;
        padding: 12px 16px;
        border: 1px solid ${colors.inputBorder};
        border-radius: 24px;
        font-size: 14px;
        outline: none;
        background: ${colors.inputBackground};
        color: ${colors.text};
        transition: border-color 0.2s;
      }

      .chatbot-input:focus {
        border-color: var(--primary-color);
      }

      .chatbot-voice {
        width: 40px;
        height: 40px;
        border: none;
        border-radius: 50%;
        background: ${colors.voiceButton};
        color: ${colors.voiceButtonText};
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        position: relative;
      }

      .chatbot-voice:hover {
        background: ${colors.voiceButtonHover};
        transform: scale(1.05);
      }

      .chatbot-voice.recording {
        background: #ef4444;
        animation: pulse 1.5s infinite;
      }

      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
      }

      .voice-indicator {
        position: absolute;
        top: -2px;
        right: -2px;
        width: 12px;
        height: 12px;
        background: #10b981;
        border: 2px solid ${colors.background};
        border-radius: 50%;
        display: none;
      }

      .voice-indicator.active {
        display: block;
        animation: voicePulse 1s infinite;
      }

      @keyframes voicePulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }

      .chatbot-send {
        width: 40px;
        height: 40px;
        border: none;
        border-radius: 50%;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
      }

      .chatbot-send:hover {
        transform: scale(1.05);
        filter: brightness(1.1);
      }

      .chatbot-send:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
      }

      .chatbot-toggle {
        width: 56px;
        height: 56px;
        border: none;
        border-radius: 50%;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
      }

      .chatbot-toggle:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.2);
      }

      /* Mobile styles */
      @media (max-width: 768px) {
        .chatbot-window {
          width: 100vw !important;
          height: 100vh !important;
          border-radius: 0 !important;
          margin: 0 !important;
          max-width: none !important;
          max-height: none !important;
        }
        
        .chatbot-container {
          top: 0 !important;
          left: 0 !important;
          right: 0 !important;
          bottom: 0 !important;
          width: 100vw !important;
          height: 100vh !important;
        }

        .chatbot-toggle {
          position: fixed;
          bottom: 20px;
          right: 20px;
        }
      }

      /* Accessibility */
      @media (prefers-reduced-motion: reduce) {
        .chatbot-window,
        .chatbot-message,
        .chatbot-toggle {
          animation: none;
        }
      }

      /* High contrast mode */
      @media (prefers-contrast: high) {
        .chatbot-window {
          border: 2px solid ${colors.text};
        }
        
        .chatbot-input {
          border: 2px solid ${colors.text};
        }
      }
    `;
  }

  private getThemeColors(theme: string) {
    if (theme === 'dark') {
      return {
        background: '#1f2937',
        text: '#f9fafb',
        border: '#374151',
        botMessage: '#374151',
        botMessageText: '#f9fafb',
        inputBackground: '#111827',
        inputBorder: '#4b5563',
        voiceButton: '#4b5563',
        voiceButtonText: '#f9fafb',
        voiceButtonHover: '#6b7280',
      };
    } else {
      return {
        background: '#ffffff',
        text: '#111827',
        border: '#e5e7eb',
        botMessage: '#f3f4f6',
        botMessageText: '#111827',
        inputBackground: '#ffffff',
        inputBorder: '#d1d5db',
        voiceButton: '#f3f4f6',
        voiceButtonText: '#111827',
        voiceButtonHover: '#e5e7eb',
      };
    }
  }

  // ... (continuing in next part due to length)