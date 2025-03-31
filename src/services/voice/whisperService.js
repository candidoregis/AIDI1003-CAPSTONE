import OpenAI from 'openai';
import axios from 'axios';

const openai = new OpenAI({
  apiKey: process.env.REACT_APP_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true // Note: Only for development. In production, these calls should go through your backend
});

export const processVoiceInput = async (transcript) => {
  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: `You are an HR assistant. Parse the following voice input and extract job search criteria 
                   such as role, experience level, skills, location, and any other relevant parameters.
                   Return the result in a structured JSON format.`
        },
        {
          role: "user",
          content: transcript
        }
      ]
    });

    return JSON.parse(response.choices[0].message.content);
  } catch (error) {
    console.error('Error processing voice input:', error);
    throw error;
  }
};

export const analyzeVoiceTone = async (audioBlob) => {
  try {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.webm');
    formData.append('model', 'whisper-1');

    const response = await openai.audio.transcriptions.create({
      file: audioBlob,
      model: 'whisper-1'
    });

    const transcript = response.text;

    // Analyze tone using GPT-4
    const toneAnalysis = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: "Analyze the following speech for confidence, clarity, and professionalism. Provide a brief assessment."
        },
        {
          role: "user",
          content: transcript
        }
      ]
    });

    return {
      transcript,
      analysis: toneAnalysis.choices[0].message.content
    };
  } catch (error) {
    console.error('Error analyzing voice:', error);
    throw error;
  }
};

export const getJobSuggestions = async (criteria) => {
  try {
    // This would typically call your backend API
    // For now, we'll simulate with a mock response
    return {
      suggestions: [
        {
          id: 1,
          title: "Senior Software Engineer",
          company: "Tech Corp",
          location: "Remote",
          skills: ["React", "Node.js", "Python"],
          experience: "5+ years",
          confidenceScore: 0.95
        },
        {
          id: 2,
          title: "Full Stack Developer",
          company: "Innovation Labs",
          location: "New York, NY",
          skills: ["JavaScript", "React", "MongoDB"],
          experience: "3+ years",
          confidenceScore: 0.88
        }
      ]
    };
  } catch (error) {
    console.error('Error getting job suggestions:', error);
    throw error;
  }
};
