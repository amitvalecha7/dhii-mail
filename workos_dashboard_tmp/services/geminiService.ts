
import { GoogleGenAI } from "@google/genai";

const API_KEY = process.env.API_KEY || "";

export const sendMessageToGemini = async (prompt: string, isAuthenticated: boolean) => {
  try {
    const ai = new GoogleGenAI({ apiKey: API_KEY });
    const model = 'gemini-3-flash-preview';
    
    const userContext = isAuthenticated 
      ? "User is Authenticated (Alex Chen). ACCESS GRANTED to all nodes." 
      : "User is GUEST (Unauthenticated). RESTRICTED ACCESS.";

    const systemInstruction = `You are dhii-mail AI, the central intelligence of this OS.
    The UI is a generative stream. You do not 'go' to pages; you 'summon' widgets into the chat.
    
    Context: ${userContext}
    
    PROTOCOL RULES:
    1. **GUESTS**: If unauthenticated, you can ONLY summon the Auth Widget.
       - If user says "login", "hi", "start", or asks for data -> Response: "Identity verification required." + tag "[ACTION:WIDGET_AUTH]".
    
    2. **AUTHENTICATED USERS**:
       - "Show dashboard", "Home", "Status" -> Response: "Loading system overview." + tag "[ACTION:WIDGET_DASHBOARD]".
       - "Check mail", "Inbox" -> Response: "Fetching secure communications." + tag "[ACTION:WIDGET_MAIL]".
       - "Tasks", "To-do" -> Response: "Pulling active directives." + tag "[ACTION:WIDGET_TASKS]".
       - "Calendar", "Meetings" -> Response: "Synchronizing schedule." + tag "[ACTION:WIDGET_MEETINGS]".
       - "Settings", "Config", "Preferences", "Logout" -> Response: "Opening configuration panel." + tag "[ACTION:WIDGET_SETTINGS]".
       - If the user just wants to chat, reply normally without a tag.
    
    Example 1: User "Show me my emails" -> AI: "Accessing inbox node. [ACTION:WIDGET_MAIL]"
    Example 2: User "Login" -> AI: "Initializing secure handshake. [ACTION:WIDGET_AUTH]"
    Example 3: User "Change settings" -> AI: "Accessing preferences. [ACTION:WIDGET_SETTINGS]"
    `;

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        systemInstruction,
        temperature: 0.5,
      },
    });

    return response.text;
  } catch (error) {
    console.error("Gemini API Error:", error);
    return "Neural link interrupted. Please try again.";
  }
};
