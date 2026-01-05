
import React from 'react';
import { User, AppScreen } from '../types';

interface DashboardScreenProps {
  user: User;
  onNavigate: (screen: AppScreen) => void;
}

const DashboardScreen: React.FC<DashboardScreenProps> = ({ user, onNavigate }) => {
  return (
    <div className="flex-1 flex flex-col p-10 overflow-y-auto no-scrollbar relative z-10">
      <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-1">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tighter font-display text-gradient">System Overdrive.</h1>
          <p className="text-slate-500 font-medium">Ready for deployment, Commander {user.name.split(' ')[0]}.</p>
        </div>
        <div className="px-4 py-2 rounded-full liquid-glass border-white/5 flex items-center gap-2">
          <span className="size-2 rounded-full bg-indigo-500 animate-pulse"></span>
          <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Neural Integrity: 99.8%</span>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
        
        {/* Morning Briefing Card */}
        <div className="xl:col-span-2 liquid-glass rounded-[2.5rem] p-8 glow-hover transition-all animate-float">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <div className="size-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                <span className="material-symbols-outlined">summarize</span>
              </div>
              <div>
                <h3 className="text-xl font-extrabold font-display tracking-tight">Morning Briefing</h3>
                <p className="text-slate-500 text-[10px] font-black uppercase tracking-widest">Synthesized Intelligence</p>
              </div>
            </div>
          </div>
          <div className="space-y-4">
            <div className="p-6 rounded-3xl bg-white/5 border border-white/5 hover:bg-white/[0.08] transition-all cursor-pointer group">
              <p className="text-slate-300 text-sm leading-relaxed">
                <span className="text-primary font-bold">Inbox Alert:</span> 3 high-impact threads require review. Sarah's Q3 deck needs approval before 2 PM.
              </p>
            </div>
            <div className="p-6 rounded-3xl bg-white/5 border border-white/5 flex items-center justify-between">
              <p className="text-slate-400 text-sm font-medium">Draft summary for Product meeting?</p>
              <button className="px-5 py-2.5 rounded-xl bg-primary/10 text-primary text-xs font-black hover:bg-primary/20 transition-all uppercase tracking-widest">Execute</button>
            </div>
          </div>
        </div>

        {/* Unread Emails Card */}
        <div className="liquid-glass rounded-[2.5rem] p-8 glow-hover transition-all">
          <div className="flex items-center justify-between mb-8">
            <h3 className="text-xl font-extrabold font-display tracking-tight">Priority Feed</h3>
            <span className="text-[10px] font-black bg-primary/20 text-primary px-2 py-0.5 rounded-full uppercase tracking-tighter">Live</span>
          </div>
          <div className="space-y-4">
            {[
              { sender: 'Sarah Jenkins', subject: 'Q3 Marketing Assets', time: '12m' },
              { sender: 'Linear Neural', subject: 'Issue: UI Interpolation', time: '1h' },
              { sender: 'GitHub Bot', subject: 'Production Deployed', time: '2h' }
            ].map((item, idx) => (
              <div key={idx} className="flex items-center gap-4 p-3 rounded-2xl hover:bg-white/5 transition-all cursor-pointer group">
                <div className="size-10 rounded-xl bg-white/5 border border-white/5 flex items-center justify-center font-bold text-slate-500 group-hover:border-primary/50 group-hover:text-primary transition-all">
                  {item.sender[0]}
                </div>
                <div className="flex-1 overflow-hidden">
                  <p className="text-sm font-bold truncate text-slate-200">{item.sender}</p>
                  <p className="text-xs text-slate-500 truncate">{item.subject}</p>
                </div>
                <span className="text-[10px] font-bold text-slate-600 shrink-0">{item.time}</span>
              </div>
            ))}
            <button onClick={() => onNavigate('MAIL')} className="w-full py-4 mt-2 rounded-2xl border border-dashed border-white/10 text-slate-500 text-[10px] font-black uppercase tracking-[0.2em] hover:border-primary/50 hover:text-slate-300 transition-all">View All Nodes</button>
          </div>
        </div>

        {/* Schedule Card */}
        <div className="xl:col-span-3 liquid-glass rounded-[2.5rem] p-8 glow-hover transition-all">
          <div className="flex items-center justify-between mb-8">
            <h3 className="text-xl font-extrabold font-display tracking-tight text-gradient">Schedule Overdrive</h3>
            <button className="text-slate-500 text-xs font-black uppercase tracking-widest hover:text-white">Full Timeline</button>
          </div>
          <div className="flex gap-6 overflow-x-auto no-scrollbar pb-2">
            {[
              { time: '10:00 AM', title: 'Sprint Sync', type: 'internal', status: 'Live' },
              { time: '11:30 AM', title: 'Product Review', type: 'critical', status: 'Upcoming' },
              { time: '02:00 PM', title: 'Hiring: Lead Designer', type: 'external', status: 'Upcoming' },
              { time: '04:30 PM', title: 'Focus Session', type: 'internal', status: 'Scheduled' }
            ].map((meet, idx) => (
              <div key={idx} className="min-w-[300px] p-6 rounded-3xl bg-white/5 border border-white/5 hover:border-primary/30 transition-all flex flex-col justify-between h-[180px] relative group overflow-hidden">
                <div className="absolute top-0 right-0 p-6 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity">
                  <span className="material-symbols-outlined text-6xl">calendar_month</span>
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{meet.time}</span>
                    {meet.status === 'Live' && <span className="size-1.5 rounded-full bg-red-500 animate-pulse"></span>}
                  </div>
                  <h4 className="text-lg font-bold text-slate-100">{meet.title}</h4>
                </div>
                <div className="flex items-center justify-between mt-4">
                  <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest ${
                    meet.type === 'critical' ? 'bg-red-500/10 text-red-400' : 'bg-primary/10 text-primary'
                  }`}>{meet.type}</span>
                  <button className="size-11 rounded-2xl bg-white/5 border border-white/5 flex items-center justify-center hover:bg-primary hover:text-white transition-all shadow-xl group-hover:scale-110">
                    <span className="material-symbols-outlined text-[20px]">videocam</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};

export default DashboardScreen;
