import { useState, useEffect, useCallback, useRef } from 'react';
import { kernelBridge, StreamEvent, StreamOptions } from '../services/kernelBridge';

export interface StreamState {
  isConnected: boolean;
  events: StreamEvent[];
  error: Error | null;
  isLoading: boolean;
}

export interface UseStreamingOptions extends StreamOptions {
  autoConnect?: boolean;
  maxEvents?: number;
  onEventFilter?: (event: StreamEvent) => boolean;
}

/**
 * React hook for Server-Sent Events (SSE) streaming
 * Provides easy integration with A2UI streaming endpoints
 */
export function useStreaming(sessionId: string, options: UseStreamingOptions = {}) {
  const [streamState, setStreamState] = useState<StreamState>({
    isConnected: false,
    events: [],
    error: null,
    isLoading: true,
  });

  const eventBufferRef = useRef<StreamEvent[]>([]);
  const { autoConnect = true, maxEvents = 100, onEventFilter, ...streamOptions } = options;

  const handleMessage = useCallback((event: StreamEvent) => {
    // Apply event filter if provided
    if (onEventFilter && !onEventFilter(event)) {
      return;
    }

    // Add event to buffer
    eventBufferRef.current.push(event);

    // Limit buffer size
    if (eventBufferRef.current.length > maxEvents) {
      eventBufferRef.current.shift(); // Remove oldest event
    }

    // Update state
    setStreamState(prev => ({
      ...prev,
      events: [...eventBufferRef.current],
      error: null,
    }));

    // Call original onMessage if provided
    streamOptions.onMessage?.(event);
  }, [maxEvents, onEventFilter, streamOptions.onMessage]);

  const handleConnect = useCallback(() => {
    setStreamState(prev => ({
      ...prev,
      isConnected: true,
      isLoading: false,
      error: null,
    }));

    streamOptions.onConnect?.();
  }, [streamOptions.onConnect]);

  const handleDisconnect = useCallback(() => {
    setStreamState(prev => ({
      ...prev,
      isConnected: false,
      isLoading: false,
    }));

    streamOptions.onDisconnect?.();
  }, [streamOptions.onDisconnect]);

  const handleError = useCallback((error: Error) => {
    setStreamState(prev => ({
      ...prev,
      error,
      isLoading: false,
    }));

    streamOptions.onError?.(error);
  }, [streamOptions.onError]);

  const connect = useCallback(() => {
    if (!sessionId) {
      console.warn('Cannot connect streaming: sessionId is required');
      return;
    }

    setStreamState(prev => ({ ...prev, isLoading: true, error: null }));

    kernelBridge.connectStream(sessionId, {
      onMessage: handleMessage,
      onConnect: handleConnect,
      onDisconnect: handleDisconnect,
      onError: handleError,
    });
  }, [sessionId, handleMessage, handleConnect, handleDisconnect, handleError]);

  const disconnect = useCallback(() => {
    if (sessionId) {
      kernelBridge.disconnectStream(sessionId);
      setStreamState(prev => ({ ...prev, isConnected: false, isLoading: false }));
    }
  }, [sessionId]);

  const clearEvents = useCallback(() => {
    eventBufferRef.current = [];
    setStreamState(prev => ({ ...prev, events: [] }));
  }, []);

  const sendEvent = useCallback(async (eventType: string, data: any) => {
    if (!sessionId) {
      throw new Error('Cannot send event: sessionId is required');
    }

    return kernelBridge.sendStreamEvent(sessionId, eventType, data);
  }, [sessionId]);

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect && sessionId) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      if (sessionId) {
        kernelBridge.disconnectStream(sessionId);
      }
    };
  }, [autoConnect, sessionId, connect]);

  // Reconnect when sessionId changes
  useEffect(() => {
    if (sessionId && autoConnect) {
      connect();
    }
  }, [sessionId, autoConnect, connect]);

  return {
    ...streamState,
    connect,
    disconnect,
    clearEvents,
    sendEvent,
    isStreamConnected: kernelBridge.isStreamConnected(sessionId),
  };
}

/**
 * Convenience hook for component-specific streaming
 * Filters events by component type
 */
export function useComponentStreaming(
  sessionId: string,
  componentType: string,
  options: UseStreamingOptions = {}
) {
  const filteredOptions = {
    ...options,
    onEventFilter: (event: StreamEvent) => {
      const matchesComponent = event.data?.ui?.component?.[componentType] !== undefined;
      const matchesType = ['skeleton_response', 'composition_response', 'update_response'].includes(event.type);
      
      return matchesComponent && matchesType;
    },
  };

  return useStreaming(sessionId, filteredOptions);
}

/**
 * Hook for progress tracking in streaming
 */
export function useStreamingProgress(sessionId: string, options: UseStreamingOptions = {}) {
  const [progress, setProgress] = useState({
    stage: 'initializing',
    percentage: 0,
    message: 'Initializing...',
  });

  const handleMessage = useCallback((event: StreamEvent) => {
    if (event.data?.progress) {
      setProgress(event.data.progress);
    }

    options.onMessage?.(event);
  }, [options.onMessage]);

  const streaming = useStreaming(sessionId, {
    ...options,
    onMessage: handleMessage,
  });

  return {
    ...streaming,
    progress,
  };
}