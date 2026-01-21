
import React, { useState } from 'react';

interface AuthScreenProps {
  onAuthSuccess: (email: string) => void;
}

const AuthScreen: React.FC<AuthScreenProps> = ({ onAuthSuccess }) => {
  const [email, setEmail] = useState('alex@workos.com');
  const [password, setPassword] = useState('password123');
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="h-full w-full flex flex-col items-center justify-center p-6 relative overflow-y-auto no-scrollbar">
      {/* Subtle Internal Decor */}
      <div className="absolute top-10 left-10 w-64 h-64 bg-primary/10 rounded-full blur-[80px] opacity-60 pointer-events-none"></div>
      
      <div className="glass-card w-full max-w-md rounded-[2rem] p-8 flex flex-col gap-6 animate-in fade-in zoom-in duration-500 z-10 border border-white/10 shadow-2xl">
        <div className="text-center space-y-2">
          <div className="mx-auto size-16 rounded-2xl bg-gradient-to-tr from-primary to-blue-500 flex items-center justify-center shadow-lg shadow-primary/20 mb-4">
            <span className="material-symbols-outlined text-white text-3xl">blur_on</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tighter text-white font-display">
            {isLogin ? 'Welcome Back' : 'Join dhii-mail'}
          </h1>
          <p className="text-slate-400 text-sm font-medium">
            {isLogin ? 'Authenticate to access your workspace.' : 'Initialize your agentic OS.'}
          </p>
        </div>

        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 pl-1">Neural ID / Email</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 text-[20px] group-focus-within:text-primary transition-colors">alternate_email</span>
              <input 
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3.5 pl-11 pr-4 placeholder:text-slate-600 focus:outline-none focus:border-primary/50 text-white transition-all text-sm font-medium" 
                placeholder="name@company.com" 
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 pl-1">Passcode</label>
              {isLogin && <button className="text-[10px] font-bold text-primary hover:text-white transition-colors">RESET?</button>}
            </div>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 text-[20px] group-focus-within:text-primary transition-colors">lock</span>
              <input 
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3.5 pl-11 pr-10 placeholder:text-slate-600 focus:outline-none focus:border-primary/50 text-white transition-all text-sm font-medium" 
                placeholder="••••••••" 
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <button 
            onClick={() => onAuthSuccess(email)}
            className="w-full bg-primary hover:bg-blue-600 text-white font-bold py-4 rounded-xl shadow-lg shadow-primary/30 transition-all active:scale-[0.98] mt-2 flex items-center justify-center gap-2 uppercase tracking-widest text-xs"
          >
            {isLogin ? 'Initialize Session' : 'Create Node'}
            <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
        </div>

        <div className="relative py-2">
           <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-white/5"></div></div>
           <div className="relative flex justify-center"><span className="bg-[#0b0e14] px-3 text-[10px] font-bold text-slate-600 uppercase tracking-widest">Or Authenticate With</span></div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <button className="flex items-center justify-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/5 rounded-xl text-white text-xs font-bold transition-all">
            <img className="w-4 h-4" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCzGcr5UXMuCK9q9jeOkNEfNsOON3N0ZyPLGyU8LzKEFdA54RASn9vHPINNGDd3mvwMR_LVCCksI_-NoqRCcR_MgBGU3et7NMgMY6w-zk9FH4RoyDM0Ycw18E0Gv2cck3rhcK9FzBZaFxS4qpwUYgC0y4P4TJdVsOqlnqseqdADzjvGWrETBuNDJk-HMzphmeE20_qcPB09fdoEJpaa_xDqkSkDi12tVPuV_F5rEe6F_UFW32u94mCAPmbFyumMFkprah-tSEbpMOtV" alt="G" />
            Google
          </button>
          <button className="flex items-center justify-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/5 rounded-xl text-white text-xs font-bold transition-all">
             <span className="material-symbols-outlined text-[18px]">fingerprint</span>
             Biometrics
          </button>
        </div>

        <p className="text-center text-xs text-slate-400 mt-2 font-medium">
          {isLogin ? "New to the system?" : "Already verified?"}
          <button onClick={() => setIsLogin(!isLogin)} className="ml-1 font-bold text-white hover:text-primary transition-colors">
            {isLogin ? "Deploy Node" : "Access"}
          </button>
        </p>
      </div>
    </div>
  );
};

export default AuthScreen;
