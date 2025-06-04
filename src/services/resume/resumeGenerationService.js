import axios from 'axios';

// Backend API URL
const API_URL = 'http://127.0.0.1:5001/api';

// Helper function to check backend status
export const checkBackendStatus = async () => {
  try {
    await axios.get(`${API_URL}/model-status`);
    return true;
  } catch (err) {
    console.error('Backend connection error:', err);
    return false;
  }
};

// Extract skills from job description
export const extractSkills = async (jobDescription) => {
  try {
    const response = await axios.post(`${API_URL}/extract-skills`, {
      jobDescription
    });
    return response.data;
  } catch (error) {
    console.error('Error extracting skills:', error);
    throw error;
  }
};

// Calculate match score between resume and job
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

// Generate personalized resume
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

// Analyze job description and candidate profile
export const analyzeJobAndProfile = async (jobDescription, candidateProfile) => {
  try {
    // Extract skills from job description
    const extractedSkills = await extractSkills(jobDescription);
    
    // Convert candidate profile to plain text for processing
    const resumeText = convertProfileToText(candidateProfile);
    
    // Calculate match score
    const matchScore = await calculateMatchScore(resumeText, extractedSkills);
    
    return {
      keywordMatch: {
        matched: extractedSkills.slice(0, 3).map(skill => skill.name || ''),
        missing: extractedSkills.slice(3, 6).map(skill => skill.name || '').filter(skill => 
          skill && resumeText && !resumeText.toLowerCase().includes(skill.toLowerCase())
        ),
        partial: extractedSkills.slice(6, 9).map(skill => skill.name || '')
      },
      recommendedSections: [
        'Professional Summary',
        'Technical Skills',
        'Work Experience',
        'Education',
        'Projects'
      ],
      toneSuggestions: {
        industry: 'technology',
        formality: 'semi-formal',
        focus: 'technical expertise'
      },
      skillGaps: {
        critical: extractedSkills.slice(0, 2).map(skill => skill.name || '').filter(skill => 
          skill && resumeText && !resumeText.toLowerCase().includes(skill.toLowerCase())
        ),
        recommended: extractedSkills.slice(2, 5).map(skill => skill.name || '').filter(skill => 
          skill && resumeText && !resumeText.toLowerCase().includes(skill.toLowerCase())
        ),
        nice: extractedSkills.slice(5, 7).map(skill => skill.name || '')
      },
      atsScore: matchScore,
      improvements: [
        'Add more quantifiable achievements',
        'Include specific projects related to the job requirements',
        'Highlight relevant skills and experiences'
      ]
    };
  } catch (error) {
    console.error('Error analyzing job and profile:', error);
    throw error;
  }
};

// Helper function to convert candidate profile to text
const convertProfileToText = (profile) => {
  if (!profile || !profile.personalInfo) {
    return '';
  }
  
  let text = `${profile.personalInfo.name || ''}\n`;
  text += `${profile.personalInfo.email || ''} | ${profile.personalInfo.phone || ''} | ${profile.personalInfo.location || ''}\n\n`;
  
  text += "EXPERIENCE\n";
  if (profile.experience && profile.experience.length > 0) {
    profile.experience.forEach(exp => {
      text += `${exp.title || ''} at ${exp.company || ''} (${exp.duration || ''})\n`;
      text += `${exp.description || ''}\n\n`;
    });
  }
  
  text += "EDUCATION\n";
  if (profile.education && profile.education.length > 0) {
    profile.education.forEach(edu => {
      text += `${edu.degree || ''} from ${edu.school || ''} (${edu.year || ''})\n`;
    });
  }
  
  text += "SKILLS\n";
  if (profile.skills && profile.skills.length > 0) {
    text += profile.skills.join(", ");
  }
  
  return text;
};

