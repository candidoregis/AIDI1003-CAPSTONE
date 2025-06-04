/**
 * Voice API Service
 * 
 * This service handles all API calls related to voice query processing.
 */
import axios from 'axios';

// API base URL
const API_BASE_URL = 'http://localhost:5003';

/**
 * Check if the backend server is running and models are loaded
 * @returns {Promise<boolean>} True if the backend is running and models are loaded
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
 * Process a voice query to extract job requirements and find matching jobs
 * @param {string} query - The voice query text
 * @returns {Promise<Object>} Object containing requirements and matching jobs
 */
export const processVoiceQuery = async (query) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/process-voice-query`, { query });
    return response.data;
  } catch (error) {
    console.error('Error processing voice query:', error);
    throw new Error(error.response?.data?.error || 'Failed to process voice query');
  }
};

/**
 * Extract job requirements from a voice query
 * @param {string} query - The voice query text
 * @returns {Promise<Object>} Object containing extracted job requirements
 */
export const extractJobRequirements = async (query) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/extract-job-requirements`, { query });
    return response.data;
  } catch (error) {
    console.error('Error extracting job requirements:', error);
    throw new Error(error.response?.data?.error || 'Failed to extract job requirements');
  }
};
