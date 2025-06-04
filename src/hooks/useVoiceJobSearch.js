import { useState, useEffect } from 'react';
import { processVoiceQuery, checkBackendStatus } from '../services/voice/voiceJobSearchService';

/**
 * Custom hook for voice job search functionality
 * @returns {Object} Voice job search state and functions
 */
const useVoiceJobSearch = () => {
  const [voiceQuery, setVoiceQuery] = useState('');
  const [matchingJobs, setMatchingJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [backendStatus, setBackendStatus] = useState('checking');

  // Check backend status on mount
  useEffect(() => {
    const checkStatus = async () => {
      const isConnected = await checkBackendStatus();
      setBackendStatus(isConnected ? 'connected' : 'disconnected');
      if (!isConnected) {
        setError('Cannot connect to the backend server. Please make sure it is running.');
      }
    };
    
    checkStatus();
  }, []);

  /**
   * Process a voice query to find matching jobs
   * @param {string} query - The transcribed voice query
   */
  const handleVoiceQuery = async (query) => {
    if (backendStatus === 'disconnected') {
      setError('Cannot connect to the backend server. Please make sure it is running.');
      return;
    }

    if (!query.trim()) {
      setError('No voice query detected');
      return;
    }

    setVoiceQuery(query);
    setError('');
    setLoading(true);

    try {
      const result = await processVoiceQuery(query);
      console.log("Voice query result:", result);
      
      // Use matchingJobs from the result (the property name returned by the backend)
      const jobs = result.matchingJobs || [];
      setMatchingJobs(jobs);
      
      if (jobs.length === 0) {
        setError('No matching jobs found. Try a different search query.');
      }
    } catch (err) {
      console.error('Error processing voice query:', err);
      setError('An error occurred while processing your voice search. Please try again.');
      setMatchingJobs([]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reset the voice job search state
   */
  const resetSearch = () => {
    setVoiceQuery('');
    setMatchingJobs([]);
    setError('');
  };

  return {
    voiceQuery,
    matchingJobs,
    loading,
    error,
    backendStatus,
    handleVoiceQuery,
    resetSearch
  };
};

export default useVoiceJobSearch;
