import { App, Plugin } from 'vue';
import ChatbotWidget from './components/ChatbotWidget.vue';
import ChatbotTrigger from './components/ChatbotTrigger.vue';
import ChatbotStatus from './components/ChatbotStatus.vue';
import { useChatbot, createChatbotStore } from './composables/useChatbot';

// Types
export interface ChatbotConfig {
  chatbotId: string;
  baseUrl?: string;
  theme?: 'light' | 'dark' | 'auto';
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  primaryColor?: string;
  secondaryColor?: string;
  borderRadius?: number;
  autoOpen?: boolean;
  autoOpenDelay?: number;
  showAvatar?: boolean;
  enableSound?: boolean;
  enableTypingIndicator?: boolean;
  enableFileUpload?: boolean;
  enableVoice?: boolean;
  maxWidth?: number;
  maxHeight?: number;
  mobileFullScreen?: boolean;
  zIndex?: number;
  customCss?: string;
}

export interface ChatbotEvents {
  onOpen?: () => void;
  onClose?: () => void;
  onMessage?: (message: string) => void;
  onError?: (error: Error) => void;
}

export interface ChatbotState {
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;
  messages: Array<{
    id: string;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
  }>;
}

// Plugin installation
const ChatbotSaaSPlugin: Plugin = {
  install(app: App, options?: { globalConfig?: ChatbotConfig }) {
    // Register components globally
    app.component('ChatbotWidget', ChatbotWidget);
    app.component('ChatbotTrigger', ChatbotTrigger);
    app.component('ChatbotStatus', ChatbotStatus);

    // Provide global configuration if specified
    if (options?.globalConfig) {
      app.provide('chatbot-global-config', options.globalConfig);
    }

    // Add global properties
    app.config.globalProperties.$chatbot = {
      createStore: createChatbotStore,
    };
  },
};

// Export everything
export {
  ChatbotWidget,
  ChatbotTrigger,
  ChatbotStatus,
  useChatbot,
  createChatbotStore,
  ChatbotSaaSPlugin,
};

export type {
  ChatbotConfig,
  ChatbotEvents,
  ChatbotState,
};

// Default export for plugin installation
export default ChatbotSaaSPlugin;
