import axios from 'axios';

// Backend API URL
const API_URL = 'http://127.0.0.1:5004/api';

/**
 * Process a voice query to find matching jobs
 * @param {string} query - The transcribed voice query
 * @param {number} maxResults - Maximum number of results to return
 * @returns {Promise<Object>} Object containing matching jobs and query info
 */
export const processVoiceQuery = async (query, maxResults = 5) => {
  try {
    const response = await axios.post(`${API_URL}/process-voice-query`, {
      query,
      maxResults
    });
    return response.data;
  } catch (error) {
    console.error('Error processing voice query:', error);
    throw error;
  }
};

/**
 * Extract job requirements from a voice query
 * @param {string} query - The transcribed voice query
 * @returns {Promise<Object>} Object containing extracted job requirements
 */
export const extractJobRequirements = async (query) => {
  try {
    const response = await axios.post(`${API_URL}/extract-job-requirements`, {
      query
    });
    return response.data;
  } catch (error) {
    console.error('Error extracting job requirements:', error);
    throw error;
  }
};

/**
 * Check if the backend API is running
 * @returns {Promise<boolean>} True if the backend is running, false otherwise
 */
export const checkBackendStatus = async () => {
  try {
    await axios.get(`${API_URL}/model-status`);
    return true;
  } catch (error) {
    console.error('Backend connection error:', error);
    return false;
  }
};
