import { createClient } from '@/lib/supabase/client';

export interface WebSocketMessage {
  type: string;
  data?: any;
  error?: string;
}

export interface WebSocketConfig {
  url: string;
  protocols?: string[];
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  timeout?: number;
}

export type WebSocketEventListener = (event: WebSocketMessage) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private listeners: Map<string, WebSocketEventListener[]> = new Map();
  private reconnectCount = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private isReconnecting = false;
  private isClosed = false;

  constructor(config: WebSocketConfig) {
    this.config = {
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      timeout: 30000,
      ...config,
    };
  }

  async connect(token?: string): Promise<void> {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return;
    }

    this.isClosed = false;

    try {
      // Get auth token if not provided
      if (!token) {
        const supabase = createClient();
        const { data: { session } } = await supabase.auth.getSession();
        token = session?.access_token;
      }

      // Build WebSocket URL with token
      const wsUrl = new URL(this.config.url);
      if (token) {
        wsUrl.searchParams.set('token', token);
      }

      this.ws = new WebSocket(wsUrl.toString(), this.config.protocols);

      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
        }, this.config.timeout);

        this.ws!.onopen = () => {
          clearTimeout(timeout);
          this.reconnectCount = 0;
          this.isReconnecting = false;
          this.emit('connected', {});
          resolve();
        };

        this.ws!.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.emit(message.type, message);
            this.emit('message', message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws!.onclose = (event) => {
          clearTimeout(timeout);
          this.emit('disconnected', { code: event.code, reason: event.reason });
          
          if (!this.isClosed && !this.isReconnecting) {
            this.handleReconnect();
          }
        };

        this.ws!.onerror = (error) => {
          clearTimeout(timeout);
          console.error('WebSocket error:', error);
          this.emit('error', { error: 'WebSocket connection error' });
          reject(new Error('WebSocket connection failed'));
        };
      });
    } catch (error) {
      throw new Error(`Failed to connect WebSocket: ${error}`);
    }
  }

  disconnect(): void {
    this.isClosed = true;
    this.clearReconnectTimer();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  send(message: WebSocketMessage): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }

    this.ws.send(JSON.stringify(message));
  }

  sendBinary(data: ArrayBuffer | Blob): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }

    this.ws.send(data);
  }

  on(event: string, listener: WebSocketEventListener): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(listener);
  }

  off(event: string, listener: WebSocketEventListener): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(listener);
      if (index > -1) {
        eventListeners.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(listener => {
        try {
          listener(data);
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error);
        }
      });
    }
  }

  private handleReconnect(): void {
    if (this.isClosed || this.reconnectCount >= this.config.maxReconnectAttempts!) {
      this.emit('reconnect_failed', { attempts: this.reconnectCount });
      return;
    }

    this.isReconnecting = true;
    this.reconnectCount++;

    this.emit('reconnecting', { attempt: this.reconnectCount });

    this.reconnectTimer = setTimeout(async () => {
      try {
        await this.connect();
        this.emit('reconnected', { attempts: this.reconnectCount });
      } catch (error) {
        console.error(`Reconnect attempt ${this.reconnectCount} failed:`, error);
        this.handleReconnect();
      }
    }, this.config.reconnectInterval);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}