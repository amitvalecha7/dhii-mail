import React, { useState, useEffect } from 'react';
import { useStreaming, useStreamingProgress } from '../hooks/useStreaming';
import { StreamEvent } from '../services/kernelBridge';

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
          <h3>Streaming Demo</h3>
          <p>Click "Start Streaming" to begin real-time UI updates</p>
        </div>
      );
    }

    switch (uiState.type) {
      case 'skeleton':
        return (
          <div className="streaming-demo-skeleton">
            <div className="skeleton-loader">
              <div className="skeleton-header"></div>
              <div className="skeleton-content"></div>
              <div className="skeleton-actions"></div>
            </div>
            <p className="streaming-message">{uiState.message}</p>
          </div>
        );

      case 'final':
        return (
          <div className="streaming-demo-final">
            <div className="ui-component">
              {uiState.data?.component ? (
                <pre className="ui-data">
                  {JSON.stringify(uiState.data.component, null, 2)}
                </pre>
              ) : (
                <div>No UI data available</div>
              )}
            </div>
            <p className="streaming-message success">{uiState.message}</p>
          </div>
        );

      case 'error':
        return (
          <div className="streaming-demo-error">
            <div className="error-message">
              <span className="error-icon">❌</span>
              {uiState.message}
            </div>
          </div>
        );

      default:
        return <div>Unknown UI state</div>;
    }
  };

  return (
    <div className="streaming-demo-container">
      <div className="streaming-demo-header">
        <h2>🌊 A2UI Streaming Transport Demo</h2>
        <div className="streaming-controls">
          <span className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
          
          {!isStreaming ? (
            <button onClick={startStreaming} className="btn btn-primary">
              Start Streaming
            </button>
          ) : (
            <button onClick={stopStreaming} className="btn btn-secondary">
              Stop Streaming
            </button>
          )}
          
          {onClose && (
            <button onClick={onClose} className="btn btn-close">
              ✕
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="streaming-error">
          <span className="error-icon">⚠️</span>
          {error.message}
        </div>
      )}

      <div className="streaming-demo-content">
        {renderUI()}
      </div>

      {isStreaming && (
        <div className="streaming-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress.percentage}%` }}
            ></div>
          </div>
          <span className="progress-text">
            {progress.stage}: {progress.message}
          </span>
        </div>
      )}

      <div className="streaming-events">
        <h4>Event Log ({events.length} events)</h4>
        <div className="events-list">
          {events.slice(-10).map((event, index) => (
            <div key={index} className={`event-item ${event.type}`}>
              <span className="event-type">{event.type}</span>
              <span className="event-timestamp">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StreamingDemo;