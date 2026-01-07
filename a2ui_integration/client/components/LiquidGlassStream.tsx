import React from 'react';
import { StreamEvent } from '../services/kernelBridge';

interface LiquidGlassStreamCardProps {
  event: StreamEvent;
  isActive?: boolean;
  className?: string;
}

/**
 * Liquid Glass Stream Card - Enhanced streaming UI component
 * Displays streaming events with A2UI.org inspired liquid glass effects
 */
export const LiquidGlassStreamCard: React.FC<LiquidGlassStreamCardProps> = ({ 
  event, 
  isActive = false, 
  className = '' 
}) => {
  const getEventIcon = (type: string) => {
    switch (type) {
      case 'skeleton':
        return 'hourglass_empty';
      case 'composition':
        return 'layers';
      case 'update':
        return 'sync_alt';
      case 'error':
        return 'error';
      default:
        return 'stream';
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'skeleton':
        return 'blue';
      case 'composition':
        return 'green';
      case 'update':
        return 'purple';
      case 'error':
        return 'red';
      default:
        return 'slate';
    }
  };

  const color = getEventColor(event.type);
  const icon = getEventIcon(event.type);

  return (
    <div className={`
      liquid-glass streaming-card specular-highlight
      ${isActive ? 'streaming-active' : ''}
      ${className}
    `}>
      <div className="flex items-center gap-4">
        <div className={`
          w-12 h-12 rounded-2xl flex items-center justify-center
          bg-${color}-500/10 text-${color}-400
          ${isActive ? 'animate-pulse' : ''}
        `}>
          <span className="material-symbols-outlined text-xl">
            {icon}
          </span>
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`
              text-sm font-bold uppercase tracking-wider
              text-${color}-400
            `}>
              {event.type}
            </span>
            {isActive && (
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
            )}
          </div>
          
          <p className="text-xs text-slate-400 truncate">
            {event.data?.message || 'Streaming event received'}
          </p>
          
          <div className="flex items-center gap-3 mt-2 text-[10px] text-slate-500">
            <span className="font-mono">
              {new Date(event.timestamp).toLocaleTimeString()}
            </span>
            {event.session_id && (
              <span className="truncate max-w-[100px]">
                Session: {event.session_id.slice(-8)}
              </span>
            )}
          </div>
        </div>
        
        <div className="flex flex-col items-end gap-2">
          {event.data?.progress && (
            <div className="flex items-center gap-2">
              <div className="w-16 h-1 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className={`h-full bg-${color}-500 rounded-full transition-all duration-300`}
                  style={{ width: `${event.data.progress.percentage || 0}%` }}
                />
              </div>
              <span className="text-[10px] text-slate-500 font-mono">
                {event.data.progress.percentage || 0}%
              </span>
            </div>
          )}
          
          {event.data?.ui && (
            <div className="flex items-center gap-1 text-[10px] text-slate-500">
              <span className="material-symbols-outlined text-[10px]">widgets</span>
              <span>UI Update</span>
            </div>
          )}
        </div>
      </div>
      
      {event.data?.ui?.component && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-2">
            <span className="material-symbols-outlined text-sm">code</span>
            <span>Component Data</span>
          </div>
          <div className="bg-black/20 rounded-xl p-3 text-[10px] text-slate-300 font-mono overflow-x-auto">
            {JSON.stringify(event.data.ui.component, null, 2).slice(0, 200)}
            {JSON.stringify(event.data.ui.component, null, 2).length > 200 && '...'}
          </div>
        </div>
      )}
    </div>
  );
};

interface LiquidGlassStreamGridProps {
  events: StreamEvent[];
  maxEvents?: number;
  className?: string;
}

/**
 * Liquid Glass Stream Grid - Container for multiple streaming events
 * Displays a grid of streaming events with liquid glass styling
 */
export const LiquidGlassStreamGrid: React.FC<LiquidGlassStreamGridProps> = ({ 
  events, 
  maxEvents = 10, 
  className = '' 
}) => {
  const displayEvents = events.slice(-maxEvents);
  const latestEventId = displayEvents[displayEvents.length - 1]?.timestamp;

  return (
    <div className={`space-y-4 ${className}`}>
      {displayEvents.length === 0 ? (
        <div className="liquid-glass streaming-card text-center py-12">
          <div className="w-16 h-16 mx-auto rounded-full bg-white/5 flex items-center justify-center mb-4">
            <span className="material-symbols-outlined text-2xl text-slate-500">stream</span>
          </div>
          <h3 className="text-lg font-semibold text-slate-300 mb-2">No Active Stream</h3>
          <p className="text-sm text-slate-500">Connect to a streaming session to see real-time UI updates</p>
        </div>
      ) : (
        displayEvents.map((event) => (
          <LiquidGlassStreamCard 
            key={event.timestamp + event.type}
            event={event}
            isActive={event.timestamp === latestEventId}
          />
        ))
      )}
      
      {displayEvents.length > 0 && (
        <div className="text-center text-xs text-slate-500 mt-4">
          Showing {displayEvents.length} of {events.length} total events
        </div>
      )}
    </div>
  );
};

export default {
  LiquidGlassStreamCard,
  LiquidGlassStreamGrid
};