
import React, { useState } from 'react';

interface AuthWidgetProps {
  onAuthSuccess: (email: string) => void;
}

const AuthWidget: React.FC<AuthWidgetProps> = ({ onAuthSuccess }) => {
  const [email, setEmail] = useState('alex@workos.com');
  const [password, setPassword] = useState('password123');
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="w-full mt-4 bg-[#0F111A] border border-white/10 rounded-2xl overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-300">
      <div className="bg-gradient-to-r from-primary/20 to-transparent p-4 border-b border-white/5 flex items-center gap-3">
        <div className="size-8 rounded-lg bg-primary/20 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-[18px]">lock</span>
        </div>
        <div>
            <h3 className="text-white text-sm font-bold">Secure Access</h3>
            <p className="text-[10px] text-slate-400 uppercase tracking-wider">Identity Verification</p>
        </div>
      </div>
      
      <div className="p-4 space-y-3">
        <div className="space-y-1">
          <label className="text-[9px] font-bold text-slate-500 uppercase tracking-widest ml-1">Email Node</label>
          <input 
            className="w-full bg-white/5 border border-white/10 rounded-lg py-2.5 px-3 text-sm text-white focus:outline-none focus:border-primary/50 transition-colors placeholder:text-slate-600"
            type="email" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="user@dhii.os"
          />
        </div>

        <div className="space-y-1">
          <label className="text-[9px] font-bold text-slate-500 uppercase tracking-widest ml-1">Passcode</label>
          <input 
            className="w-full bg-white/5 border border-white/10 rounded-lg py-2.5 px-3 text-sm text-white focus:outline-none focus:border-primary/50 transition-colors placeholder:text-slate-600"
            type="password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••"
          />
        </div>

        <button 
          onClick={() => onAuthSuccess(email)}
          className="w-full bg-primary hover:bg-blue-600 text-white text-xs font-bold py-3 rounded-lg shadow-lg shadow-primary/20 transition-all active:scale-[0.98] mt-2 flex items-center justify-center gap-2"
        >
          {isLogin ? 'Authenticate' : 'Create ID'}
          <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
        </button>

        <div className="pt-2 border-t border-white/5 flex justify-between items-center">
            <button onClick={() => setIsLogin(!isLogin)} className="text-[10px] text-slate-400 hover:text-white transition-colors">
                {isLogin ? 'Need an account?' : 'Have an ID?'}
            </button>
            <span className="text-[10px] text-emerald-500/80 font-mono flex items-center gap-1">
                <span className="size-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                Secure
            </span>
        </div>
      </div>
    </div>
  );
};

export default AuthWidget;
