
export interface KernelState {
  [key: string]: any;
}

export interface KernelAction {
  type: string;
  payload?: any;
}

class KernelBridge {
  private baseUrl: string = '/api/a2ui';

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
}

export const kernelBridge = new KernelBridge();
