
export type AppScreen = 'STREAM'; // The app is now just a stream

export interface User {
  id: string;
  name: string;
  avatar: string;
  email: string;
}

export type WidgetType = 
  | 'AUTH' 
  | 'DASHBOARD' 
  | 'MAIL' 
  | 'TASKS' 
  | 'MEETINGS' 
  | 'SETTINGS' 
  | 'NONE';

export interface ChatMessage {
  id: string; // Added ID for keying
  role: 'user' | 'model';
  text: string;
  timestamp: Date;
  widget?: WidgetType;
}
