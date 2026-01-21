
import React, { useState, useMemo } from 'react';

interface Task {
  id: number;
  title: string;
  due: string;
  tag: string;
  status: 'pending' | 'done';
  priority: 'high' | 'medium' | 'low';
}

const TasksWidget: React.FC = () => {
  const [filter, setFilter] = useState('all');
  const [inputValue, setInputValue] = useState('');
  
  const [tasks, setTasks] = useState<Task[]>([
    { id: 1, title: 'Approve Q3 Budget Report', due: 'Today', tag: 'Finance', status: 'pending', priority: 'high' },
    { id: 2, title: 'Review Candidate Resumes', due: 'Tomorrow', tag: 'Hiring', status: 'pending', priority: 'medium' },
    { id: 3, title: 'Update CI/CD Pipeline Config', due: 'Oct 12', tag: 'DevOps', status: 'done', priority: 'low' },
    { id: 4, title: 'Prepare Board Meeting Slides', due: 'Oct 15', tag: 'Strategy', status: 'pending', priority: 'high' },
  ]);

  const filteredTasks = useMemo(() => {
    return tasks.filter(t => {
        if (filter === 'all') return true;
        if (filter === 'done') return t.status === 'done';
        if (filter === 'today') return t.due === 'Today';
        if (filter === 'critical') return t.priority === 'high';
        return true;
    });
  }, [tasks, filter]);

  const handleAddTask = () => {
    if (!inputValue.trim()) return;
    const newTask: Task = {
        id: Date.now(),
        title: inputValue,
        due: 'Today',
        tag: 'General',
        status: 'pending',
        priority: 'medium'
    };
    setTasks(prev => [newTask, ...prev]);
    setInputValue('');
  };

  const toggleStatus = (id: number) => {
    setTasks(prev => prev.map(t => 
        t.id === id ? { ...t, status: t.status === 'pending' ? 'done' : 'pending' } : t
    ));
  };

  const deleteTask = (id: number) => {
    setTasks(prev => prev.filter(t => t.id !== id));
  };

  const FilterButton = ({ id, label, icon, count }: { id: string, label: string, icon: string, count?: number }) => (
    <button 
      onClick={() => setFilter(id)}
      className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all ${
        filter === id ? 'bg-white/10 text-white font-bold' : 'text-slate-400 hover:text-white hover:bg-white/5'
      }`}
    >
       <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-[20px]">{icon}</span>
          <span className="text-xs uppercase tracking-wide">{label}</span>
       </div>
       {count !== undefined && <span className="text-[10px] opacity-60">{count}</span>}
    </button>
  );

  return (
    <div className="w-full h-[550px] bg-[#0c0e14] border border-white/5 rounded-3xl overflow-hidden shadow-2xl flex relative">
       {/* Sidebar */}
       <div className="w-60 bg-[#0f111a] border-r border-white/5 p-4 flex flex-col shrink-0">
          <h3 className="px-4 text-xs font-black text-slate-500 uppercase tracking-widest mb-6 mt-2">Task Filters</h3>
          <div className="space-y-1 flex-1">
             <FilterButton id="all" label="All Tasks" icon="list" count={tasks.length} />
             <FilterButton id="today" label="Due Today" icon="today" count={tasks.filter(t => t.due === 'Today').length} />
             <FilterButton id="critical" label="Critical" icon="priority_high" count={tasks.filter(t => t.priority === 'high').length} />
             <FilterButton id="done" label="Completed" icon="check_circle" count={tasks.filter(t => t.status === 'done').length} />
          </div>
          <div className="p-4 rounded-2xl bg-gradient-to-br from-primary/20 to-transparent border border-primary/10">
             <div className="flex items-center gap-2 mb-2 text-primary">
                <span className="material-symbols-outlined">auto_awesome</span>
                <span className="text-xs font-bold uppercase">AI Insight</span>
             </div>
             <p className="text-[10px] text-slate-300 leading-relaxed">
                {tasks.filter(t => t.status === 'pending').length} pending tasks. High velocity required to meet Q4 targets.
             </p>
          </div>
       </div>

       {/* Main List */}
       <div className="flex-1 bg-[#0c0e14] flex flex-col">
          <div className="p-6 border-b border-white/5 bg-[#0c0e14]/50 backdrop-blur-sm sticky top-0 z-10">
             <div className="flex gap-3">
                <input 
                  className="flex-1 bg-[#0f111a] border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-primary/50 transition-all placeholder:text-slate-600"
                  placeholder="Add a new task..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddTask()}
                />
                <button 
                    onClick={handleAddTask}
                    className="bg-primary hover:bg-blue-600 text-white rounded-xl px-6 font-bold text-sm shadow-lg shadow-primary/20 transition-all active:scale-95"
                >
                   Add
                </button>
             </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-2">
             {filteredTasks.length === 0 ? (
                 <div className="flex flex-col items-center justify-center h-48 opacity-40">
                    <span className="material-symbols-outlined text-3xl mb-2 text-slate-500">checklist</span>
                    <p className="text-xs font-bold text-slate-400 uppercase">No tasks found</p>
                 </div>
             ) : (
                 filteredTasks.map((task) => (
                    <div key={task.id} className={`group flex items-center gap-4 p-4 rounded-2xl border border-transparent hover:border-white/5 hover:bg-white/[0.02] transition-all cursor-pointer animate-in fade-in slide-in-from-bottom-2 ${task.status === 'done' ? 'opacity-50' : ''}`}>
                    <button 
                        onClick={() => toggleStatus(task.id)}
                        className={`size-6 rounded-full border-2 flex items-center justify-center transition-all ${
                            task.status === 'done' 
                            ? 'bg-emerald-500 border-emerald-500 text-white' 
                            : 'border-slate-600 hover:border-primary hover:bg-primary/20'
                        }`}
                    >
                        {task.status === 'done' && <span className="material-symbols-outlined text-[14px]">check</span>}
                    </button>
                    
                    <div className="flex-1" onClick={() => toggleStatus(task.id)}>
                        <h4 className={`text-sm font-medium transition-all ${task.status === 'done' ? 'line-through text-slate-500' : 'text-white'}`}>{task.title}</h4>
                        <div className="flex items-center gap-3 mt-1">
                            <span className="text-[10px] text-slate-500 flex items-center gap-1">
                                <span className="material-symbols-outlined text-[12px]">calendar_today</span> {task.due}
                            </span>
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-white/5 text-slate-400 border border-white/5">{task.tag}</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {task.priority === 'high' && task.status !== 'done' && (
                            <div className="flex items-center gap-1 text-[10px] font-bold text-amber-500 bg-amber-500/10 px-2 py-1 rounded-lg border border-amber-500/20">
                                <span className="material-symbols-outlined text-[12px]">warning</span>
                                HIGH
                            </div>
                        )}
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                            <button onClick={() => deleteTask(task.id)} className="size-8 rounded-lg hover:bg-white/10 flex items-center justify-center text-slate-500 hover:text-red-400 transition-colors">
                                <span className="material-symbols-outlined text-[18px]">delete</span>
                            </button>
                        </div>
                    </div>
                    </div>
                 ))
             )}
          </div>
       </div>
    </div>
  );
};

export default TasksWidget;
