
import React from 'react';
import { User, AppScreen } from '../types';

interface MailContentProps {
  user: User;
  onNavigate: (screen: AppScreen) => void;
}

const MailContent: React.FC<MailContentProps> = ({ user, onNavigate }) => {
  const emails = [
    { id: 1, sender: 'Sarah Jenkins', time: '12m ago', subject: 'Q3 Marketing Deck v2', snippet: 'Finalizing the banners and the social copy. Let me know if you approve.', priority: 'Action Required', avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCBHA6zcg5qQo8eP1CwhuoU6NZGaGbBDo03Zjzo-EtSRk7m_Rm5xAj9q_rf_w30OWdIMnJH28rylGX99qBhZ-dMVPnXwolxN8z5MAUaqbfPaGwgqFErPN3smXRa4-iHe09QLzDPv6ID94954okJVsjIfZTpl400S4efQlD_YIJp59y-If83ojduu54-Umf1e7WjuZY_mIfom2qRJGfLQ62hNWF8Jln1wH2uGOexm6C0rL6KnuH8cu3qozPJjo8vMNKnM6xGei_0vi-4' },
    { id: 2, sender: 'Jira Automator', time: '9:15 AM', subject: '[JIRA] Issue UX-492 Updated', snippet: 'Mike changed status to In Progress. New comments added.', priority: 'Update', isBot: true },
    { id: 3, sender: 'Alex Chen', time: 'Yesterday', subject: 'Strategic Partnership Review', snippet: 'I have attached the proposal for the upcoming Q4 expansion.', priority: 'General', avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAc9ht1U7lXkGwxPKu8kzjuTnprZAKX4CQe8sq3nvhzS6HMysFqGK9_FY1s-ftZRLDHBpR6mKm1231xjVj-Ve_O8DNwwq_b75Orf1dauATx5JsPyeWATbio-6EWRz5062kB4TgAkWj3vjoHxkPC3CiOrefQpcC9XwGaLNsmFGpR4aunmYnTfdAIbgr4Cb__l7d0vLgaFaDBw0ohxg4jS0BCptwfFJ6Z6JFzi3wSEf4RWMmc_MhDYnVS1LHzsmxoxP6-M4JlTZtGVr-Y' }
  ];

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
        {emails.map((email) => (
          <div key={email.id} className="liquid-glass rounded-[2rem] p-6 glow-hover transition-all flex items-start gap-6 cursor-pointer border border-white/5 hover:border-primary/20">
             <div className="size-12 rounded-2xl border border-white/10 overflow-hidden flex-shrink-0">
               {email.isBot ? (
                 <div className="size-full bg-blue-500/10 flex items-center justify-center text-blue-400">
                    <span className="material-symbols-outlined text-[24px]">smart_toy</span>
                 </div>
               ) : (
                 <img src={email.avatar} className="size-full object-cover" alt="" />
               )}
             </div>
             <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                   <h4 className="text-white font-bold text-lg">{email.sender}</h4>
                   <span className="text-slate-500 text-[10px] font-black uppercase tracking-widest">{email.time}</span>
                </div>
                <h5 className="text-primary font-bold text-sm mb-2 uppercase tracking-tighter">{email.subject}</h5>
                <p className="text-slate-400 text-sm line-clamp-2 leading-relaxed">{email.snippet}</p>
             </div>
             <div className="flex flex-col items-end gap-2">
                <span className={`px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest ${
                  email.priority === 'Action Required' ? 'bg-red-500/10 text-red-400' : 'bg-slate-800 text-slate-400'
                }`}>{email.priority}</span>
                <button className="size-10 rounded-xl hover:bg-white/5 text-slate-500 transition-colors flex items-center justify-center">
                  <span className="material-symbols-outlined">more_vert</span>
                </button>
             </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MailContent;
