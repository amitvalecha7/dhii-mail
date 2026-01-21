
import React from 'react';
import { User } from '../types';

interface DashboardWidgetProps {
  user: User;
}

const DashboardWidget: React.FC<DashboardWidgetProps> = ({ user }) => {
  return (
    <div className="w-full bg-[#0c0e14] border border-white/5 rounded-3xl p-6 shadow-2xl relative overflow-hidden group">
      {/* Decor */}
      <div className="absolute top-0 right-0 p-10 bg-primary/5 blur-[50px] rounded-full pointer-events-none"></div>
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
             <div className="size-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
                <span className="material-symbols-outlined">grid_view</span>
             </div>
             <div>
                <h3 className="text-lg font-bold text-white">Command Deck</h3>
                <p className="text-[10px] text-slate-400 font-black uppercase tracking-widest">System Overview</p>
             </div>
          </div>
          <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase tracking-widest border border-emerald-500/20">
            Optimal
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
           {/* Stat 1 */}
           <div className="bg-white/5 border border-white/5 rounded-2xl p-4 hover:bg-white/[0.08] transition-colors cursor-pointer">
              <div className="flex justify-between items-start mb-2">
                 <span className="material-symbols-outlined text-slate-400">mail</span>
                 <span className="text-xl font-bold text-white">12</span>
              </div>
              <p className="text-xs text-slate-500 font-medium">Unread Messages</p>
           </div>
           
           {/* Stat 2 */}
           <div className="bg-white/5 border border-white/5 rounded-2xl p-4 hover:bg-white/[0.08] transition-colors cursor-pointer">
              <div className="flex justify-between items-start mb-2">
                 <span className="material-symbols-outlined text-slate-400">event</span>
                 <span className="text-xl font-bold text-white">3</span>
              </div>
              <p className="text-xs text-slate-500 font-medium">Upcoming Events</p>
           </div>
           
           {/* Main Feed Item */}
           <div className="md:col-span-2 bg-gradient-to-r from-primary/10 to-transparent border border-primary/20 rounded-2xl p-5">
              <h4 className="text-sm font-bold text-white mb-1">Morning Briefing Available</h4>
              <p className="text-xs text-slate-400 mb-3">AI has synthesized 4 key updates from your channels.</p>
              <button className="text-xs font-bold text-primary hover:text-white transition-colors flex items-center gap-1">
                 READ SUMMARY <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
              </button>
           </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardWidget;
