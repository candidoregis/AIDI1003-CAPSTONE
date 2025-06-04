import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import os
import gc
import multiprocessing
from contextlib import contextmanager

# Download necessary NLTK resources
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

# Helper function for processing job data batches
def process_job_batch(batch):
    """Process a batch of job data."""
    # Create a copy to avoid modifying the original
    batch_copy = batch.copy()
    
    # Get the DataProcessor instance
    processor = DataProcessor.get_instance()
    
    # Process job skills and description
    batch_copy['processed_skills'] = batch_copy['job_skills'].apply(processor.preprocess_text)
    batch_copy['processed_description'] = batch_copy['job_description'].apply(processor.preprocess_text)
    
    return batch_copy[['job_id', 'job_title', 'company_name', 'job_description', 
                      'job_location', 'job_skills', 'processed_skills', 'processed_description']]

# Helper function for processing resume data batches
def process_resume_batch(batch):
    """Process a batch of resume data."""
    # Create a copy to avoid modifying the original
    batch_copy = batch.copy()
    
    # Get the DataProcessor instance
    processor = DataProcessor.get_instance()
    
    # Process resume text
    batch_copy['processed_resume'] = batch_copy['Resume_str'].apply(processor.preprocess_text)
    
    return batch_copy

class DataProcessor:
    # Class variable to store the singleton instance
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of DataProcessor."""
        if cls._instance is None:
            cls._instance = cls()  # Create a default instance if none exists
        return cls._instance
    
    def __init__(self, data_dir=None):
        """
        Initialize the DataProcessor with the directory containing the dataset files.
        
        Args:
            data_dir (str, optional): Path to the directory containing the dataset files.
                If None, a default path will be used.
        """
        if data_dir is None:
            # Use a default path relative to the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)
            project_dir = os.path.dirname(backend_dir)
            data_dir = os.path.join(backend_dir, 'data')
            
            # Create the data directory if it doesn't exist
            os.makedirs(data_dir, exist_ok=True)
        
        self.data_dir = data_dir
        self.job_skills_df = None
        self.job_summary_df = None
        self.job_postings_df = None
        self.resume_df = None
        self.processed_job_data = None
        self.processed_resume_data = None
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Set the singleton instance
        DataProcessor._instance = self
        
    def load_data(self):
        """
        Load all datasets from the data directory.
        """
        print("Loading datasets...")
        
        # Load job skills data
        job_skills_path = os.path.join(self.data_dir, 'job_skills.csv')
        if os.path.exists(job_skills_path):
            self.job_skills_df = pd.read_csv(job_skills_path)
            print(f"Loaded job skills data: {self.job_skills_df.shape}")
        
        # Load job summary data
        job_summary_path = os.path.join(self.data_dir, 'job_summary.csv')
        if os.path.exists(job_summary_path):
            self.job_summary_df = pd.read_csv(job_summary_path)
            print(f"Loaded job summary data: {self.job_summary_df.shape}")
        
        # Load job postings data
        job_postings_path = os.path.join(self.data_dir, 'linkedin_job_postings.csv')
        if os.path.exists(job_postings_path):
            # Read only necessary columns to save memory
            self.job_postings_df = pd.read_csv(
                job_postings_path,
                usecols=['job_link', 'job_title', 'company', 'job_location', 'job_level', 'job_type']
            )
            print(f"Loaded job postings data: {self.job_postings_df.shape}")
            
            # Rename columns to standardize across the application
            self.job_postings_df = self.job_postings_df.rename(columns={
                'job_link': 'job_id',
                'company': 'company_name'
            })
            
            # Add empty columns for missing data that we need
            self.job_postings_df['job_description'] = self.job_postings_df['job_title'] + " " + self.job_postings_df['job_level'] + " " + self.job_postings_df['job_type']
            self.job_postings_df['job_skills'] = ""
            self.job_postings_df['job_work_from_home'] = False
        
        # Load resume data
        resume_path = os.path.join(self.data_dir, 'Resume.csv')
        if os.path.exists(resume_path):
            self.resume_df = pd.read_csv(resume_path)
            print(f"Loaded resume data: {self.resume_df.shape}")
    
    def preprocess_text(self, text):
        """
        Preprocess text by removing special characters, converting to lowercase,
        tokenizing, removing stopwords, and lemmatizing.
        
        Args:
            text (str): Text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        processed_tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        
        return ' '.join(processed_tokens)
    
    def extract_skills_from_job_description(self, job_skills_text):
        """
        Extract skills from job skills text.
        
        Args:
            job_skills_text (str): Text containing skills
            
        Returns:
            list: List of extracted skills
        """
        if not isinstance(job_skills_text, str):
            return []
        
        # Split by commas and clean up each skill
        skills = [skill.strip() for skill in job_skills_text.split(',')]
        return [skill for skill in skills if skill]  # Remove empty strings
    
    def process_job_data(self):
        """
        Process and merge job-related datasets.
        
        Returns:
            DataFrame: Processed job data
        """
        print("Processing job data...")
        
        # Check if we have the job postings data
        if self.job_postings_df is not None:
            # Create a copy to avoid modifying the original dataframe
            job_data = self.job_postings_df.copy()
            
            # Fill NaN values
            job_data.fillna('', inplace=True)
            
            # Process in smaller batches to reduce memory usage
            batch_size = 1000
            total_rows = len(job_data)
            
            # Create batches
            batches = []
            for i in range(0, total_rows, batch_size):
                end_idx = min(i + batch_size, total_rows)
                batches.append(job_data.iloc[i:end_idx])
            
            # Process batches using multiprocessing with proper resource management
            processed_batches = []
            with poolcontext(processes=min(multiprocessing.cpu_count(), 4)) as pool:
                processed_batches = pool.map(process_job_batch, batches)
            
            # Combine processed batches
            processed_df = pd.concat(processed_batches, ignore_index=True)
            
            # Clean up to free memory
            del batches, processed_batches, job_data
            gc.collect()
            
            self.processed_job_data = processed_df
            return processed_df
        else:
            print("Job postings data not loaded. Call load_data() first.")
            return pd.DataFrame()
    
    def process_resume_data(self):
        """
        Process resume dataset.
        
        Returns:
            DataFrame: Processed resume data
        """
        print("Processing resume data...")
        
        if self.resume_df is None:
            print("Resume data not loaded. Call load_data() first.")
            return pd.DataFrame()
        
        # Create a copy of the DataFrame instead of a view
        resume_df = self.resume_df[['Resume_str', 'Category']].copy()
        
        # Process in smaller batches to reduce memory usage
        batch_size = 100
        total_rows = len(resume_df)
        
        # Create batches
        batches = [resume_df[i:i+batch_size] for i in range(0, total_rows, batch_size)]
        
        # Process batches in parallel with proper resource management
        with poolcontext(processes=min(multiprocessing.cpu_count(), 4)) as pool:
            processed_batches = pool.map(process_resume_batch, batches)
        
        # Combine processed batches
        processed_df = pd.concat(processed_batches, ignore_index=True)
        
        # Clean up to free memory
        del batches, processed_batches, resume_df
        gc.collect()
        
        self.processed_resume_data = processed_df
        return processed_df

    def prepare_training_data(self):
        """
        Prepare data for model training.
        
        Returns:
            dict: Dictionary containing training data
        """
        print("Preparing training data...")
        
        if self.processed_job_data is None:
            self.process_job_data()
        
        if self.processed_resume_data is None:
            self.process_resume_data()
        
        # Check if data is available
        if self.processed_job_data is None or self.processed_job_data.empty:
            print("No processed job data available.")
            return {}
        
        if self.processed_resume_data is None or self.processed_resume_data.empty:
            print("No processed resume data available.")
            return {}
        
        # Extract skills from job descriptions
        skills = []
        for _, row in self.processed_job_data.iterrows():
            if row['job_skills']:
                skills.extend(self.extract_skills_from_job_description(row['job_skills']))
        
        # Remove duplicates and empty strings
        unique_skills = list(set([skill for skill in skills if skill]))
        
        # Prepare job data for training
        job_data = {
            'text': self.processed_job_data['processed_description'].tolist(),
            'title': self.processed_job_data['job_title'].tolist(),
            'skills': self.processed_job_data['job_skills'].tolist(),
            'location': self.processed_job_data['job_location'].tolist(),
            'company': self.processed_job_data['company_name'].tolist()
        }
        
        # Prepare resume data for training
        resume_data = {
            'text': self.processed_resume_data['processed_resume'].tolist(),
            'category': self.processed_resume_data['Category'].tolist()
        }
        
        # Combine data for training
        training_data = {
            'job_data': job_data,
            'resume_data': resume_data,
            'unique_skills': unique_skills
        }
        
        return training_data