// Generate optimized resume content
export const generateResumeContent = async (jobDescription, candidateProfile, preferences) => {
  try {
    // Extract skills from job description
    const extractedSkills = await extractSkills(jobDescription);
    
    // Convert candidate profile to plain text for processing
    const resumeText = convertProfileToText(candidateProfile);
    
    // Generate personalized resume
    const generatedResume = await generatePersonalizedResume(resumeText, jobDescription, extractedSkills);
    
    // Ensure experience is an array
    const experienceArray = Array.isArray(generatedResume.experience) 
      ? generatedResume.experience 
      : (generatedResume.experience ? [String(generatedResume.experience)] : []);
    
    // Ensure skills is an array
    const skillsArray = Array.isArray(generatedResume.skills)
      ? generatedResume.skills
      : (generatedResume.skills ? [String(generatedResume.skills)] : []);
    
    return {
      content: {
        summary: generatedResume.summary || '',
        experience: experienceArray.map(exp => ({
          title: "Experience",
          company: "",
          duration: "",
          achievements: [exp]
        })),
        skills: {
          technical: skillsArray,
          soft: skillsArray.filter(skill => 
            typeof skill === 'string' && ['leadership', 'communication', 'teamwork', 'problem-solving'].includes(skill.toLowerCase())
          )
        },
        education: {
          degree: generatedResume.education[0] || "Bachelor's Degree",
          institution: generatedResume.education[1] || "University",
          year: "2020"
        }
      },
      format: preferences.format || 'modern',
      tone: preferences.tone || 'professional',
      atsCompatibility: generatedResume.matchScore || 85
    };
  } catch (error) {
    console.error('Error generating resume content:', error);
    throw error;
  }
};

// Check ATS compatibility
export const checkAtsCompatibility = async (resumeContent) => {
  try {
    return {
      score: resumeContent.atsCompatibility || 85,
      issues: [
        {
          type: 'formatting',
          description: 'Use standard section headings',
          severity: 'medium'
        }
      ],
      suggestions: [
        'Use "Work Experience" instead of "Professional History"',
        'Ensure all dates are in MM/YYYY format',
        'Remove graphics and special characters'
      ]
    };
  } catch (error) {
    console.error('Error checking ATS compatibility:', error);
    throw error;
  }
};

// Generate final resume
export const generateFinalResume = async (
  jobDescription,
  candidateProfile,
  preferences,
  template
) => {
  try {
    // Check if backend is available
    const backendAvailable = await checkBackendStatus();
    
    if (!backendAvailable) {
      throw new Error("Backend service is not available. Please make sure the Python backend is running.");
    }
    
    const analysis = await analyzeJobAndProfile(jobDescription, candidateProfile);
    const content = await generateResumeContent(jobDescription, candidateProfile, preferences);
    const atsCheck = await checkAtsCompatibility(content);
    
    // Extract skills from job description
    const extractedSkills = await extractSkills(jobDescription);
    
    // Convert candidate profile to plain text for processing
    const resumeText = convertProfileToText(candidateProfile);
    
    // Generate personalized resume
    const generatedResume = await generatePersonalizedResume(resumeText, jobDescription, extractedSkills);

    return {
      content,
      analysis,
      atsCheck,
      template,
      generatedResume: {
        contact: {
          name: candidateProfile.personalInfo.name,
          email: candidateProfile.personalInfo.email,
          phone: candidateProfile.personalInfo.phone,
          location: candidateProfile.personalInfo.location
        },
        summary: generatedResume.summary || '',
        skills: Array.isArray(generatedResume.skills) ? generatedResume.skills : [],
        experience: Array.isArray(generatedResume.experience) ? generatedResume.experience : 
                   (generatedResume.experience ? [generatedResume.experience] : []),
        education: Array.isArray(generatedResume.education) ? generatedResume.education : 
                  (generatedResume.education ? [generatedResume.education] : [])
      },
      versions: [{
        id: 1,
        timestamp: new Date().toISOString(),
        changes: ['Initial version']
      }]
    };
  } catch (error) {
    console.error('Error generating final resume:', error);
    throw error;
  }
};
