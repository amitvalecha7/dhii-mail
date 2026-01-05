
import React, { useState } from 'react';

interface MailConfigScreenProps {
  onComplete: () => void;
  onBack: () => void;
}

const MailConfigScreen: React.FC<MailConfigScreenProps> = ({ onComplete, onBack }) => {
  const [protocol, setProtocol] = useState('incoming');
  const [isConnecting, setIsConnecting] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'failed'>('idle');

  const handleCheck = () => {
    setIsConnecting(true);
    setTimeout(() => {
      setIsConnecting(false);
      setStatus('success');
    }, 1500);
  };

  return (
    <div className="h-screen w-full flex flex-col bg-background-dark overflow-hidden relative">
      <header className="sticky top-0 z-50 flex items-center justify-between p-4 bg-background-dark/90 backdrop-blur-md border-b border-white/5">
        <button onClick={onBack} className="size-10 flex items-center justify-center rounded-full hover:bg-white/10 transition-colors">
          <span className="material-symbols-outlined">arrow_back</span>
        </button>
        <h2 className="text-lg font-bold flex-1 text-center pr-10">Mail Configuration</h2>
      </header>

      <main className="flex-1 flex flex-col p-4 w-full max-w-lg mx-auto pb-8">
        <div className="mb-6 text-center">
          <p className="text-slate-400 text-sm">Connect your email provider manually to sync your workspace.</p>
        </div>

        <div className="glass-card rounded-xl p-5 flex flex-col gap-5">
          <div className="flex p-1 bg-background-dark/50 rounded-xl">
            <button 
              onClick={() => setProtocol('incoming')}
              className={`flex-1 h-9 flex items-center justify-center rounded-lg text-xs font-medium transition-all ${protocol === 'incoming' ? 'bg-[#2d3748] text-primary shadow-sm' : 'text-slate-400'}`}
            >
              Incoming (IMAP)
            </button>
            <button 
              onClick={() => setProtocol('outgoing')}
              className={`flex-1 h-9 flex items-center justify-center rounded-lg text-xs font-medium transition-all ${protocol === 'outgoing' ? 'bg-[#2d3748] text-primary shadow-sm' : 'text-slate-400'}`}
            >
              Outgoing (SMTP)
            </button>
          </div>

          <div className="flex flex-col gap-4">
            <div className="space-y-1.5">
              <label className="text-slate-300 text-xs font-medium ml-1">Server Hostname</label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 text-[20px]">dns</span>
                <input className="glass-input w-full rounded-lg h-12 pl-11 pr-4 text-sm focus:ring-0" placeholder="imap.gmail.com" type="text" />
              </div>
            </div>

            <div className="flex gap-3">
              <div className="flex flex-col gap-1.5 flex-1">
                <label className="text-slate-300 text-xs font-medium ml-1">Port</label>
                <input className="glass-input w-full rounded-lg h-12 px-4 text-sm focus:ring-0" placeholder="993" type="number" />
              </div>
              <div className="flex flex-col gap-1.5 flex-[1.5]">
                <label className="text-slate-300 text-xs font-medium ml-1">Security</label>
                <div className="relative">
                  <select className="glass-input w-full rounded-lg h-12 px-4 text-sm focus:ring-0 appearance-none cursor-pointer">
                    <option>SSL / TLS</option>
                    <option>STARTTLS</option>
                  </select>
                  <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none">expand_more</span>
                </div>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-slate-300 text-xs font-medium ml-1">Username</label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 text-[20px]">alternate_email</span>
                <input className="glass-input w-full rounded-lg h-12 pl-11 pr-4 text-sm focus:ring-0" placeholder="user@gmail.com" type="text" />
              </div>
            </div>
          </div>

          {status === 'success' && (
            <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3 flex items-start gap-3 animate-in fade-in slide-in-from-top-2">
              <div className="bg-emerald-500 rounded-full p-0.5 mt-0.5"><span className="material-symbols-outlined text-white text-[14px]">check</span></div>
              <div>
                <p className="text-xs font-semibold text-emerald-400">Connection successful!</p>
                <p className="text-[10px] text-emerald-300/80 leading-tight mt-0.5">Redirecting data to your dashboard.</p>
              </div>
            </div>
          )}

          <button 
            onClick={handleCheck}
            disabled={isConnecting}
            className="w-full bg-primary hover:bg-blue-600 disabled:opacity-50 text-white rounded-lg h-12 text-sm font-semibold shadow-lg shadow-blue-900/20 transition-all flex items-center justify-center gap-2 group"
          >
            <span>{isConnecting ? 'Testing...' : 'Check Connection'}</span>
            <span className="material-symbols-outlined text-[18px] group-hover:translate-x-0.5 transition-transform">bolt</span>
          </button>
        </div>

        <div className="mt-6 flex flex-col items-center gap-4">
          <button 
            disabled={status !== 'success'}
            onClick={onComplete}
            className="w-full bg-primary disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-lg h-12 text-sm font-semibold shadow-lg transition-all flex items-center justify-center gap-2"
          >
            <span>Continue to Dashboard</span>
            <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
          <button onClick={onBack} className="text-xs font-medium text-slate-400 hover:text-white transition-colors py-2">Skip configuration for now</button>
        </div>
      </main>
    </div>
  );
};

export default MailConfigScreen;
