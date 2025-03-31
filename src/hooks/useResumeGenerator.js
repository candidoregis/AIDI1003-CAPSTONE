import { useState, useEffect } from 'react';
import { checkBackendStatus } from '../services/resume/resumeApiService';
import { 
  extractSkills, 
  matchResume, 
  generateResume 
} from '../services/resume/resumeApiService';

/**
 * Custom hook for resume generation functionality
 */
const useResumeGenerator = () => {
  const [jobDescription, setJobDescription] = useState('');
  const [resume, setResume] = useState('');
  const [extractedSkills, setExtractedSkills] = useState([]);
  const [generatedResume, setGeneratedResume] = useState(null);
  const [matchScore, setMatchScore] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [backendStatus, setBackendStatus] = useState('checking');

  // Check backend status on mount
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const isConnected = await checkBackendStatus();
        setBackendStatus(isConnected ? 'connected' : 'disconnected');
        if (!isConnected) {
          setError('Cannot connect to the backend server. Please make sure it is running.');
        }
      } catch (err) {
        console.error('Error checking backend status:', err);
        setBackendStatus('disconnected');
        setError('Cannot connect to the backend server. Please make sure it is running.');
      }
    };
    
    checkStatus();
  }, []);

  // Handle analyze and generate resume
  const handleAnalyze = async () => {
    if (backendStatus === 'disconnected') {
      setError('Cannot connect to the backend server. Please make sure it is running.');
      return;
    }

    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }

    if (!resume.trim()) {
      setError('Please enter your resume');
      return;
    }

    setError('');
    setLoading(true);

    try {
      // Step 1: Extract skills from job description
      const skillsData = await extractSkills(jobDescription);
      console.log("Extracted skills data from backend:", skillsData);
      
      // Use the skills array from the response
      const skillsArray = skillsData.skills || [];
      setExtractedSkills(skillsArray);
      
      if (skillsArray.length === 0) {
        throw new Error('No skills were extracted from the job description. Please try a more detailed job description.');
      }

      // Step 2: Match resume with extracted skills
      const matchResult = await matchResume(resume, skillsArray);
      console.log("Match result from backend:", matchResult);
      
      // Set match score from result
      setMatchScore(matchResult.match_score || 0);

      // Step 3: Generate personalized resume
      const resumeData = await generateResume(resume, jobDescription, skillsArray);
      console.log("Generated resume data from backend:", resumeData);
      
      // Check if the response has the expected structure
      if (resumeData && typeof resumeData === 'object') {
        if (resumeData.personalized_resume) {
          // Backend returned the expected structure with personalized_resume field
          setGeneratedResume(resumeData.personalized_resume);
          // If match_score is provided, use it
          if ('match_score' in resumeData) {
            setMatchScore(resumeData.match_score);
          }
        } else {
          // Unexpected structure, but still an object
          console.warn("Unexpected resume data structure:", resumeData);
          setGeneratedResume(JSON.stringify(resumeData, null, 2));
          setMatchScore(matchResult.match_score || 0);
        }
      } else {
        // Response is not an object, use as is
        console.warn("Non-object resume data:", resumeData);
        setGeneratedResume(String(resumeData));
        setMatchScore(matchResult.match_score || 0);
      }
      
    } catch (err) {
      console.error('Error during resume generation:', err);
      setError(`An error occurred: ${err.message || 'Please make sure the Python backend is running and models are trained.'}`);
    } finally {
      setLoading(false);
    }
  };

  // Reset all state
  const handleReset = () => {
    setJobDescription('');
    setResume('');
    setExtractedSkills([]);
    setGeneratedResume(null);
    setMatchScore(0);
    setError('');
  };

  return {
    jobDescription,
    setJobDescription,
    resume,
    setResume,
    extractedSkills,
    generatedResume,
    matchScore,
    loading,
    error,
    backendStatus,
    handleAnalyze,
    handleReset
  };
};

export default useResumeGenerator;
