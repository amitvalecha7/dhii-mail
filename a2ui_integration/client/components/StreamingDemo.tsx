import React, { useState, useEffect, useCallback } from 'react';
import { useStreaming, useStreamingProgress } from '../hooks/useStreaming';
import { StreamEvent } from '../services/kernelBridge';
import { LiquidGlassStreamGrid } from './LiquidGlassStream';

interface StreamingDemoProps {
  sessionId: string;
  onClose?: () => void;
}

/**
 * Demo component showcasing Server-Sent Events (SSE) streaming
 * This component demonstrates real-time UI updates with progressive enhancement
 */
export const StreamingDemo: React.FC<StreamingDemoProps> = ({ sessionId, onClose }) => {
  const [uiState, setUiState] = useState<any>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const { 
    isConnected, 
    events, 
    error, 
    progress,
    connect, 
    disconnect 
  } = useStreamingProgress(sessionId, {
    autoConnect: false, // Manual control for demo
    maxEvents: 50,
  });

  // Handle incoming streaming events
  useEffect(() => {
    if (events.length === 0) return;

    const latestEvent = events[events.length - 1];
    
    switch (latestEvent.type) {
      case 'skeleton_response':
        // Show skeleton/loading state
        setUiState({
          type: 'skeleton',
          data: latestEvent.data.ui,
          message: 'Loading interface...'
        });
        break;

      case 'composition_response':
        // Show final composition
        setUiState({
          type: 'final',
          data: latestEvent.data.ui,
          message: 'Interface ready!'
        });
        setIsStreaming(false);
        break;

      case 'update_response':
        // Handle incremental updates
        setUiState(prev => ({
          ...prev,
          updates: [...(prev?.updates || []), latestEvent.data.ui]
        }));
        break;

      case 'progress_response':
        // Progress updates are handled by the hook
        break;

      case 'error_response':
        setUiState({
          type: 'error',
          data: null,
          message: latestEvent.data.error || 'Streaming error occurred'
        });
        setIsStreaming(false);
        break;

      default:
        console.log('Unhandled event type:', latestEvent.type);
    }
  }, [events]);

  const startStreaming = () => {
    setIsStreaming(true);
    setUiState(null);
    connect();
  };

  const stopStreaming = () => {
    setIsStreaming(false);
    disconnect();
  };

  const renderUI = () => {
    if (!uiState) {
      return (
        <div className="streaming-demo-placeholder">
          <div className="liquid-glass rounded-3xl p-8 text-center space-y-4 specular-highlight">
            <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center mb-4">
              <span className="material-symbols-outlined text-white text-2xl">blur_on</span>
            </div>
            <h3 className="text-xl font-bold text-slate-300">A2UI Streaming Transport</h3>
            <p className="text-slate-500 text-sm">Click "Start Streaming" to begin real-time UI updates with Liquid Glass effects</p>
            <div className="mt-6 flex items-center justify-center gap-2 text-xs text-slate-600">
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
              <span>Ready for SSE streaming</span>
            </div>
          </div>
        </div>
      );
    }

    switch (uiState.type) {
      case 'skeleton':
        return (
          <div className="streaming-demo-skeleton">
            <div className="streaming-card space-y-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-400">
                  <span className="material-symbols-outlined">hourglass_empty</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-200">Loading Interface</h3>
                  <p className="text-xs text-slate-500">Skeleton streaming in progress</p>
                </div>
              </div>
              <div className="skeleton-loader space-y-4">
                <div className="skeleton-header h-8 bg-white/5 rounded-xl animate-pulse"></div>
                <div className="skeleton-content h-32 bg-white/5 rounded-2xl animate-pulse"></div>
                <div className="skeleton-actions h-12 bg-white/5 rounded-xl animate-pulse"></div>
              </div>
            </div>
            <p className="streaming-message">{uiState.message}</p>
          </div>
        );

      case 'final':
        return (
          <div className="streaming-demo-final">
            <div className="streaming-card space-y-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 rounded-2xl bg-green-500/10 flex items-center justify-center text-green-400">
                  <span className="material-symbols-outlined">check_circle</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-200">Interface Ready</h3>
                  <p className="text-xs text-slate-500">Composition complete</p>
                </div>
              </div>
              <div className="ui-component">
                {uiState.data?.component ? (
                  <div className="ui-data">
                    <div className="flex items-center gap-2 mb-3">
                      <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                      <span className="text-xs text-slate-400">A2UI Component Data</span>
                    </div>
                    <pre className="text-xs text-slate-300 overflow-x-auto">
                      {JSON.stringify(uiState.data.component, null, 2)}
                    </pre>
                  </div>
                ) : (
                  <div className="text-slate-500 text-center py-8">No UI data available</div>
                )}
              </div>
            </div>
            <p className="streaming-message success">{uiState.message}</p>
          </div>
        );

      case 'error':
        return (
          <div className="streaming-demo-error">
            <div className="streaming-card">
              <div className="error-message">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-red-500/10 flex items-center justify-center text-red-400">
                    <span className="material-symbols-outlined">error</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-200">Streaming Error</h3>
                    <p className="text-sm text-slate-500">{uiState.message}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return <div className="text-slate-500">Unknown UI state</div>;
    }
  };

  return (
    <div className="streaming-demo-container streaming-active">
      <div className="streaming-demo-header">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20">
            <span className="material-symbols-outlined text-white text-xl">blur_on</span>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gradient">A2UI Streaming Transport</h2>
            <p className="text-sm text-slate-500">Real-time UI updates with Liquid Glass effects</p>
          </div>
        </div>
        <div className="streaming-controls">
          <span className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
          
          {!isStreaming ? (
            <button onClick={startStreaming} className="btn btn-primary specular-highlight">
              <span className="material-symbols-outlined text-sm mr-2">play_arrow</span>
              Start Streaming
            </button>
          ) : (
            <button onClick={stopStreaming} className="btn btn-secondary specular-highlight">
              <span className="material-symbols-outlined text-sm mr-2">stop</span>
              Stop Streaming
            </button>
          )}
          
          {onClose && (
            <button onClick={onClose} className="btn btn-close specular-highlight">
              <span className="material-symbols-outlined">close</span>
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="streaming-error liquid-glass rounded-xl">
          <span className="error-icon">⚠️</span>
          {error.message}
        </div>
      )}

      <div className="streaming-demo-content">
        {renderUI()}
      </div>

      {isStreaming && (
        <div className="streaming-progress liquid-glass streaming-card specular-highlight">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary animate-pulse">
              <span className="material-symbols-outlined text-xl">schedule</span>
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-bold text-slate-200">{progress.stage}</h3>
                <span className="text-sm text-slate-500 font-mono">{progress.percentage}%</span>
              </div>
              <div className="progress-bar mb-3">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progress.percentage}%` }}
                ></div>
              </div>
              <p className="text-sm text-slate-400">
                {progress.message}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="streaming-events">
        <LiquidGlassStreamGrid 
          events={events}
          maxEvents={8}
          className="streaming-active"
        />
      </div>
    </div>
  );
};

export default StreamingDemo;