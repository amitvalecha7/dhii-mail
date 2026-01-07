/**
 * Enterprise-Scale Protocol Workspace Shell
 * Tenant-agnostic, stateless workspace container
 * Zero business logic - pure protocol communication
 */

import React, { useState, useRef, useEffect } from 'react';
import { User, AppScreen, ChatMessage } from '../types';
import { ProtocolKernelBridge } from '../services/protocolKernelBridge';
import { OrchestratorOutput } from '../types/protocol';
import { DeterministicRenderer } from './DeterministicRenderer';

interface ProtocolWorkspaceShellProps {
  user: User;
  currentScreen: AppScreen;
  onNavigate: (screen: AppScreen) => void;
  children: React.ReactNode;
  tenantId?: string;
}

/**
 * Stateless workspace shell using JSON protocol
 * No business logic, no data fetching, pure protocol communication
 */
const ProtocolWorkspaceShell: React.FC<ProtocolWorkspaceShellProps> = ({ 
  user, 
  currentScreen, 
  onNavigate, 
  children,
  tenantId = 'default'
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [orchestratorOutput, setOrchestratorOutput] = useState<OrchestratorOutput | null>(null);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  // Protocol kernel bridge - tenant-agnostic
  const protocolBridge = new ProtocolKernelBridge({
    tenantId,
    userId: user.id,
    onStream: (output) => {
      setOrchestratorOutput(output);
      // Add AI response to chat
      if (output.explanation) {
        setMessages(prev => [...prev, {
          role: 'model',
          text: output.explanation,
          timestamp: new Date()
        }]);
      }
      setIsTyping(false);
    }
  });

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTo({ top: chatScrollRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, isTyping]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMsg: ChatMessage = { 
      role: 'user', 
      text: inputValue, 
      timestamp: new Date() 
    };
    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Send message via JSON protocol
      const output = await protocolBridge.sendAction('chat_message', {
        message: inputValue,
        screen: currentScreen,
        context: {
          screen: currentScreen,
          user_context: {
            id: user.id,
            name: user.name,
            email: user.email
          }
        }
      });

      setOrchestratorOutput(output);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'model',
        text: 'Protocol communication error. Please try again.',
        timestamp: new Date()
      }]);
      setIsTyping(false);
    }
  };

  const NavItem = ({ icon, label, target }: { icon: string; label: string; target: AppScreen }) => {
    const active = currentScreen === target;
    return (
      <button 
        onClick={() => onNavigate(target)}
        className={`group flex flex-col items-center justify-center size-14 rounded-2xl transition-all duration-300 ${
          active 
          ? 'bg-primary/20 text-primary shadow-[0_0_20px_rgba(99,102,241,0.2)]' 
          : 'text-slate-500 hover:text-white hover:bg-white/5'
        }`}
      >
        <span className={`material-symbols-outlined text-[24px] ${active ? 'fill-1' : ''}`}>{icon}</span>
        <span className="text-[10px] mt-1">{label}</span>
      </button>
    );
  };

  return (
    <div className="flex h-screen bg-slate-900 text-white overflow-hidden">
      {/* Protocol Status Bar */}
      <div className="fixed top-0 left-0 right-0 h-8 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-4 text-xs text-slate-400 z-50">
        <div className="flex items-center gap-4">
          <span>Protocol: v1.2</span>
          <span>Tenant: {tenantId}</span>
          <span>User: {user.id}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            orchestratorOutput?.state === 'STREAMING' ? 'bg-blue-500 animate-pulse' :
            orchestratorOutput?.state === 'COMPLETED' ? 'bg-green-500' :
            orchestratorOutput?.state === 'ERROR' ? 'bg-red-500' : 'bg-slate-500'
          }`}></div>
          <span>{orchestratorOutput?.state || 'IDLE'}</span>
        </div>
      </div>

      {/* Side Navigation */}
      <nav className="w-20 bg-slate-900/50 backdrop-blur-xl border-r border-white/5 flex flex-col items-center py-6 space-y-4 z-40 mt-8">
        <NavItem icon="dashboard" label="Dashboard" target="DASHBOARD" />
        <NavItem icon="mail" label="Mail" target="MAIL" />
        <NavItem icon="task" label="Tasks" target="TASKS" />
        <NavItem icon="event" label="Meetings" target="MEETINGS" />
        
        <div className="flex-1"></div>
        
        <NavItem icon="settings" label="Settings" target="MAIL_CONFIG" />
        
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center shadow-lg">
          <span className="text-white font-bold text-sm">{user.name.charAt(0)}</span>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden mt-8">
        {children}
      </main>

      {/* AI Chat Panel */}
      <aside className="w-80 bg-slate-800/50 backdrop-blur-xl border-l border-white/5 flex flex-col z-40 mt-8">
        <div className="p-4 border-b border-white/5">
          <h3 className="font-semibold text-sm">Neural Link</h3>
          <p className="text-xs text-slate-400">Protocol-based AI Assistant</p>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={chatScrollRef}>
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs px-4 py-2 rounded-lg text-sm ${
                msg.role === 'user' 
                  ? 'bg-primary text-white' 
                  : 'bg-slate-700 text-slate-200'
              }`}>
                {msg.text}
                <div className="text-xs opacity-70 mt-1">
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-slate-700 text-slate-200 px-4 py-2 rounded-lg text-sm">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="p-4 border-t border-white/5">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Protocol command..."
              className="flex-1 bg-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={isTyping}
            />
            <button 
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
              className="bg-primary hover:bg-primary/80 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </aside>
    </div>
  );
};

export default ProtocolWorkspaceShell;