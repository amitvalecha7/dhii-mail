
import React, { useState } from 'react';
import { User } from './types';
import WorkspaceShell from './components/WorkspaceShell';

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);

  const handleLogin = (email: string) => {
    setUser({
      id: 'D-8492',
      name: 'Alex Chen',
      email: email,
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1974&auto=format&fit=crop'
    });
  };

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <WorkspaceShell 
      user={user} 
      onAuthSuccess={() => handleLogin('alex@workos.com')}
      onLogout={handleLogout}
    />
  );
};

export default App;
