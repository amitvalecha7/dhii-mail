/**
 * Enterprise-Scale Protocol Dashboard Screen
 * Stateless, tenant-agnostic UI using deterministic renderer
 * Zero business logic - pure protocol rendering
 */

import React, { useEffect, useState } from 'react';
import { User, AppScreen } from '../types';
import { DeterministicRenderer } from '../components/DeterministicRenderer';
import { ProtocolKernelBridge } from '../services/protocolKernelBridge';
import { OrchestratorOutput } from '../types/protocol';

interface ProtocolDashboardScreenProps {
  user: User;
  onNavigate: (screen: AppScreen) => void;
  tenantId?: string;
}

/**
 * Stateless dashboard that renders orchestrator output via JSON protocol
 * No business logic, no data fetching, no tenant-specific code
 */
const ProtocolDashboardScreen: React.FC<ProtocolDashboardScreenProps> = ({ 
  user, 
  onNavigate, 
  tenantId = 'default' 
}) => {
  const [orchestratorOutput, setOrchestratorOutput] = useState<OrchestratorOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Protocol kernel bridge - tenant-agnostic
  const protocolBridge = new ProtocolKernelBridge({
    tenantId,
    userId: user.id,
    onStream: (output) => {
      setOrchestratorOutput(output);
      setLoading(false);
    },
    onError: (error) => {
      setError(error.message);
      setLoading(false);
    }
  });

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch orchestrator output via JSON protocol
        const output = await protocolBridge.fetchOrchestratorOutput('dashboard', {
          screen: 'dashboard',
          user_context: {
            id: user.id,
            name: user.name,
            email: user.email
          }
        });
        
        setOrchestratorOutput(output);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [user.id, tenantId]);

  const handleAction = async (actionId: string, payload?: any) => {
    try {
      const output = await protocolBridge.sendAction(actionId, payload);
      setOrchestratorOutput(output);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Action failed');
    }
  };

  const handleFormSubmit = async (formId: string, data: Record<string, any>) => {
    try {
      const output = await protocolBridge.sendAction('form_submit', {
        form_id: formId,
        data
      });
      setOrchestratorOutput(output);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Form submission failed');
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-slate-600">Loading protocol-compliant UI...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center bg-slate-50">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h3 className="text-lg font-semibold text-red-900 mb-2">Protocol Error</h3>
          <p className="text-red-700 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!orchestratorOutput) {
    return (
      <div className="flex-1 flex items-center justify-center bg-slate-50">
        <div className="text-slate-600">No UI data available</div>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-slate-50">
      {/* Protocol metadata (for debugging/development) */}
      <div className="bg-white border-b border-slate-200 px-6 py-3">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-4">
            <span>Request: {orchestratorOutput.request_id}</span>
            <span>State: {orchestratorOutput.state}</span>
            <span>Tenant: {orchestratorOutput.tenant_id}</span>
          </div>
          <div className="text-slate-400">
            Protocol v1.2 Compliant
          </div>
        </div>
      </div>

      {/* Deterministic UI Renderer */}
      <div className="flex-1 overflow-y-auto p-6">
        <DeterministicRenderer 
          orchestratorOutput={orchestratorOutput}
          onAction={handleAction}
          onFormSubmit={handleFormSubmit}
        />
      </div>

      {/* State indicator for streaming */}
      {orchestratorOutput.state === 'STREAMING' && (
        <div className="fixed bottom-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg">
          <div className="flex items-center gap-2">
            <div className="animate-pulse">●</div>
            <span className="text-sm">Processing...</span>
          </div>
        </div>
      )}

      {/* Waiting for user confirmation */}
      {orchestratorOutput.state === 'WAITING_FOR_CONFIRMATION' && (
        <div className="fixed bottom-4 right-4 bg-amber-600 text-white px-4 py-2 rounded-lg shadow-lg">
          <div className="flex items-center gap-2">
            <span className="text-sm">Waiting for confirmation...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProtocolDashboardScreen;