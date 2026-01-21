
import React, { useState, useMemo } from 'react';

interface CalendarEvent {
  id: number;
  dateStr: string; // ISO date string YYYY-MM-DD
  time: string;
  title: string;
  duration: string;
  type: string;
  color: string;
}

const MeetingsWidget: React.FC = () => {
  const [view, setView] = useState<'day' | 'week' | 'month'>('day');
  const [currentDate, setCurrentDate] = useState<Date>(new Date());
  const [showAddModal, setShowAddModal] = useState(false);
  
  // New Event Form State
  const [newEventTitle, setNewEventTitle] = useState('');
  const [newEventTime, setNewEventTime] = useState('09:00');
  const [newEventDuration, setNewEventDuration] = useState('1h');

  // Helper to format date key
  const toDateKey = (d: Date) => d.toISOString().split('T')[0];

  const [events, setEvents] = useState<CalendarEvent[]>([
    { id: 1, dateStr: toDateKey(new Date()), time: '10:00 AM', title: 'Strategic Roadmap 2025', duration: '1.5h', type: 'huddle', color: 'bg-primary' },
    { id: 2, dateStr: toDateKey(new Date()), time: '12:30 PM', title: 'Lunch w/ Alex Koh', duration: '1h', type: 'external', color: 'bg-amber-500' },
    { id: 3, dateStr: toDateKey(new Date()), time: '02:00 PM', title: 'Design Review: UI v4', duration: '45m', type: 'internal', color: 'bg-emerald-500' },
    { id: 4, dateStr: toDateKey(new Date()), time: '04:00 PM', title: 'Weekly Sync', duration: '30m', type: 'recurring', color: 'bg-purple-500' },
  ]);

  const filteredEvents = useMemo(() => {
    // For simplicity in this mock, only 'day' view filters strictly. 
    // Real app would filter based on week range or month range.
    if (view === 'day') {
        return events.filter(e => e.dateStr === toDateKey(currentDate));
    }
    return events; // Show all for other views in this simple mock
  }, [events, currentDate, view]);

  const handleDateChange = (daysToAdd: number) => {
    const newDate = new Date(currentDate);
    newDate.setDate(newDate.getDate() + daysToAdd);
    setCurrentDate(newDate);
  };

  const handleAddEvent = () => {
    if (!newEventTitle) return;
    
    // Convert 24h input to AM/PM mock
    const [h, m] = newEventTime.split(':');
    const hour = parseInt(h);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    const timeStr = `${hour12}:${m} ${ampm}`;

    const newEvent: CalendarEvent = {
        id: Date.now(),
        dateStr: toDateKey(currentDate),
        time: timeStr,
        title: newEventTitle,
        duration: newEventDuration,
        type: 'custom',
        color: 'bg-blue-400'
    };
    
    setEvents(prev => [...prev, newEvent].sort((a,b) => a.time.localeCompare(b.time)));
    setShowAddModal(false);
    setNewEventTitle('');
  };

  // Mini Calendar Generation
  const generateMiniCalendar = () => {
    const start = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const end = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    const days = [];
    
    // Padding
    for(let i=0; i<start.getDay(); i++) days.push(null);
    // Days
    for(let i=1; i<=end.getDate(); i++) days.push(i);

    return days;
  };

  return (
    <div className="w-full h-[600px] bg-[#0c0e14] border border-white/5 rounded-3xl overflow-hidden shadow-2xl flex relative">
       
       {/* ADD EVENT MODAL OVERLAY */}
       {showAddModal && (
         <div className="absolute inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-sm bg-[#131620] border border-white/10 rounded-2xl p-6 shadow-2xl animate-in zoom-in-95">
                <h3 className="text-white font-bold text-lg mb-4">New Event</h3>
                <div className="space-y-4">
                    <div className="space-y-1">
                        <label className="text-xs text-slate-500 font-bold uppercase">Title</label>
                        <input 
                            className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-primary text-sm"
                            placeholder="Meeting name..."
                            value={newEventTitle}
                            onChange={(e) => setNewEventTitle(e.target.value)}
                            autoFocus
                        />
                    </div>
                    <div className="flex gap-3">
                        <div className="flex-1 space-y-1">
                            <label className="text-xs text-slate-500 font-bold uppercase">Time</label>
                            <input 
                                type="time"
                                className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-primary text-sm"
                                value={newEventTime}
                                onChange={(e) => setNewEventTime(e.target.value)}
                            />
                        </div>
                        <div className="flex-1 space-y-1">
                            <label className="text-xs text-slate-500 font-bold uppercase">Duration</label>
                            <select 
                                className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-primary text-sm"
                                value={newEventDuration}
                                onChange={(e) => setNewEventDuration(e.target.value)}
                            >
                                <option value="15m">15m</option>
                                <option value="30m">30m</option>
                                <option value="45m">45m</option>
                                <option value="1h">1h</option>
                                <option value="1.5h">1.5h</option>
                            </select>
                        </div>
                    </div>
                    <div className="flex gap-3 pt-2">
                        <button 
                            onClick={() => setShowAddModal(false)}
                            className="flex-1 py-3 rounded-xl border border-white/10 text-slate-400 hover:text-white hover:bg-white/5 text-sm font-bold transition-colors"
                        >
                            Cancel
                        </button>
                        <button 
                            onClick={handleAddEvent}
                            disabled={!newEventTitle}
                            className="flex-1 py-3 rounded-xl bg-primary hover:bg-blue-600 disabled:opacity-50 text-white text-sm font-bold transition-colors shadow-lg"
                        >
                            Create
                        </button>
                    </div>
                </div>
            </div>
         </div>
       )}

       {/* LEFT PANEL: MINI CALENDAR & FILTERS */}
       <div className="w-64 bg-[#0f111a] border-r border-white/5 flex flex-col p-6 shrink-0">
          <button 
            onClick={() => setShowAddModal(true)}
            className="w-full bg-white text-black hover:bg-slate-200 transition-colors rounded-xl py-3 font-bold text-sm flex items-center justify-center gap-2 mb-8 shadow-lg shadow-white/5"
          >
             <span className="material-symbols-outlined text-[18px]">add</span>
             New Event
          </button>

          {/* Mini Calendar */}
          <div className="mb-8 select-none">
             <div className="flex justify-between items-center mb-4">
                <span className="text-sm font-bold text-white">
                    {currentDate.toLocaleString('default', { month: 'long', year: 'numeric' })}
                </span>
                <div className="flex gap-2">
                   <button onClick={() => handleDateChange(-30)} className="text-slate-500 hover:text-white"><span className="material-symbols-outlined text-[16px]">chevron_left</span></button>
                   <button onClick={() => handleDateChange(30)} className="text-slate-500 hover:text-white"><span className="material-symbols-outlined text-[16px]">chevron_right</span></button>
                </div>
             </div>
             <div className="grid grid-cols-7 gap-2 text-center text-[10px] text-slate-500 mb-2 font-bold">
                <span>S</span><span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span>
             </div>
             <div className="grid grid-cols-7 gap-y-2 gap-x-1 text-center text-xs text-slate-300">
                {generateMiniCalendar().map((day, i) => (
                    day === null ? <span key={i}></span> : (
                        <button 
                            key={i}
                            onClick={() => {
                                const newDate = new Date(currentDate);
                                newDate.setDate(day);
                                setCurrentDate(newDate);
                            }}
                            className={`size-7 rounded-full flex items-center justify-center mx-auto transition-colors ${
                                day === currentDate.getDate() 
                                ? 'bg-primary text-white shadow-lg shadow-primary/30' 
                                : 'hover:bg-white/10 text-slate-400'
                            }`}
                        >
                            {day}
                        </button>
                    )
                ))}
             </div>
          </div>

          <div className="space-y-3">
             <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">My Calendars</p>
             <div className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white">
                <div className="size-3 rounded border border-primary bg-primary/20"></div> Work
             </div>
             <div className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white">
                <div className="size-3 rounded border border-purple-500 bg-purple-500/20"></div> Personal
             </div>
             <div className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer hover:text-white">
                <div className="size-3 rounded border border-amber-500 bg-amber-500/20"></div> Travel
             </div>
          </div>
       </div>

       {/* MAIN CALENDAR VIEW */}
       <div className="flex-1 flex flex-col bg-[#0c0e14]">
          {/* Header */}
          <div className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-[#0c0e14]/50 backdrop-blur-sm sticky top-0 z-10">
             <div className="flex items-center gap-4">
                <h3 className="text-white font-bold text-lg">
                    {currentDate.toLocaleString('default', { weekday: 'long' })}, {currentDate.toLocaleString('default', { month: 'short', day: 'numeric' })}
                </h3>
                <div className="flex gap-1">
                   <button onClick={() => handleDateChange(-1)} className="p-1 hover:bg-white/10 rounded-lg text-slate-400"><span className="material-symbols-outlined text-[18px]">chevron_left</span></button>
                   <button onClick={() => handleDateChange(1)} className="p-1 hover:bg-white/10 rounded-lg text-slate-400"><span className="material-symbols-outlined text-[18px]">chevron_right</span></button>
                </div>
             </div>
             <div className="flex p-1 bg-white/5 rounded-lg">
                <button onClick={() => setView('day')} className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${view === 'day' ? 'bg-white/10 text-white' : 'text-slate-500'}`}>Day</button>
                <button onClick={() => setView('week')} className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${view === 'week' ? 'bg-white/10 text-white' : 'text-slate-500'}`}>Week</button>
                <button onClick={() => setView('month')} className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${view === 'month' ? 'bg-white/10 text-white' : 'text-slate-500'}`}>Month</button>
             </div>
          </div>

          {/* Timeline View */}
          <div className="flex-1 overflow-y-auto p-6 relative">
             <div className="absolute left-6 top-0 bottom-0 w-px bg-white/5 z-0"></div>
             
             {/* Current Time Indicator (Static for demo) */}
             <div className="absolute left-0 right-0 top-[180px] flex items-center z-10 pointer-events-none opacity-50">
                <div className="w-16 text-right text-[10px] font-bold text-primary pr-4">11:15 AM</div>
                <div className="flex-1 h-px bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"></div>
             </div>

             <div className="space-y-6 relative z-10">
                {filteredEvents.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 opacity-40">
                         <span className="material-symbols-outlined text-4xl mb-2 text-slate-500">event_busy</span>
                         <p className="text-sm font-bold text-slate-400">No events scheduled</p>
                    </div>
                ) : (
                    filteredEvents.map((event) => (
                    <div key={event.id} className="flex gap-4 group animate-in slide-in-from-left-4 duration-500">
                        <div className="w-12 text-right text-xs text-slate-500 font-medium pt-1 whitespace-nowrap">{event.time}</div>
                        <div className="flex-1">
                            <div className={`p-4 rounded-xl border border-white/5 bg-white/[0.03] hover:bg-white/[0.06] transition-all cursor-pointer relative overflow-hidden group-hover:border-white/10`}>
                                <div className={`absolute left-0 top-0 bottom-0 w-1 ${event.color}`}></div>
                                <div className="flex justify-between items-start">
                                <div>
                                    <h4 className="text-sm font-bold text-white mb-1">{event.title}</h4>
                                    <p className="text-xs text-slate-500 flex items-center gap-1">
                                        <span className="material-symbols-outlined text-[12px]">schedule</span>
                                        {event.duration}
                                    </p>
                                </div>
                                <button className="opacity-0 group-hover:opacity-100 transition-opacity size-8 rounded-lg bg-white/10 flex items-center justify-center text-white hover:bg-white/20">
                                    <span className="material-symbols-outlined text-[16px]">more_horiz</span>
                                </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    ))
                )}
             </div>
          </div>
       </div>
    </div>
  );
};

export default MeetingsWidget;
