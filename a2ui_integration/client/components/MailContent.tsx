
import React, { useEffect, useState } from 'react';
import { User, AppScreen } from '../types';
import { kernelBridge } from '../services/kernelBridge';

interface MailContentProps {
  user: User;
  onNavigate: (screen: AppScreen) => void;
}

const MailContent: React.FC<MailContentProps> = ({ user, onNavigate }) => {
  const [emails, setEmails] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEmails = async () => {
      try {
        const response = await kernelBridge.fetchState('email/inbox');
        // Handle UIResponse structure (response.data) or direct data
        const data = response.data || response;
        // Handle both direct array or nested object structure
        const emailList = Array.isArray(data) ? data : (data.emails || []);
        setEmails(emailList);
      } catch (error) {
        console.error('Failed to load emails:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEmails();
  }, []);

  if (loading) {
     return <div className="flex-1 flex items-center justify-center text-slate-400">Loading Inbox Stream...</div>;
  }

  return (
    <div className="flex-1 flex flex-col p-10 overflow-y-auto no-scrollbar relative z-10">
      <header className="mb-10 flex items-end justify-between">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tighter font-display text-gradient">Inbox Stream.</h1>
          <p className="text-slate-500 font-medium">Monitoring your communication channels.</p>
        </div>
        <button className="h-12 px-6 rounded-2xl bg-primary text-white text-sm font-black uppercase tracking-widest flex items-center gap-2 hover:bg-blue-600 transition-all shadow-lg shadow-primary/20">
          <span className="material-symbols-outlined text-[20px]">edit</span>
          Compose
        </button>
      </header>

      <div className="space-y-6">
        {emails.map((email: any, idx: number) => (
          <div key={email.id || idx} className="liquid-glass rounded-[2rem] p-6 glow-hover transition-all flex items-start gap-6 cursor-pointer border border-white/5 hover:border-primary/20">
             <div className="size-12 rounded-2xl border border-white/10 overflow-hidden flex-shrink-0">
                 <div className="size-full bg-slate-800 flex items-center justify-center font-bold text-slate-400">
                    {(email.from || email.sender || '?')[0]}
                 </div>
             </div>
             <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                   <h4 className="text-white font-bold text-lg">{email.from || email.sender}</h4>
                   <span className="text-slate-500 text-[10px] font-black uppercase tracking-widest">{email.date || 'Today'}</span>
                </div>
                <h5 className="text-primary font-bold text-sm mb-2 uppercase tracking-tighter">{email.subject}</h5>
                <p className="text-slate-400 text-sm line-clamp-2 leading-relaxed">{email.snippet || email.body_preview || 'No preview available'}</p>
             </div>
             <div className="flex flex-col items-end gap-2">
                <button className="size-10 rounded-xl hover:bg-white/5 text-slate-500 transition-colors flex items-center justify-center">
                  <span className="material-symbols-outlined">more_vert</span>
                </button>
             </div>
          </div>
        ))}
        {emails.length === 0 && (
            <div className="text-center text-slate-500 py-10">No emails found in inbox.</div>
        )}
      </div>
    </div>
  );
};

export default MailContent;
