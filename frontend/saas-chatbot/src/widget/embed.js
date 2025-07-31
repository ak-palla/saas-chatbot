/**
 * Chatbot SaaS Embeddable Widget
 * Production-ready embed script for customer websites
 */

(function(window, document) {
  'use strict';

  // Widget configuration defaults
  const DEFAULT_CONFIG = {
    baseUrl: 'https://api.yourchatbot.com',
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
    autoOpen: false,
    welcomeMessage: true
  };

  // Widget state
  let widgetInstance = null;
  let isLoaded = false;
  let config = {};

  /**
   * Load external script
   */
  function loadScript(src, callback) {
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.async = true;
    script.src = src;
    script.onload = callback;
    document.head.appendChild(script);
  }

  /**
   * Initialize the widget
   */
  function initWidget(options = {}) {
    if (isLoaded) {
      console.warn('Chatbot widget already loaded');
      return;
    }

    // Merge configuration
    config = { ...DEFAULT_CONFIG, ...options };

    // Validate required configuration
    if (!config.chatbotId) {
      console.error('❌ chatbotId is required');
      return;
    }

    // Load widget dependencies
    loadWidgetDependencies(() => {
      createWidget();
      isLoaded = true;
      console.log('🤖 Chatbot widget loaded successfully');
    });
  }

  /**
   * Load required dependencies
   */
  function loadWidgetDependencies(callback) {
    const dependencies = [
      'https://cdn.jsdelivr.net/npm/@chatbot-saas/widget@latest/dist/widget.min.js'
    ];

    let loaded = 0;
    dependencies.forEach(src => {
      loadScript(src, () => {
        loaded++;
        if (loaded === dependencies.length) {
          callback();
        }
      });
    });
  }

  /**
   * Create widget instance
   */
  function createWidget() {
    if (window.ChatbotWidget) {
      widgetInstance = new window.ChatbotWidget(config);
      
      // Auto-open if configured
      if (config.autoOpen) {
        setTimeout(() => {
          widgetInstance.open();
        }, 1000);
      }
    } else {
      console.error('❌ ChatbotWidget not found');
    }
  }

  /**
   * Public API methods
   */
  window.ChatbotSaaS = {
    init: initWidget,
    open: () => widgetInstance?.open(),
    close: () => widgetInstance?.close(),
    toggle: () => widgetInstance?.toggle(),
    destroy: () => {
      if (widgetInstance) {
        widgetInstance.destroy();
        widgetInstance = null;
        isLoaded = false;
      }
    },
    sendMessage: (message) => widgetInstance?.sendMessage?.(message),
    addMessage: (content, sender) => widgetInstance?.addMessage?.(content, sender)
  };

  // Auto-initialization if data attributes are present
  document.addEventListener('DOMContentLoaded', () => {
    const script = document.currentScript || document.querySelector('script[src*="embed.js"]');
    if (script) {
      const dataset = script.dataset;
      if (dataset.chatbotId) {
        initWidget({
          chatbotId: dataset.chatbotId,
          baseUrl: dataset.baseUrl || DEFAULT_CONFIG.baseUrl,
          theme: dataset.theme || DEFAULT_CONFIG.theme,
          position: dataset.position || DEFAULT_CONFIG.position,
          primaryColor: dataset.primaryColor || DEFAULT_CONFIG.primaryColor,
          greeting: dataset.greeting || DEFAULT_CONFIG.greeting,
          botName: dataset.botName || DEFAULT_CONFIG.botName,
          enableVoice: dataset.enableVoice === 'true',
          autoOpen: dataset.autoOpen === 'true'
        });
      }
    }
  });

})(window, document);