/**
 * Enterprise-Scale Protocol App
 * Complete frontend implementation of the enterprise mental model
 * [ Python Backend ] → (JSON protocol) → [ UI Runtime (React / TS) ]
 */

import React, { useState } from 'react';
import { AppScreen, User } from './types';
import AuthScreen from './screens/AuthScreen';
import OnboardingScreen from './screens/OnboardingScreen';
import ProtocolDashboardScreen from './screens/ProtocolDashboardScreen';
import ProtocolWorkspaceShell from './components/ProtocolWorkspaceShell';
import { ProtocolKernelBridge } from './services/protocolKernelBridge';

// Tenant context for enterprise deployment
interface TenantContext {
  id: string;
  name: string;
  config: Record<string, any>;
}

const App: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>('AUTH');
  const [user, setUser] = useState<User | null>(null);
  const [tenantContext, setTenantContext] = useState<TenantContext>({
    id: 'default',
    name: 'Default Tenant',
    config: {}
  });

  // Initialize protocol kernel bridge with tenant context
  const protocolBridge = new ProtocolKernelBridge({
    tenantId: tenantContext.id,
    onError: (error) => {
      console.error('Protocol Error:', error);
      // Could implement global error boundary here
    }
  });

  const handleLogin = async (email: string) => {
    try {
      // Authenticate via protocol
      const authResponse = await protocolBridge.fetchOrchestratorOutput('auth', {
        email,
        action: 'login'
      });

      // Extract user data from protocol response
      const userData = authResponse.chunks.find(chunk => chunk.type === 'AuthResult');
      if (userData && 'user' in userData) {
        setUser(userData.user as User);
        setCurrentScreen('ONBOARDING');
      } else {
        throw new Error('Invalid authentication response');
      }
    } catch (error) {
      console.error('Authentication failed:', error);
      // Handle authentication error
    }
  };

  const handleTenantSelection = (tenantId: string) => {
    // In enterprise deployment, tenant would be selected from URL, subdomain, or auth context
    setTenantContext({
      id: tenantId,
      name: `Tenant ${tenantId}`,
      config: {}
    });
  };

  const renderContent = () => {
    // All content screens use protocol-compliant rendering
    switch (currentScreen) {
      case 'DASHBOARD':
        return (
          <ProtocolDashboardScreen 
            user={user!} 
            onNavigate={setCurrentScreen} 
            tenantId={tenantContext.id}
          />
        );
      
      // Other screens would also use protocol-compliant versions
      case 'MAIL':
        // return <ProtocolMailScreen user={user!} onNavigate={setCurrentScreen} tenantId={tenantContext.id} />;
        return <div className="flex-1 flex items-center justify-center text-slate-600">Mail screen - Protocol implementation pending</div>;
      
      case 'TASKS':
        // return <ProtocolTasksScreen user={user!} onNavigate={setCurrentScreen} tenantId={tenantContext.id} />;
        return <div className="flex-1 flex items-center justify-center text-slate-600">Tasks screen - Protocol implementation pending</div>;
      
      case 'MEETINGS':
        // return <ProtocolMeetingsScreen user={user!} onNavigate={setCurrentScreen} tenantId={tenantContext.id} />;
        return <div className="flex-1 flex items-center justify-center text-slate-600">Meetings screen - Protocol implementation pending</div>;
      
      default:
        return (
          <ProtocolDashboardScreen 
            user={user!} 
            onNavigate={setCurrentScreen} 
            tenantId={tenantContext.id}
          />
        );
    }
  };

  // Authentication flow
  if (currentScreen === 'AUTH') {
    return <AuthScreen onAuthSuccess={handleLogin} />;
  }

  // Onboarding flow
  if (currentScreen === 'ONBOARDING') {
    return (
      <OnboardingScreen 
        user={user!} 
        onComplete={() => setCurrentScreen('DASHBOARD')} 
        onBack={() => setCurrentScreen('AUTH')} 
      />
    );
  }

  // Main application with protocol-compliant workspace shell
  return (
    <ProtocolWorkspaceShell 
      user={user!} 
      currentScreen={currentScreen} 
      onNavigate={setCurrentScreen}
      tenantId={tenantContext.id}
    >
      {renderContent()}
    </ProtocolWorkspaceShell>
  );
};

export default App;