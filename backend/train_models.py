import os
import sys
import time
import argparse
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Add the parent directory to the path so we can import the ml_model package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_model.data_processor import DataProcessor
from ml_model.model_trainer import ModelTrainer
from ml_model.voice_query_processor import VoiceQueryProcessor

def train_models(data_dir, model_dir, sample_size=None):
    """
    Train models using the dataset.
    
    Args:
        data_dir (str): Path to the directory containing the dataset files
        model_dir (str): Path to the directory to save trained models
        sample_size (int, optional): Number of samples to use for training (for testing purposes)
    """
    print(f"Training models using data from {data_dir}")
    print(f"Models will be saved to {model_dir}")
    
    # Create model directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    start_time = time.time()
    
    # Process data
    data_processor = DataProcessor(data_dir)
    
    print("Loading datasets...")
    data = data_processor.load_data()
    
    # If sample_size is provided, use only a subset of the data
    if sample_size:
        print(f"Using sample size of {sample_size} for training")
        for key in data:
            if len(data[key]) > sample_size:
                data[key] = data[key].sample(sample_size, random_state=42)
        
        # Update the DataProcessor's dataframes
        data_processor.job_skills_df = data['job_skills']
        data_processor.job_summary_df = data['job_summary']
        data_processor.job_postings_df = data['job_postings']
        data_processor.resume_df = data['resume']
    
    print("Processing job data...")
    job_data = data_processor.process_job_data()
    
    print("Processing resume data...")
    resume_data = data_processor.process_resume_data()
    
    print("Preparing training data...")
    training_data = data_processor.prepare_training_data()
    
    print("Training models...")
    model_trainer = ModelTrainer(model_dir)
    model_trainer.train_all_models(training_data)
    
    # Train voice query processing models
    print("Training voice query processing models...")
    
    # Load job postings data
    job_postings_path = os.path.join(data_dir, 'linkedin_job_postings.csv')
    if os.path.exists(job_postings_path):
        job_postings_df = pd.read_csv(job_postings_path)
        
        # Select relevant columns and clean data
        job_data = job_postings_df[['job_title', 'company_name', 'job_description', 'job_location', 'job_work_from_home', 'job_skills']].copy()
        job_data.fillna('', inplace=True)
        
        # Create a combined text field for TF-IDF vectorization
        job_data['combined_text'] = (
            job_data['job_title'] + ' ' + 
            job_data['company_name'] + ' ' + 
            job_data['job_description'] + ' ' + 
            job_data['job_location'] + ' ' + 
            job_data['job_skills']
        )
        
        # Preprocess text
        voice_processor = VoiceQueryProcessor(model_dir, data_dir)
        job_data['processed_text'] = job_data['combined_text'].apply(voice_processor.preprocess_text)
        
        # Create and train TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        
        tfidf_vectorizer.fit(job_data['processed_text'])
        
        # Save the vectorizer
        joblib.dump(tfidf_vectorizer, os.path.join(model_dir, 'tfidf_vectorizer.joblib'))
        print("TF-IDF vectorizer trained and saved.")
    else:
        print(f"Warning: Job postings data not found at {job_postings_path}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"Models trained and saved to {model_dir}")
    print(f"Training completed in {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train models for AI Resume Builder')
    parser.add_argument('--data-dir', type=str, default='../src/dataset',
                        help='Path to the directory containing the dataset files')
    parser.add_argument('--model-dir', type=str, default='./models',
                        help='Path to the directory to save trained models')
    parser.add_argument('--sample-size', type=int, default=None,
                        help='Number of samples to use for training (for testing purposes)')
    
    args = parser.parse_args()
    
    # Convert relative paths to absolute paths
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), args.data_dir))
    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), args.model_dir))
    
    train_models(data_dir, model_dir, args.sample_size)
