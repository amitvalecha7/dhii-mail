
import React, { useState, useMemo } from 'react';

interface Email {
  id: number;
  sender: string;
  to: string; // Added 'to' field for sent folder logic
  time: string;
  subject: string;
  body: string; // Added body content
  snippet: string;
  hasAttach: boolean;
  read: boolean;
  label: string;
  folder: 'inbox' | 'sent' | 'drafts' | 'trash' | 'starred';
}

const MailWidget: React.FC = () => {
  const [activeFolder, setActiveFolder] = useState<string>('inbox');
  const [view, setView] = useState<'list' | 'detail' | 'compose'>('list');
  const [selectedEmailId, setSelectedEmailId] = useState<number | null>(null);
  
  // Compose State
  const [composeTo, setComposeTo] = useState('');
  const [composeSubject, setComposeSubject] = useState('');
  const [composeBody, setComposeBody] = useState('');

  const [emails, setEmails] = useState<Email[]>([
    { 
      id: 1, 
      sender: 'Sarah Jenkins', 
      to: 'me',
      time: '10:42 AM', 
      subject: 'Q3 Marketing Deck v2', 
      body: 'Hi Alex,\n\nAttached are the final assets for the campaign launch. Please review the color palettes on slide 4 specifically.\n\nBest,\nSarah',
      snippet: 'Attached are the final assets for the campaign launch...', 
      hasAttach: true, 
      read: false, 
      label: 'Work',
      folder: 'inbox'
    },
    { 
      id: 2, 
      sender: 'Jira Automator', 
      to: 'me',
      time: '09:15 AM', 
      subject: '[JIRA] Issue UX-492 Updated', 
      body: 'User Mike changed status to In Progress.\n\nComments: "Started working on the sidebar navigation component."',
      snippet: 'Mike changed status to In Progress. New comments added.', 
      hasAttach: false, 
      read: true, 
      label: 'System',
      folder: 'inbox'
    },
    { 
      id: 3, 
      sender: 'Alex Chen', 
      to: 'partners@acme.com',
      time: 'Yesterday', 
      subject: 'Strategic Partnership Review', 
      body: 'Team,\n\nI have attached the proposal for the upcoming Q4 expansion. Let\'s discuss this in the Monday sync.\n\nRegards,\nAlex',
      snippet: 'I have attached the proposal for the upcoming Q4 expansion...', 
      hasAttach: true, 
      read: true, 
      label: 'Important',
      folder: 'sent'
    },
    { 
      id: 4, 
      sender: 'Stripe', 
      to: 'billing@workos.com',
      time: 'Yesterday', 
      subject: 'Invoice #10239 Payment Succeeded', 
      body: 'Your payment for $299.00 USD has been processed. Receipt attached.',
      snippet: 'Your payment for $299.00 USD has been processed...', 
      hasAttach: false, 
      read: true, 
      label: 'Finance',
      folder: 'inbox'
    }
  ]);

  const filteredEmails = useMemo(() => {
    return emails.filter(e => {
        if (activeFolder === 'starred') return false; // Mock implementation
        return e.folder === activeFolder;
    });
  }, [emails, activeFolder]);

  const selectedEmail = useMemo(() => emails.find(e => e.id === selectedEmailId), [emails, selectedEmailId]);

  const handleComposeSend = () => {
    const newEmail: Email = {
        id: Date.now(),
        sender: 'Alex Chen',
        to: composeTo,
        time: 'Just now',
        subject: composeSubject,
        body: composeBody,
        snippet: composeBody.substring(0, 40) + '...',
        hasAttach: false,
        read: true,
        label: 'Work',
        folder: 'sent'
    };
    setEmails(prev => [newEmail, ...prev]);
    setView('list');
    setActiveFolder('sent');
    // Reset form
    setComposeTo('');
    setComposeSubject('');
    setComposeBody('');
  };

  const handleDelete = (id: number) => {
    setEmails(prev => prev.map(e => e.id === id ? { ...e, folder: 'trash' } : e));
    if (view === 'detail') setView('list');
  };

  const handleNavClick = (folder: string) => {
    setActiveFolder(folder);
    setView('list');
    setSelectedEmailId(null);
  };

  const NavItem = ({ id, icon, label, count }: { id: string, icon: string, label: string, count?: number }) => (
    <button 
      onClick={() => handleNavClick(id)}
      className={`w-full flex items-center justify-between px-4 py-2.5 rounded-xl transition-all ${
        activeFolder === id 
        ? 'bg-primary/10 text-primary font-bold' 
        : 'text-slate-400 hover:text-white hover:bg-white/5'
      }`}
    >
      <div className="flex items-center gap-3">
        <span className="material-symbols-outlined text-[20px]">{icon}</span>
        <span className="text-sm">{label}</span>
      </div>
      {count && <span className="text-[10px] font-bold bg-white/10 px-1.5 py-0.5 rounded">{count}</span>}
    </button>
  );

  return (
    <div className="w-full h-[600px] bg-[#0c0e14] border border-white/5 rounded-3xl overflow-hidden shadow-2xl flex relative">
      {/* LEFT SIDEBAR */}
      <div className="w-56 bg-[#0f111a] border-r border-white/5 flex flex-col p-4 shrink-0">
         <button 
            onClick={() => setView('compose')}
            className="w-full bg-white text-black hover:bg-slate-200 transition-colors rounded-xl py-3 font-bold text-sm flex items-center justify-center gap-2 mb-6 shadow-lg shadow-white/5"
         >
            <span className="material-symbols-outlined text-[18px]">edit</span>
            Compose
         </button>

         <div className="space-y-1 flex-1">
            <NavItem id="inbox" icon="inbox" label="Inbox" count={emails.filter(e => e.folder === 'inbox' && !e.read).length} />
            <NavItem id="starred" icon="star" label="Starred" />
            <NavItem id="sent" icon="send" label="Sent" />
            <NavItem id="drafts" icon="draft" label="Drafts" />
            <NavItem id="trash" icon="delete" label="Trash" />
            <div className="h-px bg-white/5 my-2 mx-4"></div>
            <p className="px-4 text-[10px] font-black text-slate-600 uppercase tracking-widest mb-2 mt-2">Labels</p>
            <NavItem id="work" icon="work" label="Work" />
            <NavItem id="finance" icon="receipt" label="Finance" />
         </div>
      </div>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col bg-[#0c0e14] relative overflow-hidden">
         
         {/* -- VIEW: LIST -- */}
         {view === 'list' && (
            <>
                <div className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-[#0c0e14]/50 backdrop-blur-sm sticky top-0 z-10">
                    <div className="flex items-center gap-4">
                        <h3 className="text-white font-bold text-lg capitalize">{activeFolder}</h3>
                    </div>
                    <div className="relative">
                        <input className="bg-[#0f111a] border border-white/10 rounded-lg pl-9 pr-4 py-1.5 text-xs text-white focus:outline-none focus:border-primary/50 w-48 transition-all" placeholder="Search mail..." />
                        <span className="material-symbols-outlined absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500 text-[16px]">search</span>
                    </div>
                </div>
                
                <div className="flex-1 overflow-y-auto p-2 space-y-1">
                    {filteredEmails.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-60">
                            <span className="material-symbols-outlined text-4xl mb-2">inbox</span>
                            <p className="text-xs font-bold uppercase tracking-widest">Folder Empty</p>
                        </div>
                    ) : (
                        filteredEmails.map((email) => (
                        <div 
                            key={email.id} 
                            onClick={() => {
                                setSelectedEmailId(email.id);
                                setView('detail');
                                setEmails(prev => prev.map(e => e.id === email.id ? { ...e, read: true } : e));
                            }}
                            className={`group flex items-start gap-4 p-4 rounded-xl cursor-pointer border border-transparent hover:border-white/5 hover:bg-white/[0.02] transition-all ${!email.read ? 'bg-white/[0.02]' : ''}`}
                        >
                            <div className="mt-1">
                                <div className={`size-5 rounded border flex items-center justify-center transition-colors ${!email.read ? 'border-primary bg-primary/20 text-primary' : 'border-slate-700 text-transparent hover:border-slate-500'}`}>
                                    {email.read && <span className="material-symbols-outlined text-[14px]">check</span>}
                                </div>
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex justify-between items-center mb-1">
                                    <span className={`text-sm ${!email.read ? 'font-bold text-white' : 'font-medium text-slate-300'}`}>{email.sender}</span>
                                    <span className="text-[10px] text-slate-500 font-mono">{email.time}</span>
                                </div>
                                <h4 className={`text-xs mb-1 truncate ${!email.read ? 'text-white font-semibold' : 'text-slate-400'}`}>{email.subject}</h4>
                                <p className="text-xs text-slate-500 truncate">{email.snippet}</p>
                            </div>
                            <div className="flex flex-col items-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                {email.hasAttach && <span className="material-symbols-outlined text-slate-500 text-[16px]">attachment</span>}
                                <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-white/5 text-slate-400 border border-white/5">{email.label}</span>
                            </div>
                        </div>
                        ))
                    )}
                </div>
            </>
         )}

         {/* -- VIEW: DETAIL -- */}
         {view === 'detail' && selectedEmail && (
            <div className="flex flex-col h-full animate-in slide-in-from-right-4 duration-300">
                <div className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-[#0c0e14]/50 backdrop-blur-sm">
                   <div className="flex items-center gap-3">
                      <button onClick={() => setView('list')} className="size-8 rounded-lg hover:bg-white/10 flex items-center justify-center text-slate-400 hover:text-white transition-colors">
                         <span className="material-symbols-outlined">arrow_back</span>
                      </button>
                      <div className="h-4 w-px bg-white/10"></div>
                      <button onClick={() => handleDelete(selectedEmail.id)} className="size-8 rounded-lg hover:bg-white/10 flex items-center justify-center text-slate-400 hover:text-red-400 transition-colors" title="Delete">
                         <span className="material-symbols-outlined text-[20px]">delete</span>
                      </button>
                      <button className="size-8 rounded-lg hover:bg-white/10 flex items-center justify-center text-slate-400 hover:text-white transition-colors" title="Archive">
                         <span className="material-symbols-outlined text-[20px]">archive</span>
                      </button>
                   </div>
                   <span className="text-xs text-slate-500 font-mono">{selectedEmail.time}</span>
                </div>
                
                <div className="flex-1 p-8 overflow-y-auto">
                    <h1 className="text-2xl font-bold text-white mb-6 leading-tight">{selectedEmail.subject}</h1>
                    <div className="flex items-center gap-4 mb-8">
                        <div className="size-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-sm">
                            {selectedEmail.sender[0]}
                        </div>
                        <div>
                            <p className="text-sm font-bold text-white">{selectedEmail.sender}</p>
                            <p className="text-xs text-slate-500">to {selectedEmail.to}</p>
                        </div>
                    </div>
                    <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
                        {selectedEmail.body}
                    </div>
                    {selectedEmail.hasAttach && (
                        <div className="mt-8 pt-6 border-t border-white/5">
                            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Attachments</p>
                            <div className="flex gap-3">
                                <div className="p-3 rounded-xl border border-white/10 bg-white/5 flex items-center gap-3 cursor-pointer hover:bg-white/10 transition-colors">
                                    <span className="material-symbols-outlined text-red-400">picture_as_pdf</span>
                                    <div>
                                        <p className="text-xs font-bold text-white">Proposal_v2.pdf</p>
                                        <p className="text-[10px] text-slate-500">2.4 MB</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
         )}

         {/* -- VIEW: COMPOSE -- */}
         {view === 'compose' && (
            <div className="flex flex-col h-full animate-in slide-in-from-bottom-4 duration-300 bg-[#0c0e14]">
                <div className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-[#0c0e14]/50 backdrop-blur-sm">
                   <h3 className="text-white font-bold text-lg">New Message</h3>
                   <button onClick={() => setView('list')} className="size-8 rounded-lg hover:bg-white/10 flex items-center justify-center text-slate-400 hover:text-white transition-colors">
                      <span className="material-symbols-outlined">close</span>
                   </button>
                </div>
                
                <div className="flex-1 p-6 flex flex-col gap-4">
                    <input 
                        className="bg-transparent border-b border-white/10 px-2 py-3 text-sm text-white focus:outline-none focus:border-primary placeholder:text-slate-600 transition-colors"
                        placeholder="To:"
                        value={composeTo}
                        onChange={(e) => setComposeTo(e.target.value)}
                    />
                    <input 
                        className="bg-transparent border-b border-white/10 px-2 py-3 text-sm text-white focus:outline-none focus:border-primary placeholder:text-slate-600 transition-colors"
                        placeholder="Subject:"
                        value={composeSubject}
                        onChange={(e) => setComposeSubject(e.target.value)}
                    />
                    <textarea 
                        className="flex-1 bg-transparent border-none px-2 py-3 text-sm text-white focus:outline-none placeholder:text-slate-600 resize-none"
                        placeholder="Write your message..."
                        value={composeBody}
                        onChange={(e) => setComposeBody(e.target.value)}
                    />
                    <div className="flex items-center justify-between pt-4 border-t border-white/5">
                        <div className="flex gap-2">
                            <button className="size-8 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white flex items-center justify-center transition-colors">
                                <span className="material-symbols-outlined text-[20px]">attach_file</span>
                            </button>
                            <button className="size-8 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white flex items-center justify-center transition-colors">
                                <span className="material-symbols-outlined text-[20px]">image</span>
                            </button>
                        </div>
                        <button 
                            onClick={handleComposeSend}
                            disabled={!composeTo || !composeSubject}
                            className="bg-primary hover:bg-blue-600 disabled:opacity-50 text-white rounded-lg px-6 py-2 text-sm font-bold shadow-lg shadow-primary/20 transition-all flex items-center gap-2"
                        >
                            Send <span className="material-symbols-outlined text-[16px]">send</span>
                        </button>
                    </div>
                </div>
            </div>
         )}

      </div>
    </div>
  );
};

export default MailWidget;
