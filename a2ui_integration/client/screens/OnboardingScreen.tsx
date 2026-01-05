
import React from 'react';
import { User } from '../types';

interface OnboardingScreenProps {
  user: User;
  onComplete: () => void;
  onBack: () => void;
}

const OnboardingScreen: React.FC<OnboardingScreenProps> = ({ user, onComplete, onBack }) => {
  return (
    <div className="relative min-h-screen w-full flex flex-col items-center justify-center p-6 overflow-hidden">
      {/* Mesh Decor */}
      <div className="absolute inset-0 bg-[radial-gradient(at_0%_0%,_hsla(220,68%,20%,0.3)_0px,_transparent_50%),_radial-gradient(at_100%_100%,_hsla(211,78%,15%,0.3)_0px,_transparent_50%)] pointer-events-none opacity-60"></div>
      
      <main className="relative z-10 w-full max-w-[360px] animate-in fade-in zoom-in duration-500">
        <div className="glass-card w-full rounded-[2rem] p-8 flex flex-col items-center gap-8 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent opacity-50 pointer-events-none"></div>
          
          <div className="relative mt-4">
            <div className="absolute -inset-1 rounded-full bg-gradient-to-tr from-primary to-transparent opacity-70 blur-md"></div>
            <div className="relative h-32 w-32 rounded-full p-[2px] bg-gradient-to-tr from-primary/50 to-white/10">
              <div 
                className="h-full w-full rounded-full bg-center bg-cover border border-white/10 shadow-inner overflow-hidden"
                style={{ backgroundImage: `url(${user.avatar})` }}
              >
                <div className="absolute inset-0 bg-indigo-900/20 mix-blend-overlay"></div>
              </div>
            </div>
            <div className="absolute bottom-1 right-1 bg-background-dark border border-white/10 rounded-full p-1.5 flex items-center justify-center shadow-lg">
              <span className="material-symbols-outlined text-primary text-[18px]">verified_user</span>
            </div>
          </div>

          <div className="flex flex-col items-center gap-2 text-center w-full z-10">
            <p className="text-indigo-200/60 text-sm font-medium tracking-widest uppercase">Identity Confirmed</p>
            <h1 className="text-white text-3xl font-bold tracking-tight glow-text font-mono mt-1">
              USER-{user.id}
            </h1>
            <div className="flex flex-col items-center gap-1 mt-2">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span className="text-indigo-100/80 text-xs font-medium">System Online</span>
              </div>
              <p className="text-indigo-200/50 text-xs mt-2">
                Access Level: <span className="text-white">Administrator</span>
              </p>
            </div>
          </div>

          <div className="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent my-2"></div>

          <div className="w-full flex flex-col items-center gap-4 mb-2 z-10">
            <p className="text-indigo-200/70 text-sm text-center">
              Welcome to the OS. Your workspace has been initialized.
            </p>
            <button 
              onClick={onComplete}
              className="group relative w-full overflow-hidden rounded-xl h-12 bg-primary hover:bg-primary/90 transition-all shadow-[0_0_20px_rgba(25,93,230,0.3)] active:scale-[0.98]"
            >
              <div className="flex items-center justify-center gap-2 h-full w-full">
                <span className="text-white text-base font-semibold tracking-wide">Initialize System</span>
                <span className="material-symbols-outlined text-white text-[20px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </div>
            </button>
            <button onClick={onBack} className="text-indigo-200/40 text-xs hover:text-white transition-colors py-2">
              Switch Account
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default OnboardingScreen;
