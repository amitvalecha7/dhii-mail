
import React, { useState, useRef, useEffect } from 'react';
import { User, AppScreen, ChatMessage } from '../types';
import { sendMessageToGemini } from '../services/geminiService';

interface WorkspaceShellProps {
  user: User;
  currentScreen: AppScreen;
  onNavigate: (screen: AppScreen) => void;
  children: React.ReactNode;
}

const WorkspaceShell: React.FC<WorkspaceShellProps> = ({ user, currentScreen, onNavigate, children }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'model', text: `Welcome back, Commander. dhii-mail system is online.`, timestamp: new Date() }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTo({ top: chatScrollRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, isTyping]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    const userMsg: ChatMessage = { role: 'user', text: inputValue, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsTyping(true);

    const responseText = await sendMessageToGemini(inputValue);
    setIsTyping(false);
    setMessages(prev => [...prev, { role: 'model', text: responseText || "Neural link failure.", timestamp: new Date() }]);
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
        <span className="text-[10px] font-bold mt-1 opacity-0 group-hover:opacity-100 transition-opacity uppercase tracking-tighter">{label}</span>
      </button>
    );
  };

  return (
    <div className="h-screen w-full flex bg-[#020307] overflow-hidden">
      
      {/* Column 1: Sidebar Navigation */}
      <aside className="w-[80px] sidebar-frosted flex flex-col items-center py-6 gap-6 z-30 shrink-0">
        <div className="size-12 rounded-2xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20 mb-4 animate-pulse-slow">
          <span className="material-symbols-outlined text-white text-2xl font-bold">blur_on</span>
        </div>
        
        <nav className="flex flex-col gap-4">
          <NavItem icon="dashboard" label="Home" target="DASHBOARD" />
          <NavItem icon="alternate_email" label="Inbox" target="MAIL" />
          <NavItem icon="calendar_today" label="Events" target="MEETINGS" />
          <NavItem icon="task_alt" label="Tasks" target="TASKS" />
        </nav>

        <div className="mt-auto flex flex-col gap-4">
          <button className="text-slate-500 hover:text-white transition-colors">
            <span className="material-symbols-outlined">settings</span>
          </button>
          <div className="size-10 rounded-full overflow-hidden border border-white/10 hover:border-primary transition-all p-0.5">
            <img src={user.avatar} className="size-full rounded-full object-cover" alt="User" />
          </div>
        </div>
      </aside>

      {/* Column 2: Dynamic Center Content (A2UI Surface) */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        <div className="absolute inset-0 mesh-gradient opacity-40 pointer-events-none"></div>
        {children}
      </main>

      {/* Column 3: Translucent Agent Chat Panel */}
      <aside className="w-[380px] agent-panel-frosted flex flex-col z-30 shrink-0">
        <header className="p-6 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="size-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
              <span className="material-symbols-outlined text-[18px]">auto_awesome</span>
            </div>
            <div>
              <h2 className="text-sm font-bold font-display tracking-tight">dhii Agent</h2>
              <p className="text-[9px] font-extrabold text-slate-500 uppercase tracking-widest">Neural Layer Active</p>
            </div>
          </div>
          <button className="text-slate-500 hover:text-white"><span className="material-symbols-outlined text-sm">open_in_full</span></button>
        </header>

        <div className="flex-1 overflow-y-auto no-scrollbar p-6 space-y-6" ref={chatScrollRef}>
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`max-w-[88%] px-5 py-4 rounded-[1.5rem] text-sm leading-relaxed shadow-sm ${
                msg.role === 'user' 
                ? 'bg-primary text-white rounded-tr-none font-medium' 
                : 'liquid-glass text-slate-200 rounded-tl-none border border-white/5'
              }`}>
                {msg.text}
              </div>
              <span className="text-[9px] text-slate-600 mt-2 font-bold uppercase tracking-tighter">
                {msg.role === 'user' ? 'Commander' : 'dhii Agent'} • {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          ))}
          {isTyping && (
            <div className="flex flex-col items-start animate-pulse">
              <div className="px-5 py-4 rounded-[1.5rem] bg-white/5 text-slate-400 border border-white/5 text-sm italic">
                Scanning neural streams...
              </div>
            </div>
          )}
        </div>

        <footer className="p-6 pt-2">
          <div className="relative group">
            <textarea 
              className="w-full bg-white/5 border border-white/10 rounded-[2rem] p-4 pl-6 pr-14 text-sm text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-primary/40 transition-all resize-none min-h-[54px] max-h-48"
              placeholder="System prompt..."
              rows={1}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />
            <button 
              onClick={handleSendMessage}
              className="absolute right-2 top-2 size-10 rounded-full bg-primary text-white hover:bg-blue-600 shadow-lg shadow-primary/20 flex items-center justify-center transition-transform active:scale-95"
            >
              <span className="material-symbols-outlined text-[20px]">send</span>
            </button>
          </div>
          <p className="text-center text-[8px] text-slate-700 mt-4 font-bold uppercase tracking-[0.3em]">dhii OS v3.2 • Secure Link</p>
        </footer>
      </aside>
    </div>
  );
};

export default WorkspaceShell;
