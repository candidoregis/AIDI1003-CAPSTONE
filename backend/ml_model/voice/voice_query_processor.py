"""
Voice Query Processor Module

This module contains the VoiceQueryProcessor class that handles voice query
processing for job search functionality.
"""

import os
import re
import nltk
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import joblib
import gc
import multiprocessing
from contextlib import contextmanager

from ..nlp_processor import NLPProcessor

# Download required NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

@contextmanager
def poolcontext(*args, **kwargs):
    """
    Context manager to properly clean up multiprocessing pools.
    """
    pool = multiprocessing.Pool(*args, **kwargs)
    try:
        yield pool
    finally:
        pool.terminate()
        pool.join()
        del pool
        gc.collect()

# Helper function for processing text batches
def process_text_batch(texts):
    """Process a batch of text data."""
    # Get the VoiceQueryProcessor instance
    processor = VoiceQueryProcessor.get_instance()
    return [processor.preprocess_text(text) for text in texts]

class VoiceQueryProcessor(NLPProcessor):
    """
    Process voice queries to extract job requirements and match with available jobs.
    """
    # Class variable to store the singleton instance
    _instance = None
    
    def __new__(cls):
        """
        Create a singleton instance of the VoiceQueryProcessor.
        
        Returns:
            VoiceQueryProcessor: Singleton instance
        """
        if cls._instance is None:
            cls._instance = super(VoiceQueryProcessor, cls).__new__(cls)
            cls._instance._voice_initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialize the VoiceQueryProcessor with required data and models.
        """
        super().__init__()
        
        if self._voice_initialized:
            return
            
        # Initialize data
        self.job_data = None
        self.job_vectors = None
        
        # Initialize models
        self.models_loaded = False
        
        self._voice_initialized = True
    
    def _load_models_and_data(self):
        """
        Load models and data required for voice query processing.
        """
        if self.models_loaded:
            return
        
        # Define paths to data files
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        job_postings_path = os.path.join(data_dir, 'job_postings.csv')
        
        # Path to the LinkedIn job postings in the src/dataset folder
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        linkedin_job_postings_path = os.path.join(project_root, 'src', 'dataset', 'linkedin_job_postings.csv')
        
        # Create the data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        
        # Check if LinkedIn job postings file exists
        if os.path.exists(linkedin_job_postings_path):
            print(f"VoiceQueryProcessor: Using LinkedIn job postings data from {linkedin_job_postings_path}")
            
            try:
                # Read the LinkedIn job postings data
                linkedin_data = pd.read_csv(linkedin_job_postings_path)
                print(f"VoiceQueryProcessor: Found {len(linkedin_data)} LinkedIn job postings")
                
                # Map LinkedIn data columns to our expected format
                # Adjust these mappings based on the actual structure of your LinkedIn data
                job_data = pd.DataFrame({
                    'job_id': linkedin_data.index.astype(str),
                    'job_title': linkedin_data['Job Title'].fillna(''),
                    'company_name': linkedin_data['Company Name'].fillna(''),
                    'job_location': linkedin_data['Location'].fillna(''),
                    'job_description': linkedin_data['Description'].fillna(''),
                    'job_skills': linkedin_data['Skills'].fillna('')
                })
                
                # Save the transformed data to our format
                job_data.to_csv(job_postings_path, index=False)
                print(f"VoiceQueryProcessor: Transformed LinkedIn data saved to {job_postings_path}")
            except Exception as e:
                print(f"VoiceQueryProcessor: Error processing LinkedIn data: {str(e)}")
                print("VoiceQueryProcessor: Falling back to sample data")
                # If there's an error with the LinkedIn data, fall back to sample data
                if not os.path.exists(job_postings_path):
                    self._create_sample_job_data(job_postings_path)
        else:
            print(f"VoiceQueryProcessor: LinkedIn job postings not found at {linkedin_job_postings_path}")
            # Create sample data if needed
            if not os.path.exists(job_postings_path):
                self._create_sample_job_data(job_postings_path)
            else:
                print(f"VoiceQueryProcessor: Using existing job postings data from {job_postings_path}")
        
        # Load job data
        columns_to_read = ['job_id', 'job_title', 'company_name', 'job_location', 'job_description', 'job_skills']
        
        if os.path.exists(job_postings_path):
            self.job_data = pd.read_csv(job_postings_path, usecols=columns_to_read)
            print(f"VoiceQueryProcessor: Loaded {len(self.job_data)} job postings")
            
            # Preprocess job descriptions
            job_descriptions = self.job_data['job_description'].fillna('').tolist()
            processed_descriptions = self.batch_process_text(job_descriptions)
            
            # Create TF-IDF vectorizer and transform job descriptions
            self.vectorizer = TfidfVectorizer(max_features=5000)
            self.job_vectors = self.vectorizer.fit_transform(processed_descriptions)
        else:
            # Create empty dataframe with required columns if file doesn't exist
            self.job_data = pd.DataFrame(columns=columns_to_read)
            self.vectorizer = TfidfVectorizer(max_features=5000)
            self.job_vectors = self.vectorizer.fit_transform([])
        
        # Set models loaded flag
        self.models_loaded = True
    
    def _create_sample_job_data(self, job_postings_path):
        """
        Create sample job data if real data is not available.
        
        Args:
            job_postings_path (str): Path to save the sample job data
        """
        print(f"VoiceQueryProcessor: Creating comprehensive sample job data at {job_postings_path}")
        # Create a more comprehensive sample dataset
        sample_data = {
            'job_id': [],
            'job_title': [],
            'company_name': [],
            'job_location': [],
            'job_description': [],
            'job_skills': []
        }
        
        # Software Engineering roles
        sample_data['job_id'].append('1')
        sample_data['job_title'].append('Senior Software Engineer')
        sample_data['company_name'].append('Tech Innovations Inc')
        sample_data['job_location'].append('San Francisco, CA')
        sample_data['job_description'].append('We are looking for a senior software engineer with 5+ years of experience in Python, JavaScript, and cloud technologies. The ideal candidate will lead development of our core platform, mentor junior developers, and collaborate with product teams to deliver high-quality software solutions.')
        sample_data['job_skills'].append('python,javascript,react,node.js,aws,cloud architecture,leadership')
        
        sample_data['job_id'].append('2')
        sample_data['job_title'].append('Full Stack Developer')
        sample_data['company_name'].append('WebSolutions Co')
        sample_data['job_location'].append('Austin, TX')
        sample_data['job_description'].append('Join our team as a Full Stack Developer to build responsive web applications using modern frameworks. You should have experience with React, Node.js, and database technologies. Knowledge of DevOps practices is a plus.')
        sample_data['job_skills'].append('javascript,react,node.js,mongodb,express,html,css,git')
        
        sample_data['job_id'].append('3')
        sample_data['job_title'].append('Frontend Engineer')
        sample_data['company_name'].append('UX Masters')
        sample_data['job_location'].append('Remote')
        sample_data['job_description'].append('We need a talented Frontend Engineer to create beautiful, responsive user interfaces. The ideal candidate has strong skills in React, TypeScript, and CSS, with a keen eye for design and user experience.')
        sample_data['job_skills'].append('react,typescript,css,html,redux,responsive design,ui/ux')
        
        # Data Science roles
        sample_data['job_id'].append('4')
        sample_data['job_title'].append('Senior Data Scientist')
        sample_data['company_name'].append('Data Insights Corp')
        sample_data['job_location'].append('New York, NY')
        sample_data['job_description'].append('We are seeking an experienced Data Scientist with expertise in machine learning, statistical analysis, and big data technologies. The role involves developing predictive models, analyzing complex datasets, and communicating insights to stakeholders.')
        sample_data['job_skills'].append('python,r,machine learning,statistics,sql,tensorflow,spark,data visualization')
        
        sample_data['job_id'].append('5')
        sample_data['job_title'].append('Machine Learning Engineer')
        sample_data['company_name'].append('AI Solutions')
        sample_data['job_location'].append('Seattle, WA')
        sample_data['job_description'].append('Join our AI team to develop and deploy machine learning models at scale. Experience with deep learning frameworks, MLOps, and cloud-based ML services is required. You will work on cutting-edge AI applications in computer vision and NLP.')
        sample_data['job_skills'].append('python,tensorflow,pytorch,deep learning,mlops,computer vision,nlp')
        
        # Product and Management roles
        sample_data['job_id'].append('6')
        sample_data['job_title'].append('Product Manager')
        sample_data['company_name'].append('Product Innovators')
        sample_data['job_location'].append('Chicago, IL')
        sample_data['job_description'].append('We need a strategic Product Manager with experience in agile methodologies and user research. You will lead product development from conception to launch, working closely with design, engineering, and marketing teams.')
        sample_data['job_skills'].append('agile,scrum,user research,product roadmap,market analysis,stakeholder management')
        
        sample_data['job_id'].append('7')
        sample_data['job_title'].append('Technical Project Manager')
        sample_data['company_name'].append('Project Solutions')
        sample_data['job_location'].append('Boston, MA')
        sample_data['job_description'].append('Looking for a Technical Project Manager to oversee software development projects. The ideal candidate has a technical background, experience with project management methodologies, and strong leadership skills.')
        sample_data['job_skills'].append('project management,agile,scrum,jira,technical background,leadership,risk management')
        
        # DevOps and Cloud roles
        sample_data['job_id'].append('8')
        sample_data['job_title'].append('DevOps Engineer')
        sample_data['company_name'].append('Cloud Systems Inc')
        sample_data['job_location'].append('Denver, CO')
        sample_data['job_description'].append('Join our DevOps team to build and maintain CI/CD pipelines, automate infrastructure, and improve system reliability. Experience with AWS, Kubernetes, and infrastructure as code is required.')
        sample_data['job_skills'].append('aws,kubernetes,docker,terraform,jenkins,ci/cd,linux,automation')
        
        sample_data['job_id'].append('9')
        sample_data['job_title'].append('Cloud Architect')
        sample_data['company_name'].append('Cloud Innovations')
        sample_data['job_location'].append('Atlanta, GA')
        sample_data['job_description'].append('We are looking for a Cloud Architect to design and implement scalable, secure cloud solutions. Deep knowledge of AWS or Azure services, networking, and security best practices is essential.')
        sample_data['job_skills'].append('aws,azure,cloud architecture,networking,security,infrastructure design,cost optimization')
        
        # Specialized roles
        sample_data['job_id'].append('10')
        sample_data['job_title'].append('Cybersecurity Analyst')
        sample_data['company_name'].append('SecureTech')
        sample_data['job_location'].append('Washington, DC')
        sample_data['job_description'].append('Join our security team to protect our systems and data from cyber threats. Responsibilities include security monitoring, incident response, vulnerability assessment, and implementing security controls.')
        sample_data['job_skills'].append('cybersecurity,incident response,vulnerability assessment,security tools,network security')
        
        pd.DataFrame(sample_data).to_csv(job_postings_path, index=False)
    
    def extract_job_requirements(self, voice_query):
        """
        Extract job requirements from a voice query.
        
        Args:
            voice_query (str): Voice query text
            
        Returns:
            dict: Dictionary containing extracted job requirements
        """
        # Ensure models and data are loaded
        print(f"VoiceQueryProcessor: Loading models for extract_job_requirements")
        self._load_models_and_data()
        print(f"VoiceQueryProcessor: Models loaded successfully")
        
        # Preprocess the query
        print(f"VoiceQueryProcessor: Preprocessing query: {voice_query[:50]}...")
        processed_query = self.preprocess_text(voice_query)
        print(f"VoiceQueryProcessor: Processed query: {processed_query[:50]}...")
        
        # Extract job title
        print(f"VoiceQueryProcessor: Extracting job title")
        job_title_patterns = [
            r'looking for(?: a)? (.+?) job',
            r'find(?: a)? (.+?) job',
            r'search for(?: a)? (.+?) job',
            r'(.+?) position',
            r'(.+?) role',
            r'jobs? (?:as|for)(?: a)? (.+)',
            r'(?:want|looking) to (?:be|work as)(?: a)? (.+)'
        ]
        
        job_title = None
        for pattern in job_title_patterns:
            match = re.search(pattern, voice_query.lower())
            if match:
                job_title = match.group(1).strip()
                print(f"VoiceQueryProcessor: Found job title: {job_title}")
                break
        
        # Extract location
        print(f"VoiceQueryProcessor: Extracting location")
        location_patterns = [
            r'in (.+?)(?:,|\.|$)',
            r'near (.+?)(?:,|\.|$)',
            r'at (.+?)(?:,|\.|$)',
            r'around (.+?)(?:,|\.|$)',
            r'(?:location|area|city|region|state|country)(?: is| in)? (.+?)(?:,|\.|$)'
        ]
        
        location = None
        for pattern in location_patterns:
            match = re.search(pattern, voice_query.lower())
            if match:
                location = match.group(1).strip()
                print(f"VoiceQueryProcessor: Found location: {location}")
                break
        
        # Extract experience level
        print(f"VoiceQueryProcessor: Extracting experience level")
        experience_patterns = [
            r'(\d+)(?:\+)? years? (?:of )?experience',
            r'experience (?:of )?(\d+)(?:\+)? years?',
            r'(?:senior|junior|mid-level|entry-level)'
        ]
        
        experience = None
        for pattern in experience_patterns:
            match = re.search(pattern, voice_query.lower())
            if match:
                if match.groups():
                    experience = f"{match.group(1)}+ years"
                else:
                    experience = match.group(0)
                print(f"VoiceQueryProcessor: Found experience: {experience}")
                break
        
        # Extract skills
        print(f"VoiceQueryProcessor: Extracting skills")
        common_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'express', 
            'django', 'flask', 'spring', 'html', 'css', 'sql', 'nosql', 'mongodb', 
            'postgresql', 'mysql', 'oracle', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'ci/cd', 'git', 'agile', 'scrum', 'leadership', 'communication', 'teamwork',
            'problem solving', 'critical thinking', 'data analysis', 'machine learning',
            'ai', 'artificial intelligence', 'deep learning', 'nlp', 'natural language processing'
        ]
        
        skills = []
        for skill in common_skills:
            if skill in processed_query or skill in voice_query.lower():
                skills.append(skill)
                print(f"VoiceQueryProcessor: Found skill: {skill}")
        
        # Extract keywords using TF-IDF
        if not skills and job_title:
            print(f"VoiceQueryProcessor: No skills found, extracting keywords from job title")
            # Use job title to find related keywords
            try:
                keywords = self.extract_keywords(job_title, top_n=5)
                print(f"VoiceQueryProcessor: Extracted keywords: {keywords}")
                skills.extend(keywords)
            except Exception as e:
                print(f"VoiceQueryProcessor: Error extracting keywords: {str(e)}")
        
        # Return the extracted requirements
        result = {
            'job_title': job_title,
            'location': location,
            'experience': experience,
            'skills': skills,
            'processed_query': processed_query
        }
        print(f"VoiceQueryProcessor: Returning requirements: {result}")
        return result
    
    def find_matching_jobs(self, query, max_results=10):
        """
        Find jobs matching a query.
        
        Args:
            query (str): Query text
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of matching jobs
        """
        # Ensure models and data are loaded
        print(f"VoiceQueryProcessor: Loading models for find_matching_jobs")
        self._load_models_and_data()
        print(f"VoiceQueryProcessor: Models loaded successfully")
        
        # Check if we have job data
        if self.job_data.empty or self.job_vectors.shape[0] == 0:
            print(f"VoiceQueryProcessor: No job data available")
            return []
        
        # Preprocess the query
        print(f"VoiceQueryProcessor: Preprocessing query: {query[:50]}...")
        processed_query = self.preprocess_text(query)
        print(f"VoiceQueryProcessor: Processed query: {processed_query[:50]}...")
        
        # Vectorize the query
        print(f"VoiceQueryProcessor: Vectorizing query")
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculate cosine similarity between the query and all jobs
        # Process in batches to reduce memory usage
        batch_size = 1000
        total_jobs = self.job_vectors.shape[0]
        similarities = np.zeros(total_jobs)
        
        for i in range(0, total_jobs, batch_size):
            end_idx = min(i + batch_size, total_jobs)
            batch_vectors = self.job_vectors[i:end_idx]
            
            batch_similarities = cosine_similarity(query_vector, batch_vectors).flatten()
            similarities[i:end_idx] = batch_similarities
        
        # Get the indices of the top matching jobs
        top_indices = np.argsort(similarities)[::-1][:max_results]
        
        # Create a list of matching jobs with confidence scores
        matching_jobs = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Only include jobs with a minimum similarity
                job = self.job_data.iloc[idx]
                
                # Extract skills from job_skills field
                skills = []
                if job['job_skills']:
                    skills = [skill.strip() for skill in job['job_skills'].split(',')[:5]]
                
                # Create a job object with native Python types (not NumPy types)
                job_obj = {
                    'id': str(job.get('job_id', str(idx))),  # Convert to string to ensure JSON serializable
                    'title': str(job['job_title']),
                    'company': str(job['company_name']),
                    'location': str(job['job_location']),
                    'description': str(job['job_description'][:200] + '...' if len(job['job_description']) > 200 else job['job_description']),
                    'skills': skills,
                    'confidence': float(similarities[idx])  # Convert numpy.float64 to Python float
                }
                
                matching_jobs.append(job_obj)
        
        print(f"VoiceQueryProcessor: Returning matching jobs: {matching_jobs}")
        return matching_jobs
