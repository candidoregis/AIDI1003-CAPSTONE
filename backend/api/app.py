"""
Flask API for HR Recruitment Frontend

This module provides the REST API endpoints for the HR Recruitment Frontend application.
It serves as the backend for the React frontend and handles:
1. Voice query processing - Converting voice queries into job requirements and finding matches
2. Resume generation - Creating personalized resumes based on job descriptions
3. Resume analysis - Extracting skills and matching resumes with job requirements
4. Chat functionality - Providing AI-powered conversational assistance for recruitment tasks

The API uses two specialized NLP processors that inherit from a shared base class:
- VoiceQueryProcessor: Handles voice search functionality for job matching
- ResumeProcessor: Handles resume generation, skill extraction, and resume matching
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import numpy as np
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

# Initialize app configuration
app.config['RECENT_JOB_MATCHES'] = []

# Initialize processors
voice_processor = None
resume_processor = None

def load_models_if_needed():
    """
    Load models if they haven't been loaded yet.
    
    This function is used to lazy-load the models, ensuring they are only loaded when needed.
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
    
    Returns a simple JSON response indicating the API is running.
    """
    return jsonify({'status': 'API is running'})

@app.route('/api/model-status')
def model_status():
    """
    Check if the models are loaded and ready.
    
    Returns a JSON response indicating the status of the models.
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
    
    Expects a JSON payload with a 'query' field containing the voice query.
    
    Returns a JSON response with the extracted job requirements and matching jobs.
    """
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Process the query
        load_models_if_needed()
        
        try:
            # Extract job requirements
            requirements = voice_processor.extract_job_requirements(query)
            
            # Find matching jobs
            matching_jobs = voice_processor.find_matching_jobs(query, max_results=10)
            
            # Convert to JSON serializable objects
            requirements = convert_to_json_serializable(requirements)
            matching_jobs = convert_to_json_serializable(matching_jobs)
            
            # Return the results
            return jsonify({
                'requirements': requirements,
                'matchingJobs': matching_jobs
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract-job-requirements', methods=['POST'])
def extract_job_requirements():
    """
    Extract job requirements from a voice query.
    
    Expects a JSON payload with a 'query' field containing the voice query.
    
    Returns a JSON response with the extracted job requirements.
    """
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Process the query
        load_models_if_needed()
        
        # Extract job requirements
        requirements = voice_processor.extract_job_requirements(query)
        
        # Convert to JSON serializable objects
        requirements = convert_to_json_serializable(requirements)
        
        # Return the results
        return jsonify({'requirements': requirements})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract-skills', methods=['POST'])
def extract_skills():
    """
    Extract skills from a job description.
    
    Expects a JSON payload with a 'jobDescription' field containing the job description.
    
    Returns a JSON response with the extracted skills.
    """
    try:
        data = request.json
        job_description = data.get('jobDescription', '')
        
        if not job_description:
            return jsonify({'error': 'No job description provided'}), 400
        
        # Process the job description
        load_models_if_needed()
        
        # Extract skills
        skills = resume_processor.extract_skills(job_description)
        
        # Convert to JSON serializable objects
        skills = convert_to_json_serializable(skills)
        
        # Return the results
        return jsonify({'skills': skills})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/match-resume', methods=['POST'])
def match_resume():
    """
    Match a resume with job skills.
    
    Expects a JSON payload with 'resume' and 'jobSkills' fields.
    
    Returns a JSON response with the match result.
    """
    try:
        data = request.json
        resume = data.get('resume', '')
        job_skills = data.get('jobSkills', [])
        
        if not resume:
            return jsonify({'error': 'No resume provided'}), 400
        
        if not job_skills:
            return jsonify({'error': 'No job skills provided'}), 400
        
        # Process the resume and job skills
        load_models_if_needed()
        
        # Match resume with job skills
        match_result = resume_processor.match_resume(resume, job_skills)
        
        # Convert to JSON serializable objects
        match_result = convert_to_json_serializable(match_result)
        
        # Return the results
        return jsonify(match_result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-resume', methods=['POST'])
def generate_resume():
    """
    Generate a personalized resume based on job description and extracted skills.
    
    Expects a JSON payload with 'resume', 'jobDescription', and 'extractedSkills' fields.
    
    Returns a JSON response with the generated resume.
    """
    try:
        data = request.json
        resume = data.get('resume', '')
        job_description = data.get('jobDescription', '')
        extracted_skills = data.get('extractedSkills', [])
        
        if not resume:
            return jsonify({'error': 'No resume provided'}), 400
        
        if not job_description:
            return jsonify({'error': 'No job description provided'}), 400
        
        # Process the resume, job description, and extracted skills
        load_models_if_needed()
        
        # Generate personalized resume
        result = resume_processor.generate_resume(resume, job_description, extracted_skills)
        
        # Convert to JSON serializable objects
        result = convert_to_json_serializable(result)
        
        # Return the results
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Process a chat message and return a response.
    
    Expects a JSON payload with a 'messages' field containing the chat history.
    
    Returns a JSON response with the generated response.
    """
    try:
        # Get the messages from the request
        messages = request.json.get('messages', [])
        
        if not messages:
            return jsonify({'error': 'No messages found'}), 400
        
        # Get the last user message
        user_messages = [m for m in messages if m.get('role') == 'user']
        if not user_messages:
            return jsonify({'error': 'No user message found'}), 400
            
        last_user_message = user_messages[-1].get('content', '')
        
        # Process the message using NLP
        load_models_if_needed()
        
        try:
            # Generate a response based on the message content
            response = generate_chat_response(last_user_message)
            
            # Return the response
            return jsonify({
                'response': response,
                'timestamp': datetime.datetime.now().isoformat()
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'response': "I'm having trouble processing your request right now. Could you try again with a different question?",
                'timestamp': datetime.datetime.now().isoformat(),
                'error': str(e)
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def generate_chat_response(message):
    """
    Generate a response to a chat message using NLP.
    
    This function analyzes the user's message to identify the intent and generates
    an appropriate response. It can recognize several types of intents:
    - Greetings: Responds with a welcome message
    - Job inquiries: Uses the voice processor to find matching jobs and offers options
    - Job selection: Provides detailed information about a selected job
    - Resume assistance: Offers help with resume optimization
    - Interview scheduling: Provides interview scheduling assistance
    - Gratitude expressions: Acknowledges thanks
    - Farewells: Provides a goodbye message
    
    If no specific intent is recognized, it returns a default response to keep
    the conversation going.
    
    Args:
        message (str): The user's message
        
    Returns:
        str: The generated response based on the identified intent
    """
    # Process the message to understand intent
    message_lower = message.lower()
    
    # First check for job search intent - this takes priority over greetings
    # Check for job-related keywords or phrases
    job_search_keywords = ['job', 'position', 'opening', 'vacancy', 'work', 'career', 'looking for', 'find', 'search', 'designer', 'engineer', 'developer', 'manager', 'analyst']
    
    # Check if any job search keyword is in the message
    is_job_search = any(keyword in message_lower for keyword in job_search_keywords)
    
    if is_job_search:
        # Use the voice query processor to find relevant jobs
        try:
            # Ensure voice processor is initialized
            global voice_processor
            if voice_processor is None:
                voice_processor = VoiceQueryProcessor()
            
            # Extract job requirements using the same NLP processor as voice search
            job_requirements = voice_processor.extract_job_requirements(message)
            
            matching_jobs = voice_processor.find_matching_jobs(message, max_results=4)
            
            if matching_jobs:
                # Format job options with numbers for selection
                job_options = []
                for i, job in enumerate(matching_jobs, 1):
                    job_options.append(f"{i}. {job['title']} at {job['company']} ({job['location']})")
                
                # Store the matching jobs in the global variable for later reference
                app.config['RECENT_JOB_MATCHES'] = matching_jobs
                
                response = "I found these job opportunities that might interest you:\n\n"
                response += "\n".join(job_options)
                response += "\n\nWhich one would you like to know more about? You can reply with the number or job title."
                return response
            else:
                return "I couldn't find any matching jobs at the moment. Could you tell me more about what you're looking for?"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return "I'd be happy to help you find job opportunities. Could you tell me more about what kind of position you're looking for? (Note: I encountered an error processing your request, but I'm still here to help.)"
    
    # Check for greeting intent - only if not a job search
    elif any(keyword in message_lower for keyword in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! I'm your AI recruitment assistant. How can I help you today?"
    
    # Check for job selection intent (when user selects a job from the list)
    elif app.config.get('RECENT_JOB_MATCHES') and (
            message_lower.isdigit() or 
            any(job['title'].lower() in message_lower for job in app.config.get('RECENT_JOB_MATCHES', []))
        ):
        
        try:
            recent_jobs = app.config.get('RECENT_JOB_MATCHES', [])
            selected_job = None
            
            # Check if the user entered a number
            if message_lower.isdigit():
                job_index = int(message_lower) - 1
                if 0 <= job_index < len(recent_jobs):
                    selected_job = recent_jobs[job_index]
            
            # If not found by number, try to match by title
            if not selected_job:
                for job in recent_jobs:
                    if job['title'].lower() in message_lower:
                        selected_job = job
                        break
            
            if selected_job:
                # Format detailed job information
                response = f"## {selected_job['title']} at {selected_job['company']}\n\n"
                response += f"**Location:** {selected_job['location']}\n\n"
                response += f"**Description:**\n{selected_job['description']}\n\n"
                
                if selected_job.get('skills') and len(selected_job['skills']) > 0:
                    response += f"**Required Skills:**\n"
                    for skill in selected_job['skills']:
                        response += f"- {skill}\n"
                    response += "\n"
                
                response += f"**Match Confidence:** {selected_job.get('confidence', 0) * 100:.1f}%\n\n"
                response += "Would you like to apply for this position or see other job opportunities?"
                return response
            else:
                return "I'm sorry, I couldn't find that job in our recent results. Please select one of the options I provided or start a new job search."
        except Exception as e:
            import traceback
            traceback.print_exc()
            return "I'm having trouble retrieving the job details right now. Could you try selecting the job again or starting a new search?"
    
    # Check for resume assistance intent
    elif any(keyword in message_lower for keyword in ['resume', 'cv']):
        return "I can help you optimize your resume for specific job positions. Would you like me to analyze your resume or help you create a personalized one?"
    
    # Check for interview scheduling intent
    elif any(keyword in message_lower for keyword in ['interview', 'schedule']):
        return "I can help you schedule an interview. What date and time works best for you?"
    
    # Check for gratitude intent
    elif any(keyword in message_lower for keyword in ['thank', 'thanks']):
        return "You're welcome! Is there anything else I can help you with?"
    
    # Check for farewell intent
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
    
    # Return a random default response to maintain conversation flow
    return random.choice(default_responses)

if __name__ == '__main__':
    # Run the Flask application on port 5004, accessible from any IP address
    app.run(debug=True, host='0.0.0.0', port=5004)
