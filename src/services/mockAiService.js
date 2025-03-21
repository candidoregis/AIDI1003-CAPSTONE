// Mock AI responses for development and testing
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const mockResponses = {
  chat: [
    "I'd be happy to help you with that! What specific information are you looking for?",
    "Based on your experience, I think you'd be a great fit for our software engineering positions.",
    "The interview process typically consists of: 1) Initial screening, 2) Technical interview, 3) Culture fit interview.",
    "I can help you schedule an interview. What date and time works best for you?",
    "Let me check the available positions that match your skills.",
    "Our company offers competitive benefits including health insurance, 401(k), and flexible work hours.",
  ],
  
  resume: {
    skills: ["JavaScript", "React", "Node.js", "Python", "SQL"],
    experience: "5 years",
    education: "Bachelor's in Computer Science",
    achievements: ["Led team of 5 developers", "Reduced system downtime by 40%"],
    roleMatches: ["Senior Software Engineer", "Technical Lead", "Full Stack Developer"]
  },

  ranking: [
    {
      candidateName: "John Doe",
      score: 85,
      strengths: ["Technical expertise", "Leadership experience", "Communication skills"]
    },
    {
      candidateName: "Jane Smith",
      score: 92,
      strengths: ["Relevant industry experience", "Project management", "Innovation"]
    }
  ],

  biasAnalysis: {
    genderBias: {
      found: false,
      suggestions: []
    },
    ageBias: {
      found: false,
      suggestions: []
    },
    ethnicityBias: {
      found: false,
      suggestions: []
    }
  },

  videoAnalysis: {
    communication: {
      clarity: 90,
      confidence: 85,
      engagement: 88
    },
    keyTopics: ["Technical skills", "Team collaboration", "Problem-solving"],
    overallImpression: "Strong candidate with excellent communication skills"
  }
};

// Helper function to get random response
const getRandomResponse = (responses) => {
  return responses[Math.floor(Math.random() * responses.length)];
};

// Mock AI service functions
export const getChatCompletion = async (messages) => {
  await delay(1000); // Simulate API delay
  return {
    message: getRandomResponse(mockResponses.chat),
    timestamp: new Date().toISOString()
  };
};

export const analyzeResume = async (resumeText) => {
  await delay(1500);
  return {
    ...mockResponses.resume,
    timestamp: new Date().toISOString()
  };
};

export const rankCandidates = async (jobDescription, candidates) => {
  await delay(1500);
  return {
    rankings: mockResponses.ranking,
    timestamp: new Date().toISOString()
  };
};

export const analyzeSkillGaps = async (jobRequirements, candidateSkills) => {
  await delay(1000);
  return {
    missingSkills: ["Cloud Architecture", "DevOps"],
    recommendations: [
      "AWS Certification course",
      "Docker and Kubernetes training"
    ],
    timestamp: new Date().toISOString()
  };
};

export const analyzeBias = async (text) => {
  await delay(1000);
  return {
    ...mockResponses.biasAnalysis,
    timestamp: new Date().toISOString()
  };
};

export const analyzeVideoInterview = async (transcriptData, sentimentData) => {
  await delay(2000);
  return {
    ...mockResponses.videoAnalysis,
    timestamp: new Date().toISOString()
  };
};

export const predictCandidateSuccess = async (candidateData, jobData) => {
  await delay(1500);
  return {
    successProbability: 85,
    strengths: ["Technical skills", "Team fit", "Experience"],
    areas_for_growth: ["Leadership", "Public speaking"],
    timestamp: new Date().toISOString()
  };
};
