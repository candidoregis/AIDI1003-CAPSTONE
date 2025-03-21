import { analyzeBias, getChatCompletion } from './mockAiService';

// Helper function to extract keywords from job description
const extractKeywords = (jobDescription) => {
  const commonKeywords = {
    skills: ['javascript', 'react', 'node', 'python', 'java', 'sql', 'aws'],
    softSkills: ['leadership', 'communication', 'teamwork', 'problem-solving'],
    experience: ['years', 'senior', 'junior', 'lead', 'manager'],
    education: ['bachelor', 'master', 'phd', 'degree'],
  };

  const keywords = {};
  Object.entries(commonKeywords).forEach(([category, words]) => {
    keywords[category] = words.filter(word => 
      jobDescription.toLowerCase().includes(word.toLowerCase())
    );
  });

  return keywords;
};

// Analyze job description and candidate profile
export const analyzeJobAndProfile = async (jobDescription, candidateProfile) => {
  try {
    // Extract keywords from job description
    const keywords = extractKeywords(jobDescription);

    // Mock response for development
    return {
      keywordMatch: {
        matched: ['javascript', 'react', 'leadership'],
        missing: ['aws', 'python'],
        partial: ['node.js']
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
        critical: ['AWS certification'],
        recommended: ['Python basics', 'Docker'],
        nice: ['GraphQL']
      },
      atsScore: 85,
      improvements: [
        'Add more quantifiable achievements',
        'Include specific AWS projects',
        'Highlight team leadership experience'
      ]
    };
  } catch (error) {
    console.error('Error analyzing job and profile:', error);
    throw error;
  }
};

// Generate optimized resume content
export const generateResumeContent = async (jobDescription, candidateProfile, preferences) => {
  try {
    const sections = {
      summary: "Experienced software engineer with a proven track record in full-stack development...",
      experience: [
        {
          title: "Senior Software Engineer",
          company: "Tech Corp",
          duration: "2020 - Present",
          achievements: [
            "Led development of cloud-native applications using React and Node.js",
            "Reduced system response time by 40% through optimization",
            "Mentored 5 junior developers"
          ]
        }
      ],
      skills: {
        technical: ["JavaScript", "React", "Node.js", "AWS", "Python"],
        soft: ["Leadership", "Communication", "Problem Solving"]
      },
      education: {
        degree: "Bachelor of Science in Computer Science",
        institution: "Tech University",
        year: "2018"
      }
    };

    return {
      content: sections,
      format: preferences.format || 'modern',
      tone: preferences.tone || 'professional',
      atsCompatibility: 90
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
      score: 90,
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
    const analysis = await analyzeJobAndProfile(jobDescription, candidateProfile);
    const content = await generateResumeContent(jobDescription, candidateProfile, preferences);
    const atsCheck = await checkAtsCompatibility(content);

    return {
      content,
      analysis,
      atsCheck,
      template,
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
