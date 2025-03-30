import axios from 'axios';

// Backend API URL
const API_URL = 'http://127.0.0.1:5001/api';

/**
 * Check if the backend API is running
 * @returns {Promise<boolean>} True if the backend is running, false otherwise
 */
export const checkBackendStatus = async () => {
  try {
    await axios.get(`${API_URL}/model-status`);
    return true;
  } catch (err) {
    console.error('Backend connection error:', err);
    return false;
  }
};

/**
 * Extract skills from a job description
 * @param {string} jobDescription - The job description to extract skills from
 * @returns {Promise<Array>} Array of extracted skills
 */
export const extractSkills = async (jobDescription) => {
  try {
    const response = await axios.post(`${API_URL}/extract-skills`, {
      jobDescription
    });
    
    // Process skills data to ensure it's in a consistent format
    const skills = response.data;
    return Array.isArray(skills) 
      ? skills.map(skill => {
          if (typeof skill === 'string') return { name: skill };
          if (typeof skill === 'object') {
            // Handle the case where skill is an object with category, relevance, skill properties
            if (skill.skill) return { name: skill.skill, ...skill };
            if (skill.name) return skill;
            // Convert complex objects to a simpler format
            return { name: JSON.stringify(skill) };
          }
          return { name: String(skill) };
        })
      : [];
  } catch (error) {
    console.error('Error extracting skills:', error);
    throw error;
  }
};

/**
 * Calculate match score between resume and job skills
 * @param {string} resume - The resume text
 * @param {Array} jobSkills - Array of job skills
 * @returns {Promise<number>} Match score as a percentage
 */
export const calculateMatchScore = async (resume, jobSkills) => {
  try {
    const response = await axios.post(`${API_URL}/match-resume`, {
      resume,
      jobSkills
    });
    return response.data.matchScore;
  } catch (error) {
    console.error('Error calculating match score:', error);
    throw error;
  }
};

/**
 * Generate a personalized resume based on job description and skills
 * @param {string} resume - The original resume text
 * @param {string} jobDescription - The job description
 * @param {Array} extractedSkills - Array of extracted skills
 * @returns {Promise<Object>} Generated resume data
 */
export const generatePersonalizedResume = async (resume, jobDescription, extractedSkills) => {
  try {
    const response = await axios.post(`${API_URL}/generate-resume`, {
      resume,
      jobDescription,
      extractedSkills
    });
    return response.data;
  } catch (error) {
    console.error('Error generating personalized resume:', error);
    throw error;
  }
};
