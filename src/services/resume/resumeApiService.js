import axios from 'axios';

// Backend API URL
const API_URL = 'http://127.0.0.1:5004/api';

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
    const data = response.data;
    
    // Return the skills array directly
    return {
      skills: data.skills || [],
      experience: data.experience || 0,
      education: data.education || []
    };
  } catch (err) {
    console.error('Error extracting skills:', err);
    throw new Error('Failed to extract skills from job description');
  }
};

/**
 * Match a resume with job skills
 * @param {string} resume - The resume text
 * @param {Array} jobSkills - Array of job skills
 * @returns {Promise<Object>} Match results
 */
export const matchResume = async (resume, jobSkills) => {
  try {
    console.log('Matching resume with skills:', { resume: resume.substring(0, 100) + '...', jobSkills });
    
    const response = await axios.post(`${API_URL}/match-resume`, {
      resume,
      jobSkills
    });
    
    return response.data;
  } catch (err) {
    console.error('Error matching resume:', err);
    throw new Error('Failed to match resume with job skills');
  }
};

/**
 * Generate a personalized resume
 * @param {string} resume - The original resume text
 * @param {string} jobDescription - The job description
 * @param {Array} extractedSkills - Array of extracted skills
 * @returns {Promise<Object>} Generated resume data
 */
export const generateResume = async (resume, jobDescription, extractedSkills) => {
  try {
    console.log('Generating resume:', { 
      resume: resume.substring(0, 100) + '...', 
      jobDescription: jobDescription.substring(0, 100) + '...',
      extractedSkills
    });
    
    const response = await axios.post(`${API_URL}/generate-resume`, {
      resume,
      jobDescription,
      extractedSkills
    });
    
    return response.data;
  } catch (err) {
    console.error('Error generating resume:', err);
    throw new Error('Failed to generate personalized resume');
  }
};
