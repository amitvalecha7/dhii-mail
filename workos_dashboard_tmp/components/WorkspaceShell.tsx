
import React, { useState, useRef, useEffect, useMemo } from 'react';
import { User, ChatMessage, WidgetType } from '../types';
import { sendMessageToGemini } from '../services/geminiService';
import AuthWidget from './AuthWidget';
import DashboardWidget from './DashboardWidget';
import MailWidget from './MailWidget';
import TasksWidget from './TasksWidget';
import MeetingsWidget from './MeetingsWidget';
import SettingsWidget from './SettingsWidget';

interface WorkspaceShellProps {
  user: User | null;
  onAuthSuccess: () => void;
  onLogout: () => void;
}

const WorkspaceShell: React.FC<WorkspaceShellProps> = ({ user, onAuthSuccess, onLogout }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [activeModule, setActiveModule] = useState<WidgetType>('DASHBOARD');
  const scrollRef = useRef<HTMLDivElement>(null);

  // Find the index of the absolute last message that HAS a widget
  const lastWidgetIndex = useMemo(() => {
    // We iterate backwards to find the last one
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].widget && messages[i].widget !== 'NONE') {
        return i;
      }
    }
    return -1;
  }, [messages]);

  // Initial Welcome
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{ 
        id: 'init',
        role: 'model', 
        text: "dhii-mail OS v4.0 Online. \nConversational Interface Ready. \nPlease authenticate to access nodes.", 
        timestamp: new Date(),
        widget: user ? 'DASHBOARD' : 'NONE'
      }]);
    }
  }, []);

  // Reactive System Messages on Login
  useEffect(() => {
    if (user && !messages.some(m => m.text.includes('Identity Verified'))) {
       setMessages(prev => [...prev, {
         id: `sys-${Date.now()}`,
         role: 'model',
         text: `Identity Verified: Commander ${user.name.split(' ')[0]}. Access Level: Admin.`,
         timestamp: new Date(),
         widget: 'DASHBOARD'
       }]);
    }
  }, [user]);

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, isTyping, lastWidgetIndex]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isTyping) return;
    
    const userMsg: ChatMessage = { 
      id: `usr-${Date.now()}`,
      role: 'user', 
      text: inputValue, 
      timestamp: new Date() 
    };
    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsTyping(true);

    const isAuthenticated = !!user;
    const responseText = await sendMessageToGemini(inputValue, isAuthenticated);
    setIsTyping(false);

    if (responseText) {
      let cleanText = responseText;
      let widgetType: WidgetType = 'NONE';
      
      // PARSE PROTOCOL
      if (responseText.includes('[ACTION:WIDGET_AUTH]')) {
        widgetType = 'AUTH';
        cleanText = cleanText.replace('[ACTION:WIDGET_AUTH]', '');
      } else if (responseText.includes('[ACTION:WIDGET_DASHBOARD]')) {
        widgetType = 'DASHBOARD';
        cleanText = cleanText.replace('[ACTION:WIDGET_DASHBOARD]', '');
      } else if (responseText.includes('[ACTION:WIDGET_MAIL]')) {
        widgetType = 'MAIL';
        cleanText = cleanText.replace('[ACTION:WIDGET_MAIL]', '');
      } else if (responseText.includes('[ACTION:WIDGET_TASKS]')) {
        widgetType = 'TASKS';
        cleanText = cleanText.replace('[ACTION:WIDGET_TASKS]', '');
      } else if (responseText.includes('[ACTION:WIDGET_MEETINGS]')) {
        widgetType = 'MEETINGS';
        cleanText = cleanText.replace('[ACTION:WIDGET_MEETINGS]', '');
      } else if (responseText.includes('[ACTION:WIDGET_SETTINGS]')) {
        widgetType = 'SETTINGS';
        cleanText = cleanText.replace('[ACTION:WIDGET_SETTINGS]', '');
      }
      
      if (widgetType !== 'NONE') setActiveModule(widgetType);

      setMessages(prev => [...prev, { 
        id: `ai-${Date.now()}`,
        role: 'model', 
        text: cleanText.trim(), 
        widget: widgetType, 
        timestamp: new Date() 
      }]);
    }
  };

  const handleManualTrigger = (type: WidgetType, label: string) => {
    const userMsg: ChatMessage = {
      id: `usr-click-${Date.now()}`,
      role: 'user',
      text: `Access ${label}`,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    setTimeout(() => {
        setIsTyping(false);
        let widgetToRender: WidgetType = type;
        let responseText = `Loading ${label} module...`;

        if (!user) {
            widgetToRender = 'AUTH';
            responseText = `Access denied to ${label}. Identity verification required.`;
        }

        if (widgetToRender !== 'NONE') setActiveModule(widgetToRender);

        const sysMsg: ChatMessage = {
            id: `sys-click-${Date.now()}`,
            role: 'model',
            text: responseText,
            widget: widgetToRender,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, sysMsg]);
    }, 600);
  };

  const handleLogoutAction = () => {
    onLogout();
    setMessages(prev => [...prev, {
      id: `sys-logout-${Date.now()}`,
      role: 'model',
      text: 'Session Terminated. Guest Mode Active.',
      timestamp: new Date(),
      widget: 'AUTH'
    }]);
    setActiveModule('AUTH');
  };

  const renderWidget = (type?: WidgetType) => {
    switch (type) {
      case 'AUTH': return !user ? <AuthWidget onAuthSuccess={onAuthSuccess} /> : null;
      case 'DASHBOARD': return user ? <DashboardWidget user={user} /> : null;
      case 'MAIL': return user ? <MailWidget /> : null;
      case 'TASKS': return user ? <TasksWidget /> : null;
      case 'MEETINGS': return user ? <MeetingsWidget /> : null;
      case 'SETTINGS': return user ? <SettingsWidget user={user} onLogout={handleLogoutAction} /> : null;
      default: return null;
    }
  };

  const SidebarItem = ({ icon, label, type, active }: { icon: string, label: string, type: WidgetType, active: boolean }) => (
    <button 
      onClick={() => handleManualTrigger(type, label)}
      className={`group relative flex items-center justify-center size-12 rounded-xl transition-all duration-300 ${
        active 
        ? 'bg-primary text-white shadow-[0_0_15px_rgba(99,102,241,0.5)]' 
        : 'text-slate-500 hover:text-white hover:bg-white/10'
      }`}
      title={label}
    >
      <span className="material-symbols-outlined text-[24px]">{icon}</span>
      <span className="absolute left-14 px-2 py-1 bg-[#1a1d26] border border-white/10 rounded text-[10px] font-bold uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 pointer-events-none">
        {label}
      </span>
      {active && <div className="absolute -left-3 top-1/2 -translate-y-1/2 w-1 h-6 bg-primary rounded-r-full"></div>}
    </button>
  );

  return (
    <div className="h-screen w-full flex bg-[#020307] relative overflow-hidden font-sans">
      <div className="absolute inset-0 mesh-gradient opacity-30 pointer-events-none"></div>

      {user && (
        <aside className="w-20 hidden md:flex flex-col items-center py-6 border-r border-white/5 bg-[#0a0c10]/40 backdrop-blur-xl z-50 animate-in slide-in-from-left-4 duration-500">
          <div className="size-10 rounded-xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-white mb-8 shadow-lg shadow-primary/20">
              <span className="material-symbols-outlined text-[20px]">blur_on</span>
          </div>
          <nav className="flex-1 flex flex-col gap-6 w-full px-4 items-center">
              <SidebarItem icon="grid_view" label="Dashboard" type="DASHBOARD" active={activeModule === 'DASHBOARD'} />
              <div className="w-8 h-px bg-white/5 rounded-full"></div>
              <SidebarItem icon="mail" label="Inbox" type="MAIL" active={activeModule === 'MAIL'} />
              <SidebarItem icon="calendar_today" label="Timeline" type="MEETINGS" active={activeModule === 'MEETINGS'} />
              <SidebarItem icon="check_circle" label="Directives" type="TASKS" active={activeModule === 'TASKS'} />
          </nav>
          <div className="mt-auto flex flex-col items-center gap-4">
              <button 
                onClick={() => handleManualTrigger('SETTINGS', 'Settings')}
                className={`size-10 rounded-full flex items-center justify-center transition-colors ${activeModule === 'SETTINGS' ? 'bg-white/20 text-white' : 'bg-white/5 text-slate-500 hover:text-white'}`}
              >
                <span className="material-symbols-outlined text-[20px]">settings</span>
              </button>
              <div className="size-10 rounded-full border border-white/10 p-0.5">
                  <img src={user.avatar} className="size-full rounded-full object-cover" alt="User" />
              </div>
          </div>
        </aside>
      )}

      <div className="flex-1 flex flex-col relative min-w-0">
        <header className="sticky top-0 z-40 flex items-center justify-between px-6 py-4 bg-[#020307]/80 backdrop-blur-md border-b border-white/5">
          <div className="flex items-center gap-3 md:hidden">
             <div className="size-8 rounded-xl bg-primary/20 flex items-center justify-center text-primary">
                <span className="material-symbols-outlined text-[20px]">blur_on</span>
             </div>
          </div>
          <div className="flex-1 text-center md:text-left md:pl-4">
             <h2 className="text-sm font-bold text-slate-200 tracking-tight">dhii-mail <span className="text-slate-600">/</span> {activeModule}</h2>
          </div>
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${user ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-amber-500/10 border-amber-500/20 text-amber-400'}`}>
               <div className={`size-1.5 rounded-full ${user ? 'bg-emerald-500' : 'bg-amber-500'} animate-pulse`}></div>
               <span className="text-[10px] font-bold uppercase tracking-wider">{user ? 'Online' : 'Guest'}</span>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto no-scrollbar scroll-smooth p-4 md:p-0" ref={scrollRef}>
          <div className="max-w-4xl mx-auto px-2 md:px-8 py-8 flex flex-col gap-8">
             
             {messages.map((msg, index) => {
               // Only render the widget if this is the absolute LAST message that has a widget
               const isLatestWidget = index === lastWidgetIndex;
               // If a widget exists but it's not the latest, we show a small tag instead
               const showCollapsedTag = msg.widget && msg.widget !== 'NONE' && !isLatestWidget;

               return (
                 <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} animate-in fade-in slide-in-from-bottom-4 duration-500`}>
                    
                    <div className={`max-w-[85%] md:max-w-[70%] px-6 py-4 rounded-[1.5rem] text-sm md:text-base leading-relaxed shadow-lg backdrop-blur-md ${
                      msg.role === 'user' 
                      ? 'bg-primary text-white rounded-tr-none font-medium shadow-primary/20' 
                      : 'bg-[#131620]/90 border border-white/5 text-slate-200 rounded-tl-none shadow-black/50'
                    }`}>
                       <p className="whitespace-pre-line">{msg.text}</p>
                       {/* Render Collapsed Tag if old */}
                       {showCollapsedTag && (
                         <div className="mt-2 pt-2 border-t border-white/5">
                           <span className="text-[9px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-1">
                             <span className="material-symbols-outlined text-[10px]">history</span>
                             {msg.widget} NODE [ARCHIVED]
                           </span>
                         </div>
                       )}
                    </div>

                    <span className="text-[10px] font-bold text-slate-600 mt-2 mb-1 uppercase tracking-widest px-2">
                      {msg.role === 'user' ? 'You' : 'dhii Agent'} • {msg.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </span>

                    {/* ONLY Render Active Widget */}
                    {isLatestWidget && msg.widget && msg.widget !== 'NONE' && (
                      <div className="w-full mt-2 mb-6 pl-0 md:pl-0 animate-in zoom-in-95 duration-500 origin-top-left">
                         {renderWidget(msg.widget)}
                      </div>
                    )}
                 </div>
               );
             })}
             
             {isTyping && (
               <div className="flex items-center gap-2 text-slate-500 px-4">
                  <span className="size-1.5 bg-slate-500 rounded-full animate-bounce"></span>
                  <span className="size-1.5 bg-slate-500 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                  <span className="size-1.5 bg-slate-500 rounded-full animate-bounce [animation-delay:0.4s]"></span>
               </div>
             )}

             <div className="h-24"></div>
          </div>
        </main>

        <footer className="absolute bottom-0 left-0 right-0 p-4 md:p-6 bg-gradient-to-t from-[#020307] via-[#020307] to-transparent z-40">
           <div className="max-w-3xl mx-auto relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-primary to-accent rounded-[2rem] opacity-20 blur group-hover:opacity-40 transition-opacity duration-500"></div>
              <div className="relative flex items-center bg-[#0F111A] border border-white/10 rounded-[2rem] shadow-2xl overflow-hidden">
                 <input 
                   className="flex-1 bg-transparent border-none text-white placeholder-slate-500 px-6 py-4 focus:ring-0 text-base"
                   placeholder={user ? "Command the stream..." : "Type 'Login' to begin..."}
                   value={inputValue}
                   onChange={(e) => setInputValue(e.target.value)}
                   onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                   disabled={isTyping}
                   autoFocus
                 />
                 <button 
                   onClick={handleSendMessage}
                   disabled={!inputValue.trim() || isTyping}
                   className="mr-2 p-2 rounded-full bg-white/5 hover:bg-primary text-slate-400 hover:text-white transition-all disabled:opacity-50"
                 >
                   <span className="material-symbols-outlined">arrow_upward</span>
                 </button>
              </div>
           </div>
        </footer>
      </div>
    </div>
  );
};

export default WorkspaceShell;
