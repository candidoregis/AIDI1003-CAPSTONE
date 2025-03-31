"""
Flask API for HR Recruitment Frontend

This module provides the API endpoints for the HR Recruitment Frontend application.
It handles voice query processing, resume generation, and other HR-related tasks.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import gc
import numpy as np
from contextlib import contextmanager
import json
import random
import datetime

# Add the parent directory to the path so we can import the ml_model package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the processors
from ml_model.voice.voice_query_processor import VoiceQueryProcessor
from ml_model.resume.resume_processor import ResumeProcessor

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Initialize processors
voice_processor = None
resume_processor = None

def load_models_if_needed():
    """
    Load models if they haven't been loaded yet.
    """
    global voice_processor, resume_processor
    
    if voice_processor is None:
        voice_processor = VoiceQueryProcessor()
    
    if resume_processor is None:
        resume_processor = ResumeProcessor()

# Helper function to convert NumPy types to Python native types
def convert_to_json_serializable(obj):
    """
    Convert NumPy types to Python native types for JSON serialization.
    
    Args:
        obj: Object to convert
        
    Returns:
        Object with NumPy types converted to Python native types
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_json_serializable(item) for item in obj)
    else:
        return obj

@app.route('/')
def index():
    """
    Root endpoint.
    """
    return jsonify({'status': 'API is running'})

@app.route('/api/model-status')
def model_status():
    """
    Check if the models are loaded and ready.
    """
    try:
        # Attempt to load models if not already loaded
        load_models_if_needed()
        
        return jsonify({
            'status': 'ready',
            'message': 'Models are loaded and ready'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error loading models: {str(e)}'
        }), 500

