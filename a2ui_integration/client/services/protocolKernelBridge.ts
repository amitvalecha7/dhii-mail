/**
 * Protocol-Aware Kernel Bridge
 * Handles JSON protocol communication with Python backend
 * Tenant-agnostic, stateless protocol layer
 */

import { OrchestratorOutput, AdjacencyList } from '../types/protocol';

export interface ProtocolOptions {
  tenantId?: string;
  userId?: string;
  sessionId?: string;
  onStream?: (output: OrchestratorOutput) => void;
  onError?: (error: ProtocolError) => void;
}

export interface ProtocolError {
  code: string;
  message: string;
  details?: any;
  requestId?: string;
}

export interface ProtocolRequest {
  action: string;
  payload?: any;
  tenant_id: string;
  user_id: string;
  request_id?: string;
}

class ProtocolKernelBridge {
  private baseUrl: string = '/api/a2ui';
  private options: ProtocolOptions;

  constructor(options: ProtocolOptions = {}) {
    this.options = options;
  }

  /**
   * Fetch orchestrator output using JSON protocol
   * Returns complete orchestrator output envelope with chunks
   */
  async fetchOrchestratorOutput(route: string, params: Record<string, any> = {}): Promise<OrchestratorOutput> {
    try {
      const request: ProtocolRequest = {
        action: route,
        payload: params,
        tenant_id: this.options.tenantId || 'default',
        user_id: this.options.userId || 'default',
        request_id: this.generateRequestId()
      };

      const response = await fetch(`${this.baseUrl}/protocol/orchestrator`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': request.tenant_id,
          'X-User-ID': request.user_id,
          'X-Request-ID': request.request_id
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`Protocol Error: ${response.statusText}`);
      }

      const output = await response.json() as OrchestratorOutput;
      
      // Validate orchestrator output format
      this.validateOrchestratorOutput(output);
      
      return output;
    } catch (error) {
      const protocolError: ProtocolError = {
        code: 'FETCH_FAILED',
        message: error instanceof Error ? error.message : 'Unknown error',
        details: error
      };
      
      this.options.onError?.(protocolError);
      throw protocolError;
    }
  }

  /**
   * Stream orchestrator output for real-time updates
   */
  async streamOrchestratorOutput(route: string, params: Record<string, any> = {}): Promise<void> {
    const requestId = this.generateRequestId();
    const tenantId = this.options.tenantId || 'default';
    const userId = this.options.userId || 'default';

    const eventSource = new EventSource(
      `${this.baseUrl}/protocol/stream?` + new URLSearchParams({
        action: route,
        tenant_id: tenantId,
        user_id: userId,
        request_id: requestId,
        ...params
      })
    );

    eventSource.onmessage = (event) => {
      try {
        const output = JSON.parse(event.data) as OrchestratorOutput;
        this.validateOrchestratorOutput(output);
        this.options.onStream?.(output);
      } catch (error) {
        const protocolError: ProtocolError = {
          code: 'STREAM_PARSE_ERROR',
          message: 'Failed to parse streaming output',
          details: error,
          requestId
        };
        this.options.onError?.(protocolError);
      }
    };

    eventSource.onerror = (error) => {
      const protocolError: ProtocolError = {
        code: 'STREAM_ERROR',
        message: 'Streaming connection error',
        details: error,
        requestId
      };
      this.options.onError?.(protocolError);
      eventSource.close();
    };
  }

  /**
   * Fetch adjacency list for ComponentGraph rendering
   */
  async fetchAdjacencyList(route: string, params: Record<string, any> = {}): Promise<AdjacencyList> {
    try {
      const request: ProtocolRequest = {
        action: route,
        payload: params,
        tenant_id: this.options.tenantId || 'default',
        user_id: this.options.userId || 'default',
        request_id: this.generateRequestId()
      };

      const response = await fetch(`${this.baseUrl}/protocol/adjacency`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': request.tenant_id,
          'X-User-ID': request.user_id,
          'X-Request-ID': request.request_id
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`Adjacency Error: ${response.statusText}`);
      }

      return await response.json() as AdjacencyList;
    } catch (error) {
      const protocolError: ProtocolError = {
        code: 'ADJACENCY_FAILED',
        message: error instanceof Error ? error.message : 'Unknown error',
        details: error
      };
      
      this.options.onError?.(protocolError);
      throw protocolError;
    }
  }

  /**
   * Send user action back to backend
   */
  async sendAction(actionId: string, payload?: any): Promise<OrchestratorOutput> {
    try {
      const request: ProtocolRequest = {
        action: 'user_action',
        payload: { actionId, ...payload },
        tenant_id: this.options.tenantId || 'default',
        user_id: this.options.userId || 'default',
        request_id: this.generateRequestId()
      };

      const response = await fetch(`${this.baseUrl}/protocol/action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': request.tenant_id,
          'X-User-ID': request.user_id,
          'X-Request-ID': request.request_id
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`Action Error: ${response.statusText}`);
      }

      return await response.json() as OrchestratorOutput;
    } catch (error) {
      const protocolError: ProtocolError = {
        code: 'ACTION_FAILED',
        message: error instanceof Error ? error.message : 'Unknown error',
        details: error
      };
      
      this.options.onError?.(protocolError);
      throw protocolError;
    }
  }

  /**
   * Validate orchestrator output format
   */
  private validateOrchestratorOutput(output: any): void {
    if (!output || typeof output !== 'object') {
      throw new Error('Invalid orchestrator output: not an object');
    }

    const requiredFields = ['request_id', 'tenant_id', 'user_id', 'state', 'chunks', 'timestamp'];
    for (const field of requiredFields) {
      if (!(field in output)) {
        throw new Error(`Invalid orchestrator output: missing ${field}`);
      }
    }

    if (!Array.isArray(output.chunks)) {
      throw new Error('Invalid orchestrator output: chunks must be array');
    }

    const validStates = ['STREAMING', 'WAITING_FOR_CONFIRMATION', 'COMPLETED', 'ERROR'];
    if (!validStates.includes(output.state)) {
      throw new Error(`Invalid orchestrator output: invalid state ${output.state}`);
    }
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Export singleton instance
export const protocolKernelBridge = new ProtocolKernelBridge();

export default ProtocolKernelBridge;