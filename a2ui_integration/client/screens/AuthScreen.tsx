
import React, { useState } from 'react';

interface AuthScreenProps {
  onAuthSuccess: (email: string) => void;
}

const AuthScreen: React.FC<AuthScreenProps> = ({ onAuthSuccess }) => {
  const [email, setEmail] = useState('alex@workos.com');
  const [password, setPassword] = useState('password123');
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/20 rounded-full blur-[120px] opacity-40"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-purple-600/10 rounded-full blur-[120px] opacity-40"></div>

      <div className="glass-card w-full max-w-md rounded-2xl p-8 flex flex-col gap-6 animate-in fade-in zoom-in duration-500">
        <div className="text-center space-y-2">
          <div className="mx-auto w-16 h-16 rounded-xl bg-gradient-to-tr from-primary to-blue-400 flex items-center justify-center shadow-lg shadow-primary/20 mb-4">
            <span className="material-symbols-outlined text-white text-3xl">smart_toy</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            {isLogin ? 'Welcome back' : 'Create your workspace'}
          </h1>
          <p className="text-slate-400 text-sm">
            {isLogin ? 'Log in to your WorkOS workspace' : 'Your new conversational OS for work awaits.'}
          </p>
        </div>

        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 pl-1">Work Email</label>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-[20px] group-focus-within:text-primary transition-colors">mail</span>
              <input 
                className="glass-input w-full rounded-lg py-3 pl-10 pr-4 placeholder:text-slate-600 focus:outline-none focus:ring-0 sm:text-sm" 
                placeholder="name@company.com" 
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 pl-1">Password</label>
              {isLogin && <button className="text-xs text-primary font-medium hover:underline">Forgot?</button>}
            </div>
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-[20px] group-focus-within:text-primary transition-colors">lock</span>
              <input 
                className="glass-input w-full rounded-lg py-3 pl-10 pr-10 placeholder:text-slate-600 focus:outline-none focus:ring-0 sm:text-sm" 
                placeholder="••••••••" 
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                <span className="material-symbols-outlined text-[20px]">visibility_off</span>
              </button>
            </div>
          </div>

          {!isLogin && (
             <div className="flex items-start pt-2">
                <input id="terms" type="checkbox" className="w-4 h-4 mt-0.5 border-slate-600 rounded bg-transparent text-primary focus:ring-0" />
                <label htmlFor="terms" className="ml-2 text-xs text-slate-400">
                  I agree to the <span className="text-primary cursor-pointer">Terms</span> and <span className="text-primary cursor-pointer">Privacy</span>
                </label>
             </div>
          )}

          <button 
            onClick={() => onAuthSuccess(email)}
            className="w-full bg-primary hover:bg-blue-600 text-white font-semibold py-3.5 px-4 rounded-lg shadow-lg shadow-primary/30 transition-all active:scale-[0.98] mt-2 flex items-center justify-center gap-2"
          >
            {isLogin ? 'Log In' : 'Create Account'}
            <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
          </button>
        </div>

        <div className="relative py-2">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-700"></div></div>
          <div className="relative flex justify-center text-xs uppercase"><span className="bg-[#151b26] px-2 text-slate-500 rounded-sm">Or continue with</span></div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <button className="flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 rounded-lg text-white text-sm font-medium">
            <img className="w-4 h-4" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCzGcr5UXMuCK9q9jeOkNEfNsOON3N0ZyPLGyU8LzKEFdA54RASn9vHPINNGDd3mvwMR_LVCCksI_-NoqRCcR_MgBGU3et7NMgMY6w-zk9FH4RoyDM0Ycw18E0Gv2cck3rhcK9FzBZaFxS4qpwUYgC0y4P4TJdVsOqlnqseqdADzjvGWrETBuNDJk-HMzphmeE20_qcPB09fdoEJpaa_xDqkSkDi12tVPuV_F5rEe6F_UFW32u94mCAPmbFyumMFkprah-tSEbpMOtV" alt="G" />
            Google
          </button>
          <button className="flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 rounded-lg text-white text-sm font-medium">
             <span className="material-symbols-outlined text-[18px]">ios</span>
             Apple
          </button>
        </div>

        <p className="text-center text-sm text-slate-400 mt-2">
          {isLogin ? "Don't have an account?" : "Already a member?"}
          <button onClick={() => setIsLogin(!isLogin)} className="ml-1 font-semibold text-white hover:text-primary transition-colors">
            {isLogin ? "Sign Up" : "Sign In"}
          </button>
        </p>
      </div>
    </div>
  );
};

export default AuthScreen;
