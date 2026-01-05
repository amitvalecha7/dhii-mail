
import { GoogleGenAI } from "@google/genai";

const API_KEY = process.env.API_KEY || "";

export const sendMessageToGemini = async (prompt: string, context?: string) => {
  try {
    const ai = new GoogleGenAI({ apiKey: API_KEY });
    const model = 'gemini-3-flash-preview';
    
    const systemInstruction = context 
      ? `You are dhii-mail AI. Context: ${context}. You are a sophisticated agentic assistant. Help users manage their inbox, schedule, and tasks with high precision.`
      : "You are dhii-mail AI, a futuristic conversational operating system for work. You have deep control over the user's mail, calendar, and tasks. Respond elegantly and professionally.";

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        systemInstruction,
        temperature: 0.8,
      },
    });

    return response.text;
  } catch (error) {
    console.error("Gemini API Error:", error);
    return "The neural link is experiencing interference. Please retry your request, Commander.";
  }
};
