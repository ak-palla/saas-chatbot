import React, { useEffect, useRef, useState, useCallback } from 'react';
import clsx from 'clsx';

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
  onOpen?: () => void;
  onClose?: () => void;
  onMessage?: (message: string) => void;
  onError?: (error: Error) => void;
}

export interface ChatbotWidgetProps extends ChatbotConfig {
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}

export interface ChatbotContextType {
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;
  open: () => void;
  close: () => void;
  sendMessage: (message: string) => void;
  config: ChatbotConfig;
}

// Context
const ChatbotContext = React.createContext<ChatbotContextType | null>(null);

export const useChatbot = () => {
  const context = React.useContext(ChatbotContext);
  if (!context) {
    throw new Error('useChatbot must be used within a ChatbotProvider');
  }
  return context;
};

// Default configuration
const defaultConfig: Partial<ChatbotConfig> = {
  baseUrl: 'https://api.yourchatbot.com',
  theme: 'light',
  position: 'bottom-right',
  primaryColor: '#3b82f6',
  secondaryColor: '#1f2937',
  borderRadius: 12,
  autoOpen: false,
  autoOpenDelay: 3000,
  showAvatar: true,
  enableSound: true,
  enableTypingIndicator: true,
  enableFileUpload: false,
  enableVoice: false,
  maxWidth: 400,
  maxHeight: 600,
  mobileFullScreen: true,
  zIndex: 999999,
};

// Widget component
export const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({
  className,
  style,
  children,
  onOpen,
  onClose,
  onMessage,
  onError,
  ...configProps
}) => {
  const widgetRef = useRef<HTMLDivElement>(null);
  const scriptRef = useRef<HTMLScriptElement | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [widgetInstance, setWidgetInstance] = useState<any>(null);

  // Merge configuration with defaults
  const config: ChatbotConfig = {
    ...defaultConfig,
    ...configProps,
  } as ChatbotConfig;

  // Load widget script
  const loadWidgetScript = useCallback(async () => {
    if (!config.chatbotId) {
      setError('Chatbot ID is required');
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Remove existing script if any
      if (scriptRef.current) {
        document.head.removeChild(scriptRef.current);
      }

      // Create and load new script
      const script = document.createElement('script');
      script.src = `${config.baseUrl}/widget/embed.js`;
      script.async = true;
      
      script.onload = () => {
        // Initialize widget
        if (typeof (window as any).ChatbotSaaS !== 'undefined') {
          const instance = (window as any).ChatbotSaaS.init({
            ...config,
            container: widgetRef.current,
            onOpen: () => {
              setIsOpen(true);
              onOpen?.();
            },
            onClose: () => {
              setIsOpen(false);
              onClose?.();
            },
            onMessage: (message: string) => {
              onMessage?.(message);
            },
            onError: (err: Error) => {
              setError(err.message);
              onError?.(err);
            },
          });
          
          setWidgetInstance(instance);
          setIsLoading(false);
        } else {
          throw new Error('ChatbotSaaS library not found');
        }
      };

      script.onerror = () => {
        setError('Failed to load chatbot widget');
        setIsLoading(false);
      };

      scriptRef.current = script;
      document.head.appendChild(script);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      setIsLoading(false);
    }
  }, [config, onOpen, onClose, onMessage, onError]);

  // Initialize widget on mount
  useEffect(() => {
    loadWidgetScript();

    // Cleanup on unmount
    return () => {
      if (scriptRef.current) {
        document.head.removeChild(scriptRef.current);
      }
      if (widgetInstance) {
        widgetInstance.destroy?.();
      }
    };
  }, [loadWidgetScript]);

  // Widget control functions
  const openWidget = useCallback(() => {
    if (widgetInstance) {
      widgetInstance.open();
    }
  }, [widgetInstance]);

  const closeWidget = useCallback(() => {
    if (widgetInstance) {
      widgetInstance.close();
    }
  }, [widgetInstance]);

  const sendMessage = useCallback((message: string) => {
    if (widgetInstance) {
      widgetInstance.sendMessage(message);
    }
  }, [widgetInstance]);

  // Context value
  const contextValue: ChatbotContextType = {
    isOpen,
    isLoading,
    error,
    open: openWidget,
    close: closeWidget,
    sendMessage,
    config,
  };

  // Render loading state
  if (isLoading) {
    return (
      <div 
        className={clsx('chatbot-widget-loading', className)}
        style={style}
      >
        {children || (
          <div className="chatbot-loading-spinner">
            <div className="spinner"></div>
            <span>Loading chatbot...</span>
          </div>
        )}
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div 
        className={clsx('chatbot-widget-error', className)}
        style={style}
      >
        {children || (
          <div className="chatbot-error-message">
            <span>Failed to load chatbot: {error}</span>
            <button onClick={loadWidgetScript}>Retry</button>
          </div>
        )}
      </div>
    );
  }

  // Render widget
  return (
    <ChatbotContext.Provider value={contextValue}>
      <div 
        ref={widgetRef}
        className={clsx('chatbot-widget-container', className)}
        style={style}
      >
        {children}
      </div>
    </ChatbotContext.Provider>
  );
};

