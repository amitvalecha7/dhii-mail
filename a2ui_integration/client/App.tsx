
import React, { useState } from 'react';
import { AppScreen, User } from './types';
import AuthScreen from './screens/AuthScreen';
import OnboardingScreen from './screens/OnboardingScreen';
import DashboardScreen from './screens/DashboardScreen';
import WorkspaceShell from './components/WorkspaceShell';
import MailContent from './components/MailContent';
import TasksContent from './components/TasksContent';
import MeetingsContent from './components/MeetingsContent';

const App: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>('AUTH');
  const [user, setUser] = useState<User | null>(null);

  const handleLogin = (email: string) => {
    setUser({
      id: 'D-8492',
      name: 'Alex Chen',
      email: email,
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1974&auto=format&fit=crop'
    });
    setCurrentScreen('ONBOARDING');
  };

  const renderContent = () => {
    switch (currentScreen) {
      case 'DASHBOARD':
        return <DashboardScreen user={user!} onNavigate={setCurrentScreen} />;
      case 'MAIL':
        return <MailContent user={user!} onNavigate={setCurrentScreen} />;
      case 'TASKS':
        return <TasksContent user={user!} onNavigate={setCurrentScreen} />;
      case 'MEETINGS':
        return <MeetingsContent user={user!} onNavigate={setCurrentScreen} />;
      default:
        return <DashboardScreen user={user!} onNavigate={setCurrentScreen} />;
    }
  };

  if (currentScreen === 'AUTH') return <AuthScreen onAuthSuccess={handleLogin} />;
  if (currentScreen === 'ONBOARDING') return <OnboardingScreen user={user!} onComplete={() => setCurrentScreen('DASHBOARD')} onBack={() => setCurrentScreen('AUTH')} />;

  // Workspace screens all live inside the shell
  return (
    <WorkspaceShell user={user!} currentScreen={currentScreen} onNavigate={setCurrentScreen}>
      {renderContent()}
    </WorkspaceShell>
  );
};

export default App;
