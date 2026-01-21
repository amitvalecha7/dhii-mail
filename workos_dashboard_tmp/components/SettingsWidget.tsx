
import React from 'react';
import { User } from '../types';

interface SettingsWidgetProps {
  user: User;
  onLogout: () => void;
}

const SettingsWidget: React.FC<SettingsWidgetProps> = ({ user, onLogout }) => {
  return (
    <div className="w-full bg-[#0c0e14] border border-white/5 rounded-3xl p-6 shadow-2xl overflow-hidden relative animate-in zoom-in-95 duration-500">
      {/* Background Decor */}
      <div className="absolute top-0 right-0 p-20 bg-slate-800/5 blur-[60px] rounded-full pointer-events-none"></div>

      <div className="flex items-center gap-3 mb-6 relative z-10">
        <div className="size-10 rounded-xl bg-slate-800/50 flex items-center justify-center text-slate-400 border border-white/5">
           <span className="material-symbols-outlined">settings</span>
        </div>
        <div>
           <h3 className="text-lg font-bold text-white">System Configuration</h3>
           <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest">Node Settings</p>
        </div>
      </div>

      <div className="space-y-6 relative z-10">
         {/* Profile Card */}
         <div className="p-4 rounded-2xl bg-white/5 border border-white/5 flex items-center gap-4">
            <img src={user.avatar} className="size-12 rounded-full border border-white/10" alt="Profile" />
            <div className="flex-1 min-w-0">
               <h4 className="text-white font-bold text-sm truncate">{user.name}</h4>
               <p className="text-slate-500 text-xs truncate">{user.email}</p>
            </div>
            <button className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-xs font-bold text-slate-300 transition-colors border border-white/5">
               Edit
            </button>
         </div>

         {/* Preferences Section */}
         <div className="space-y-3">
            <label className="text-[10px] font-black uppercase tracking-widest text-slate-600 pl-2">Interface Preferences</label>
            <div className="p-4 rounded-2xl bg-[#0F111A] border border-white/5 space-y-4">
               {/* Toggle 1 */}
               <div className="flex items-center justify-between group cursor-pointer">
                  <div className="flex items-center gap-3">
                     <span className="material-symbols-outlined text-slate-500 text-[20px]">notifications</span>
                     <span className="text-sm font-medium text-slate-300 group-hover:text-white transition-colors">Neural Notifications</span>
                  </div>
                  <div className="w-10 h-6 rounded-full bg-primary p-1 transition-colors"><div className="w-4 h-4 rounded-full bg-white shadow-sm translate-x-4 transition-transform"></div></div>
               </div>
               
               {/* Divider */}
               <div className="h-px bg-white/5 w-full"></div>

               {/* Toggle 2 */}
               <div className="flex items-center justify-between group cursor-pointer">
                  <div className="flex items-center gap-3">
                     <span className="material-symbols-outlined text-slate-500 text-[20px]">sync</span>
                     <span className="text-sm font-medium text-slate-300 group-hover:text-white transition-colors">Auto-Sync Streams</span>
                  </div>
                  <div className="w-10 h-6 rounded-full bg-primary p-1 transition-colors"><div className="w-4 h-4 rounded-full bg-white shadow-sm translate-x-4 transition-transform"></div></div>
               </div>

               {/* Divider */}
               <div className="h-px bg-white/5 w-full"></div>

               {/* Toggle 3 */}
               <div className="flex items-center justify-between group cursor-pointer">
                  <div className="flex items-center gap-3">
                     <span className="material-symbols-outlined text-slate-500 text-[20px]">volume_up</span>
                     <span className="text-sm font-medium text-slate-300 group-hover:text-white transition-colors">Sound Effects</span>
                  </div>
                  <div className="w-10 h-6 rounded-full bg-slate-700 p-1 transition-colors"><div className="w-4 h-4 rounded-full bg-white shadow-sm transition-transform"></div></div>
               </div>
            </div>
         </div>

         {/* Danger Zone */}
         <div className="pt-2">
            <button 
              onClick={onLogout}
              className="w-full py-4 rounded-xl border border-red-500/20 bg-red-500/5 hover:bg-red-500/10 text-red-400 text-xs font-bold uppercase tracking-widest transition-colors flex items-center justify-center gap-2 group"
            >
               <span className="material-symbols-outlined text-[18px] group-hover:rotate-180 transition-transform">power_settings_new</span>
               Terminiate Session (Logout)
            </button>
         </div>
      </div>
    </div>
  );
};

export default SettingsWidget;
