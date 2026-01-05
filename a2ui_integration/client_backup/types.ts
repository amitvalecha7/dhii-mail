
export type AppScreen = 
  | 'AUTH' 
  | 'ONBOARDING' 
  | 'DASHBOARD' 
  | 'MAIL' 
  | 'TASKS' 
  | 'MEETINGS' 
  | 'MAIL_CONFIG' 
  | 'MAIL_REPLY';

export interface User {
  id: string;
  name: string;
  avatar: string;
  email: string;
}

export interface ChatMessage {
  role: 'user' | 'model';
  text: string;
  timestamp: Date;
}
