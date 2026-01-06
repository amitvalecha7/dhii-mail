
export interface KernelState {
  [key: string]: any;
}

export interface KernelAction {
  type: string;
  payload?: any;
}

export interface StreamEvent {
  type: string;
  data: any;
  timestamp: string;
  user_id?: string;
  session_id?: string;
}

export interface StreamOptions {
  onMessage?: (event: StreamEvent) => void;
  onError?: (error: Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

class KernelBridge {
  private baseUrl: string = '/api/a2ui';
  private eventSource: EventSource | null = null;
  private activeStreams: Map<string, EventSource> = new Map();

  async fetchState<T = any>(route: string): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}/${route}`);
      if (!response.ok) {
        throw new Error(`Kernel Error: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Failed to fetch state from ${route}:`, error);
      throw error;
    }
  }

  async sendAction(action: string, payload: any = {}): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/ui/action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action, payload }),
      });
      if (!response.ok) {
        throw new Error(`Action Error: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Failed to send action ${action}:`, error);
      throw error;
    }
  }

  async sendChat(message: string, sessionId?: string): Promise<any> {
     try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, session_id: sessionId }),
      });
      if (!response.ok) {
        throw new Error(`Chat Error: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to send chat message:', error);
      throw error;
    }
  }

  // Server-Sent Events (SSE) Streaming Support
  connectStream(sessionId: string, options: StreamOptions = {}): void {
    try {
      // Close existing stream for this session if any
      this.disconnectStream(sessionId);
      
      const streamUrl = `${this.baseUrl}/stream/${sessionId}`;
      const eventSource = new EventSource(streamUrl);
      
      this.activeStreams.set(sessionId, eventSource);
      
      eventSource.onopen = () => {
        console.log(`SSE stream connected for session: ${sessionId}`);
        options.onConnect?.();
      };
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log(`Received SSE event:`, data);
          
          const streamEvent: StreamEvent = {
            type: data.type || 'unknown',
            data: data,
            timestamp: data.timestamp || new Date().toISOString(),
            user_id: data.user_id,
            session_id: sessionId
          };
          
          options.onMessage?.(streamEvent);
        } catch (error) {
          console.error('Error parsing SSE message:', error);
          options.onError?.(error as Error);
        }
      };
      
      eventSource.onerror = (error) => {
        console.error(`SSE stream error for session ${sessionId}:`, error);
        options.onError?.(error as Error);
        
        // Auto-reconnect after 3 seconds if not manually disconnected
        setTimeout(() => {
          if (this.activeStreams.has(sessionId)) {
            console.log(`Attempting to reconnect SSE stream for session: ${sessionId}`);
            this.connectStream(sessionId, options);
          }
        }, 3000);
      };
      
      console.log(`SSE stream initiated for session: ${sessionId}`);
      
    } catch (error) {
      console.error(`Failed to connect SSE stream for session ${sessionId}:`, error);
      options.onError?.(error as Error);
    }
  }

  disconnectStream(sessionId: string): void {
    const eventSource = this.activeStreams.get(sessionId);
    if (eventSource) {
      eventSource.close();
      this.activeStreams.delete(sessionId);
      console.log(`SSE stream disconnected for session: ${sessionId}`);
    }
  }

  disconnectAllStreams(): void {
    this.activeStreams.forEach((eventSource, sessionId) => {
      eventSource.close();
      console.log(`SSE stream disconnected for session: ${sessionId}`);
    });
    this.activeStreams.clear();
  }

  sendStreamEvent(sessionId: string, eventType: string, data: any): Promise<any> {
    return this.sendAction('stream_event', {
      session_id: sessionId,
      event_type: eventType,
      data: data
    });
  }

  isStreamConnected(sessionId: string): boolean {
    const eventSource = this.activeStreams.get(sessionId);
    return eventSource !== undefined && eventSource.readyState === EventSource.OPEN;
  }

  getActiveStreams(): string[] {
    return Array.from(this.activeStreams.keys());
  }
}

export const kernelBridge = new KernelBridge();