// Provider component for multiple widgets or global state
export interface ChatbotProviderProps {
  config: ChatbotConfig;
  children: React.ReactNode;
}

export const ChatbotProvider: React.FC<ChatbotProviderProps> = ({
  config,
  children,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [widgetInstance, setWidgetInstance] = useState<any>(null);

  const open = useCallback(() => {
    if (widgetInstance) {
      widgetInstance.open();
      setIsOpen(true);
    }
  }, [widgetInstance]);

  const close = useCallback(() => {
    if (widgetInstance) {
      widgetInstance.close();
      setIsOpen(false);
    }
  }, [widgetInstance]);

  const sendMessage = useCallback((message: string) => {
    if (widgetInstance) {
      widgetInstance.sendMessage(message);
    }
  }, [widgetInstance]);

  const contextValue: ChatbotContextType = {
    isOpen,
    isLoading,
    error,
    open,
    close,
    sendMessage,
    config,
  };

  return (
    <ChatbotContext.Provider value={contextValue}>
      {children}
    </ChatbotContext.Provider>
  );
};

// Hook for programmatic control
export const useChatbotControl = () => {
  const { open, close, sendMessage, isOpen } = useChatbot();
  
  return {
    openChatbot: open,
    closeChatbot: close,
    sendMessage,
    isOpen,
  };
};

// Trigger component for custom buttons
export interface ChatbotTriggerProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

export const ChatbotTrigger: React.FC<ChatbotTriggerProps> = ({
  children,
  className,
  style,
  onClick,
}) => {
  const { open } = useChatbot();

  const handleClick = () => {
    open();
    onClick?.();
  };

  return (
    <button
      className={clsx('chatbot-trigger', className)}
      style={style}
      onClick={handleClick}
      type="button"
    >
      {children}
    </button>
  );
};

// Status component
export interface ChatbotStatusProps {
  className?: string;
  style?: React.CSSProperties;
}

export const ChatbotStatus: React.FC<ChatbotStatusProps> = ({
  className,
  style,
}) => {
  const { isLoading, error, isOpen } = useChatbot();

  let status = 'ready';
  let message = 'Chatbot is ready';

  if (isLoading) {
    status = 'loading';
    message = 'Loading chatbot...';
  } else if (error) {
    status = 'error';
    message = `Error: ${error}`;
  } else if (isOpen) {
    status = 'open';
    message = 'Chatbot is open';
  }

  return (
    <div 
      className={clsx('chatbot-status', `chatbot-status-${status}`, className)}
      style={style}
    >
      <span className="chatbot-status-indicator"></span>
      <span className="chatbot-status-message">{message}</span>
    </div>
  );
};

// Export all components and types
export default ChatbotWidget;

export type {
  ChatbotConfig,
  ChatbotWidgetProps,
  ChatbotContextType,
  ChatbotProviderProps,
  ChatbotTriggerProps,
  ChatbotStatusProps,
};