@app.route('/api/process-voice-query', methods=['POST'])
def process_voice_query():
    """
    Process a voice query and return matching jobs.
    """
    try:
        print("Received voice query request")
        data = request.json
        print(f"Request data: {data}")
        
        query = data.get('query', '')
        print(f"Query: {query}")
        
        if not query:
            print("Error: No query provided")
            return jsonify({'error': 'No query provided'}), 400
        
        # Process the query
        print("Loading models for voice query processing...")
        load_models_if_needed()
        print("Models loaded successfully")
        
        try:
            # Extract job requirements
            print(f"Extracting job requirements from query: {query[:50]}...")
            requirements = voice_processor.extract_job_requirements(query)
            print(f"Extracted requirements: {requirements}")
            
            # Find matching jobs
            print("Finding matching jobs...")
            matching_jobs = voice_processor.find_matching_jobs(query, max_results=10)
            print(f"Found {len(matching_jobs)} matching jobs")
            
            # Convert to JSON serializable objects
            requirements = convert_to_json_serializable(requirements)
            matching_jobs = convert_to_json_serializable(matching_jobs)
            
            # Return the results
            print("Returning results")
            return jsonify({
                'requirements': requirements,
                'matchingJobs': matching_jobs
            })
        except Exception as e:
            print(f"Error in voice query processing: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        print(f"Unexpected error in process_voice_query: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract-job-requirements', methods=['POST'])
def extract_job_requirements():
    """
    Extract job requirements from a voice query.
    """
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Extract job requirements
    load_models_if_needed()
    requirements = voice_processor.extract_job_requirements(query)
    
    return jsonify(convert_to_json_serializable(requirements))

@app.route('/api/extract-skills', methods=['POST'])
def extract_skills():
    """
    Extract skills from a job description.
    """
    try:
        data = request.json
        print(f"Received data for extract-skills: {data}")
        
        job_description = data.get('jobDescription', '')
        print(f"Job description length: {len(job_description)}")
        
        if not job_description:
            print("Error: Job description is required")
            return jsonify({'error': 'Job description is required'}), 400
        
        # Extract skills
        print("Loading models for skill extraction...")
        load_models_if_needed()
        
        print("Extracting skills...")
        extracted_skills = resume_processor.extract_skills(job_description)
        
        print(f"Extracted skills: {extracted_skills}")
        return jsonify(convert_to_json_serializable(extracted_skills))
    except Exception as e:
        print(f"Error in extract_skills: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/match-resume', methods=['POST'])
def match_resume():
    """
    Match a resume with job skills.
    """
    try:
        data = request.json
        print(f"Received data: {data}")
        
        resume = data.get('resume', '')
        job_skills = data.get('jobSkills', [])
        
        print(f"Resume length: {len(resume)}")
        print(f"Job skills: {job_skills}")
        
        if not resume:
            print("Error: Resume is required")
            return jsonify({'error': 'Resume is required'}), 400
        
        if not job_skills:
            print("Error: Job skills are required")
            return jsonify({'error': 'Job skills are required'}), 400
        
        # Match resume with job skills
        print("Loading models...")
        load_models_if_needed()
        
        print("Matching resume...")
        match_result = resume_processor.match_resume(resume, job_skills)
        
        print(f"Match result: {match_result}")
        return jsonify(convert_to_json_serializable(match_result))
    except Exception as e:
        print(f"Error in match_resume: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-resume', methods=['POST'])
def generate_resume():
    """
    Generate a personalized resume based on job description and extracted skills.
    """
    try:
        data = request.json
        print(f"Received data for generate-resume: {data}")
        
        resume = data.get('resume', '')
        job_description = data.get('jobDescription', '')
        extracted_skills = data.get('extractedSkills', [])
        
        print(f"Resume length: {len(resume)}")
        print(f"Job description length: {len(job_description)}")
        print(f"Extracted skills: {extracted_skills}")
        
        if not resume:
            print("Error: Resume is required")
            return jsonify({'error': 'Resume is required'}), 400
        
        if not job_description:
            print("Error: Job description is required")
            return jsonify({'error': 'Job description is required'}), 400
        
        if not extracted_skills:
            print("Error: Extracted skills are required")
            return jsonify({'error': 'Extracted skills are required'}), 400
        
        # Generate resume
        print("Loading models for resume generation...")
        load_models_if_needed()
        
        print("Generating resume...")
        print(f"Resume first 100 chars: {resume[:100]}")
        print(f"Job description first 100 chars: {job_description[:100]}")
        print(f"Skills count: {len(extracted_skills)}")
        
        generated_resume = resume_processor.generate_resume(resume, job_description, extracted_skills)
        
        print("Resume generation result keys:", list(generated_resume.keys()) if isinstance(generated_resume, dict) else "Not a dict")
        if isinstance(generated_resume, dict) and 'personalized_resume' in generated_resume:
            print(f"Personalized resume length: {len(generated_resume['personalized_resume'])}")
            print(f"Personalized resume first 100 chars: {generated_resume['personalized_resume'][:100]}")
        
        print("Resume generated successfully")
        return jsonify(convert_to_json_serializable(generated_resume))
    except Exception as e:
        print(f"Error in generate_resume: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Process a chat message and return a response.
    """
    try:
        print("Received chat request")
        data = request.json
        print(f"Request data: {data}")
        
        messages = data.get('messages', [])
        if not messages:
            print("Error: No messages provided")
            return jsonify({'error': 'No messages provided'}), 400
        
        # Get the last user message
        last_user_message = None
        for message in reversed(messages):
            if message.get('role') == 'user':
                last_user_message = message.get('content')
                break
                
        if not last_user_message:
            print("Error: No user message found")
            return jsonify({'error': 'No user message found'}), 400
            
        print(f"Last user message: {last_user_message}")
        
        # Process the message using NLP
        load_models_if_needed()
        
        # Generate a response based on the message content
        response = generate_chat_response(last_user_message)
        
        print(f"Generated response: {response}")
        
        # Return the response
        return jsonify({
            'response': response,
            'timestamp': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def generate_chat_response(message):
    """
    Generate a response to a chat message using NLP.
    
    Args:
        message (str): The user's message
        
    Returns:
        str: The generated response
    """
    # Process the message to understand intent
    message_lower = message.lower()
    
    # Check for common intents
    if any(keyword in message_lower for keyword in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! I'm your AI recruitment assistant. How can I help you today?"
        
    elif any(keyword in message_lower for keyword in ['job', 'position', 'opening', 'vacancy']):
        # Use the voice query processor to find relevant jobs
        try:
            job_requirements = voice_processor.extract_job_requirements(message)
            matching_jobs = voice_processor.find_matching_jobs(message, max_results=3)
            
            if matching_jobs:
                job_titles = [job['title'] for job in matching_jobs]
                return f"I found some jobs that might interest you: {', '.join(job_titles)}. Would you like more details about any of these positions?"
            else:
                return "I couldn't find any matching jobs at the moment. Could you tell me more about what you're looking for?"
        except Exception as e:
            print(f"Error finding jobs: {str(e)}")
            return "I'd be happy to help you find job opportunities. Could you tell me more about what kind of position you're looking for?"
    
    elif any(keyword in message_lower for keyword in ['resume', 'cv']):
        return "I can help you optimize your resume for specific job positions. Would you like me to analyze your resume or help you create a personalized one?"
    
    elif any(keyword in message_lower for keyword in ['interview', 'schedule']):
        return "I can help you schedule an interview. What date and time works best for you?"
    
    elif any(keyword in message_lower for keyword in ['thank', 'thanks']):
        return "You're welcome! Is there anything else I can help you with?"
    
    elif any(keyword in message_lower for keyword in ['bye', 'goodbye']):
        return "Goodbye! Feel free to come back if you have more questions."
    
    # Default responses for when we don't understand the intent
    default_responses = [
        "I'd be happy to help with that. Could you provide more details?",
        "That's an interesting question. Let me help you with that.",
        "I'm here to assist with your recruitment needs. Could you elaborate a bit more?",
        "I'd like to help you with that. Can you give me more information?",
        "I'm your AI recruitment assistant. How can I assist you further with that request?"
    ]
    
    return random.choice(default_responses)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
