/**
 * Chatbot API Service
 * 
 * This service handles all API calls related to the AI assistant chatbot.
 */
import axios from 'axios';

// API base URL
const API_BASE_URL = 'http://localhost:5004';

/**
 * Check if the backend server is running
 * @returns {Promise<boolean>} True if the backend is running
 */
export const checkBackendStatus = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/model-status`);
    return response.data.status === 'ready';
  } catch (error) {
    console.error('Error checking backend status:', error);
    return false;
  }
};

/**
 * Send a chat message to the backend and get a response
 * @param {Array} messages - Array of message objects with role and content
 * @returns {Promise<Object>} Response from the chatbot
 */
export const getChatCompletion = async (messages) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/chat`, { messages });
    return {
      message: response.data.response,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error getting chat completion:', error);
    if (error.response && error.response.status === 503) {
      throw new Error('The AI service is currently unavailable. Please try again later.');
    } else if (error.response && error.response.data && error.response.data.error) {
      throw new Error(error.response.data.error);
    } else {
      throw new Error('Failed to get a response from the AI assistant. Please try again.');
    }
  }
};
