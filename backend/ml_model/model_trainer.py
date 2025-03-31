import os
import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from gensim.models import Word2Vec
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout

class ModelTrainer:
    def __init__(self, model_dir):
        """
        Initialize the ModelTrainer with the directory to save trained models.
        
        Args:
            model_dir (str): Path to the directory to save trained models
        """
        self.model_dir = model_dir
        self.skill_extractor = None
        self.resume_classifier = None
        self.word2vec_model = None
        self.tokenizer = None
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
    
    def train_skill_extractor(self, job_data):
        """
        Train a model to extract skills from job descriptions.
        
        Args:
            job_data (dict): Dictionary containing job data
        """
        print("Training skill extractor model...")
        
        # Create a TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            min_df=5,
            max_df=0.8,
            ngram_range=(1, 2)
        )
        
        # Prepare data
        X = job_data['text']
        
        # Fit the vectorizer
        tfidf_vectorizer.fit(X)
        
        # Save the vectorizer
        self.skill_extractor = tfidf_vectorizer
        joblib.dump(tfidf_vectorizer, os.path.join(self.model_dir, 'skill_extractor.joblib'))
        
        print("Skill extractor model trained and saved.")
        
        return tfidf_vectorizer
    
    def train_resume_classifier(self, resume_data):
        """
        Train a model to classify resumes into job categories.
        
        Args:
            resume_data (dict): Dictionary containing resume data
        """
        print("Training resume classifier model...")
        
        # Prepare data
        X = resume_data['text']
        y = resume_data['category']
        
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create a pipeline with TF-IDF vectorizer and Random Forest classifier
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, min_df=5, max_df=0.8)),
            ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        # Train the model
        pipeline.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = pipeline.predict(X_test)
        print(classification_report(y_test, y_pred))
        
        # Save the model
        self.resume_classifier = pipeline
        joblib.dump(pipeline, os.path.join(self.model_dir, 'resume_classifier.joblib'))
        
        print("Resume classifier model trained and saved.")
        
        return pipeline
    
    def train_word2vec_model(self, job_data, resume_data):
        """
        Train a Word2Vec model for word embeddings.
        
        Args:
            job_data (dict): Dictionary containing job data
            resume_data (dict): Dictionary containing resume data
        """
        print("Training Word2Vec model...")
        
        # Prepare data
        texts = list(job_data['text']) + list(resume_data['text'])
        
        # Tokenize texts
        tokenized_texts = [text.split() for text in texts if isinstance(text, str)]
        
        # Train Word2Vec model
        word2vec_model = Word2Vec(
            sentences=tokenized_texts,
            vector_size=100,
            window=5,
            min_count=5,
            workers=4
        )
        
        # Save the model
        self.word2vec_model = word2vec_model
        word2vec_model.save(os.path.join(self.model_dir, 'word2vec.model'))
        
        print("Word2Vec model trained and saved.")
        
        return word2vec_model
    
    def train_deep_learning_model(self, job_data, resume_data):
        """
        Train a deep learning model for resume-job matching.
        
        Args:
            job_data (dict): Dictionary containing job data
            resume_data (dict): Dictionary containing resume data
        """
        print("Training deep learning model...")
        
        # Prepare data
        job_texts = list(job_data['text'])
        resume_texts = list(resume_data['text'])
        
        # Create a tokenizer
        tokenizer = Tokenizer(num_words=10000)
        tokenizer.fit_on_texts(job_texts + resume_texts)
        
        # Save the tokenizer
        self.tokenizer = tokenizer
        joblib.dump(tokenizer, os.path.join(self.model_dir, 'tokenizer.joblib'))
        
        # Convert texts to sequences
        job_sequences = tokenizer.texts_to_sequences(job_texts)
        resume_sequences = tokenizer.texts_to_sequences(resume_texts)
        
        # Pad sequences
        max_length = 200
        job_padded = pad_sequences(job_sequences, maxlen=max_length, padding='post')
        resume_padded = pad_sequences(resume_sequences, maxlen=max_length, padding='post')
        
        # Create a simple model for demonstration
        # In a real scenario, you would need labeled data for resume-job matching
        model = Sequential([
            Embedding(input_dim=10000, output_dim=128, input_length=max_length),
            LSTM(64, return_sequences=True),
            LSTM(32),
            Dense(64, activation='relu'),
            Dropout(0.5),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
        # Save the model architecture
        model_json = model.to_json()
        with open(os.path.join(self.model_dir, 'dl_model.json'), 'w') as json_file:
            json_file.write(model_json)
        
        print("Deep learning model architecture saved.")
        
        return model, tokenizer
    
    def train_all_models(self, training_data):
        """
        Train all models using the provided training data.
        
        Args:
            training_data (dict): Dictionary containing training data
        """
        job_data = training_data['job_data']
        resume_data = training_data['resume_data']
        
        # Train skill extractor
        self.train_skill_extractor(job_data)
        
        # Train resume classifier
        self.train_resume_classifier(resume_data)
        
        # Train Word2Vec model
        self.train_word2vec_model(job_data, resume_data)
        
        # Train deep learning model
        self.train_deep_learning_model(job_data, resume_data)
        
        print("All models trained and saved.")
        
    def load_models(self):
        """
        Load all trained models.
        
        Returns:
            dict: Dictionary containing loaded models
        """
        print("Loading trained models...")
        
        # Load skill extractor
        skill_extractor_path = os.path.join(self.model_dir, 'skill_extractor.joblib')
        if os.path.exists(skill_extractor_path):
            self.skill_extractor = joblib.load(skill_extractor_path)
        
        # Load resume classifier
        resume_classifier_path = os.path.join(self.model_dir, 'resume_classifier.joblib')
        if os.path.exists(resume_classifier_path):
            self.resume_classifier = joblib.load(resume_classifier_path)
        
        # Load Word2Vec model
        word2vec_path = os.path.join(self.model_dir, 'word2vec.model')
        if os.path.exists(word2vec_path):
            self.word2vec_model = Word2Vec.load(word2vec_path)
        
        # Load tokenizer
        tokenizer_path = os.path.join(self.model_dir, 'tokenizer.joblib')
        if os.path.exists(tokenizer_path):
            self.tokenizer = joblib.load(tokenizer_path)
        
        return {
            'skill_extractor': self.skill_extractor,
            'resume_classifier': self.resume_classifier,
            'word2vec_model': self.word2vec_model,
            'tokenizer': self.tokenizer
        }
