
import React, { useEffect, useState } from 'react';
import { User, AppScreen } from '../types';
import { kernelBridge } from '../services/kernelBridge';

interface MeetingsContentProps {
  user: User;
  onNavigate: (screen: AppScreen) => void;
}

const MeetingsContent: React.FC<MeetingsContentProps> = ({ user, onNavigate }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await kernelBridge.fetchState('meetings');
        setData(response.data || response);
      } catch (error) {
        console.error('Failed to load meetings data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
      return <div className="flex-1 flex items-center justify-center text-slate-400">Loading Neural Events...</div>;
  }

  const activeSession = data?.active_session || {
    title: 'No Active Session',
    time_range: '--:-- --',
    participants_count: 0
  };

  const timeline = data?.timeline || [];

  return (
    <div className="flex-1 flex flex-col p-10 overflow-y-auto no-scrollbar relative z-10">
      <header className="mb-10 flex items-end justify-between">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tighter font-display text-gradient">Neural Events.</h1>
          <p className="text-slate-500 font-medium">Synchronized schedule across all nodes.</p>
        </div>
        <div className="flex gap-2">
          <button className="size-12 rounded-2xl liquid-glass flex items-center justify-center text-slate-400 hover:text-white transition-all"><span className="material-symbols-outlined">search</span></button>
          <button className="h-12 px-6 rounded-2xl bg-white text-black text-sm font-black uppercase tracking-widest flex items-center gap-2 hover:bg-slate-200 transition-all">New Event</button>
        </div>
      </header>

      <div className="space-y-12">
        <section>
          <div className="flex items-center justify-between mb-6 px-2">
            <h2 className="text-xl font-bold text-white font-display">Active Session</h2>
            <span className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.2em] animate-pulse">Live Now</span>
          </div>
          <div className="liquid-glass rounded-[3rem] overflow-hidden p-8 border border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
             <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8">
                <div className="space-y-4">
                   <div>
                     <span className="text-xs font-black text-slate-500 uppercase tracking-[0.3em]">{activeSession.time_range}</span>
                     <h3 className="text-3xl font-extrabold text-white mt-1 tracking-tighter">{activeSession.title}</h3>
                   </div>
                   <div className="flex -space-x-3">
                      {[1, 2, 3, 4].map(i => (
                        <div key={i} className="size-10 rounded-full border-4 border-[#0a0c10] bg-slate-700"></div>
                      ))}
                      <div className="size-10 rounded-full border-4 border-[#0a0c10] bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-500">+{activeSession.participants_count}</div>
                   </div>
                </div>
                <div className="flex items-center gap-4">
                   <button className="h-14 px-8 rounded-2xl bg-primary text-white text-sm font-black uppercase tracking-widest shadow-xl shadow-primary/30 hover:scale-105 transition-transform">Enter Huddle</button>
                   <button className="size-14 rounded-2xl liquid-glass flex items-center justify-center text-slate-400 hover:text-white transition-all"><span className="material-symbols-outlined">share</span></button>
                </div>
             </div>
          </div>
        </section>

        <section>
           <h3 className="text-xs font-black uppercase tracking-[0.3em] text-slate-600 mb-8 pl-2">Timeline Progression</h3>
           <div className="relative pl-8 border-l border-white/10 space-y-12 ml-4">
              {timeline.map((item: any, idx: number) => (
                <div key={idx} className="relative">
                  <div className="absolute -left-[37px] top-0 size-4 rounded-full bg-slate-800 ring-8 ring-background-dark border-2 border-slate-700"></div>
                  <div className="liquid-glass rounded-3xl p-6 glow-hover transition-all max-w-2xl">
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1 block">{item.time}</span>
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="text-lg font-bold text-slate-200">{item.title}</h4>
                      <span className="px-2 py-0.5 rounded bg-white/5 text-[9px] font-black uppercase tracking-tighter text-slate-400">{item.tag}</span>
                    </div>
                    <p className="text-slate-500 text-sm">{item.desc}</p>
                  </div>
                </div>
              ))}
              {timeline.length === 0 && <div className="text-slate-500 text-sm">No upcoming events.</div>}
           </div>
        </section>
      </div>
    </div>
  );
};

export default MeetingsContent;
