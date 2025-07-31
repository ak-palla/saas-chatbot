/**
 * Chatbot SaaS Widget - Main Entry Point
 * Export all widget components for npm distribution
 */

// Main widget class
export { ChatbotWidget } from './chatbot-widget';

// Types
export type {
  WidgetConfig,
  ChatMessage,
  ChatbotResponse,
  VoiceSession,
  VoiceConfig
} from './types';

// Utilities
export { WidgetUtils } from './utils';

// WebSocket client
export { WidgetWebSocketClient } from './websocket-client';

// Voice handler
export { WidgetVoiceHandler } from './voice-handler';

// Default export for UMD builds
import { ChatbotWidget } from './chatbot-widget';
export default ChatbotWidget;

// Global type declarations
declare global {
  interface Window {
    ChatbotSaaS: {
      init: (config: any) => void;
      open: () => void;
      close: () => void;
      toggle: () => void;
      destroy: () => void;
      sendMessage: (message: string) => void;
      addMessage: (content: string, sender: 'user' | 'bot') => void;
    };
    ChatbotWidget: typeof ChatbotWidget;
  }
}