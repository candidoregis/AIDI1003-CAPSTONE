import { GoogleGenerativeAI } from '@google/generative-ai';

// Initialize Gemini API with a demo key (you can get your own free key later)
const genAI = new GoogleGenerativeAI('AIzaSyDhDGQ3tFpN1nXBQxuRDVTMJsVWFYBzYPc');
const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

// Helper function to handle API errors
const handleApiError = (error) => {
  console.error('Gemini API Error:', error);
  if (error.message) {
    throw new Error(`Error: ${error.message}`);
  } else {
    throw new Error('An unexpected error occurred. Please try again.');
  }
};

// Chat Completion with Memory
export const getChatCompletion = async (messages, context = {}) => {
  try {
    if (!messages?.length) {
      throw new Error('Please provide messages for the chat');
    }

    // Format the conversation history for the model
    const formattedMessages = messages.map(m => `${m.role}: ${m.content}`).join('\n');
    
    // Include any context information
    const contextStr = Object.keys(context).length 
      ? `\nContext: ${JSON.stringify(context, null, 2)}` 
      : '';

    const prompt = `You are an AI recruitment assistant helping with HR tasks.
      Respond to the following conversation, maintaining a professional, helpful tone.
      
      Conversation history:
      ${formattedMessages}
      ${contextStr}
      
      Your response:`;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    
    return {
      message: text,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    handleApiError(error);
  }
};
