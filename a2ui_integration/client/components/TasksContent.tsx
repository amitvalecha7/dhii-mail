
import React, { useEffect, useState } from 'react';
import { User, AppScreen } from '../types';
import { kernelBridge } from '../services/kernelBridge';

interface TasksContentProps {
  user: User;
  onNavigate: (screen: AppScreen) => void;
}

const TasksContent: React.FC<TasksContentProps> = ({ user, onNavigate }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await kernelBridge.fetchState('tasks');
        setData(response.data || response);
      } catch (error) {
        console.error('Failed to load tasks data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
      return <div className="flex-1 flex items-center justify-center text-slate-400">Loading System Tasks...</div>;
  }

  const criticalPath = data?.critical_path || {
    title: 'No Critical Tasks',
    due_in: 'N/A',
    description: 'All systems nominal.'
  };

  const scheduledJobs = data?.scheduled_jobs || [];

  return (
    <div className="flex-1 flex flex-col p-10 overflow-y-auto no-scrollbar relative z-10">
      <header className="mb-10">
        <h1 className="text-4xl font-extrabold tracking-tighter font-display text-gradient">System Tasks.</h1>
        <p className="text-slate-500 font-medium">Your agentic to-do list for today.</p>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <section className="space-y-6">
           <h3 className="text-xs font-black uppercase tracking-[0.3em] text-slate-600 mb-4 pl-2">Critical Path</h3>
           <div className="liquid-glass rounded-[2.5rem] p-8 border-l-4 border-l-red-500">
              <div className="flex justify-between items-start mb-6">
                 <div>
                   <h4 className="text-xl font-bold text-white mb-1">{criticalPath.title}</h4>
                   <p className="text-slate-500 text-xs font-bold uppercase tracking-widest flex items-center gap-1">
                     <span className="material-symbols-outlined text-[14px]">warning</span>
                     Due in {criticalPath.due_in}
                   </p>
                 </div>
                 <div className="size-12 rounded-2xl bg-red-500/10 flex items-center justify-center text-red-400">
                   <span className="material-symbols-outlined">finance</span>
                 </div>
              </div>
              <p className="text-slate-400 text-sm mb-8 leading-relaxed">{criticalPath.description}</p>
              <button className="w-full h-12 rounded-2xl bg-white/5 border border-white/5 text-slate-200 text-sm font-black uppercase tracking-widest hover:bg-white/10 transition-all">Mark Processed</button>
           </div>
        </section>

        <section className="space-y-6">
           <h3 className="text-xs font-black uppercase tracking-[0.3em] text-slate-600 mb-4 pl-2">Scheduled Jobs</h3>
           <div className="space-y-4">
              {scheduledJobs.map((task: any, idx: number) => (
                <div key={idx} className="liquid-glass rounded-3xl p-5 flex items-center justify-between glow-hover transition-all">
                  <div className="flex items-center gap-4">
                    <div className="size-10 rounded-xl bg-white/5 flex items-center justify-center text-slate-500">
                      <span className="material-symbols-outlined text-[20px]">{task.icon}</span>
                    </div>
                    <div>
                      <h5 className="text-white font-bold text-sm">{task.title}</h5>
                      <span className="text-[9px] font-black uppercase tracking-widest text-slate-600">{task.label}</span>
                    </div>
                  </div>
                  <button className="size-8 rounded-lg border border-white/10 flex items-center justify-center text-slate-600 hover:text-primary transition-colors">
                    <span className="material-symbols-outlined text-[18px]">radio_button_unchecked</span>
                  </button>
                </div>
              ))}
              {scheduledJobs.length === 0 && <div className="text-slate-500 text-sm">No scheduled jobs.</div>}
           </div>
        </section>
      </div>
    </div>
  );
};

export default TasksContent;
