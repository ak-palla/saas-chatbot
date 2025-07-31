import { WidgetConfig } from './types';

// Utility functions for the widget

export class WidgetUtils {
  static generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  static sanitizeHtml(html: string): string {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
  }

  static formatTime(date: Date): string {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  static isValidUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  static getScriptConfig(): Partial<WidgetConfig> {
    const scripts = document.getElementsByTagName('script');
    const currentScript = scripts[scripts.length - 1];
    
    if (!currentScript) return {};

    return {
      chatbotId: currentScript.getAttribute('data-chatbot-id') || '',
      baseUrl: currentScript.getAttribute('data-base-url') || undefined,
      theme: currentScript.getAttribute('data-theme') as any || 'light',
      position: currentScript.getAttribute('data-position') as any || 'bottom-right',
      primaryColor: currentScript.getAttribute('data-primary-color') || '#3b82f6',
      greeting: currentScript.getAttribute('data-greeting') || undefined,
      botName: currentScript.getAttribute('data-bot-name') || undefined,
      enableVoice: currentScript.getAttribute('data-enable-voice') === 'true',
      maxWidth: parseInt(currentScript.getAttribute('data-max-width') || '400'),
      maxHeight: parseInt(currentScript.getAttribute('data-max-height') || '600'),
      zIndex: parseInt(currentScript.getAttribute('data-z-index') || '999999'),
    };
  }

  static isMobile(): boolean {
    return window.innerWidth <= 768;
  }

  static debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  }

  static async loadChatbotConfig(baseUrl: string, chatbotId: string): Promise<any> {
    const response = await fetch(`${baseUrl}/api/v1/chatbots/${chatbotId}/public`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to load chatbot config: ${response.status}`);
    }

    return response.json();
  }

  static createCSSRule(selector: string, styles: Record<string, string>): string {
    const styleString = Object.entries(styles)
      .map(([property, value]) => `${property}: ${value}`)
      .join('; ');
    
    return `${selector} { ${styleString} }`;
  }

  static injectCSS(css: string, id?: string): HTMLStyleElement {
    const style = document.createElement('style');
    if (id) style.id = id;
    style.textContent = css;
    document.head.appendChild(style);
    return style;
  }

  static removeCSS(id: string): void {
    const style = document.getElementById(id);
    if (style) {
      style.remove();
    }
  }

  static postMessageToParent(data: any): void {
    if (window.parent !== window) {
      window.parent.postMessage(data, '*');
    }
  }

  static isWebSocketSupported(): boolean {
    return 'WebSocket' in window;
  }

  static isAudioSupported(): boolean {
    return 'AudioContext' in window || 'webkitAudioContext' in window;
  }

  static isMicrophoneSupported(): boolean {
    return navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
  }
}