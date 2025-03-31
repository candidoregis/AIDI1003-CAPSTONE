"""
NLP Processor Module

This module contains the base NLPProcessor class that provides common NLP functionality
for both voice query processing and resume generation.
"""

import os
import re
import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class NLPProcessor:
    """
    Base class for NLP processing tasks.
    
    This class provides common functionality for text preprocessing, 
    vectorization, and similarity calculations used by both the voice 
    query processor and resume processor.
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Create a singleton instance of the NLPProcessor.
        
        Returns:
            NLPProcessor: Singleton instance
        """
        if cls._instance is None:
            cls._instance = super(NLPProcessor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialize the NLPProcessor with required NLP tools.
        """
        if self._initialized:
            return
            
        # Initialize NLP tools
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Initialize vectorizer
        self.vectorizer = None
        
        # Initialize data
        self.data_loaded = False
        
        self._initialized = True
    
    def _load_models_and_data(self):
        """
        Load models and data required for NLP processing.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _load_models_and_data")
    
    def preprocess_text(self, text):
        """
        Preprocess text by removing special characters, converting to lowercase,
        tokenizing, removing stopwords, and lemmatizing.
        
        Args:
            text (str): Text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        
        # Join tokens back into a string
        return ' '.join(tokens)
    
    def vectorize_text(self, text, fit=False):
        """
        Convert text to a TF-IDF vector.
        
        Args:
            text (str or list): Text or list of texts to vectorize
            fit (bool): Whether to fit the vectorizer on the text
            
        Returns:
            numpy.ndarray: TF-IDF vector(s)
        """
        if not self.vectorizer and not fit:
            self.vectorizer = TfidfVectorizer(max_features=5000)
        
        if isinstance(text, str):
            text = [text]
            
        if fit:
            return self.vectorizer.fit_transform(text)
        else:
            return self.vectorizer.transform(text)
    
    def calculate_similarity(self, vector1, vector2):
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vector1 (numpy.ndarray): First vector
            vector2 (numpy.ndarray): Second vector
            
        Returns:
            float: Cosine similarity score
        """
        return cosine_similarity(vector1, vector2)[0][0]
    
    def batch_process_text(self, texts, batch_size=1000, preprocess=True):
        """
        Process a large list of texts in batches to avoid memory issues.
        
        Args:
            texts (list): List of texts to process
            batch_size (int): Size of each batch
            preprocess (bool): Whether to preprocess the texts
            
        Returns:
            list: List of processed texts
        """
        processed_texts = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            if preprocess:
                batch = [self.preprocess_text(text) for text in batch]
                
            processed_texts.extend(batch)
            
        return processed_texts
    
    def extract_keywords(self, text, top_n=10):
        """
        Extract the most important keywords from a text.
        
        Args:
            text (str): Text to extract keywords from
            top_n (int): Number of keywords to extract
            
        Returns:
            list: List of top keywords
        """
        try:
            print(f"NLPProcessor: Extracting keywords from text: {text}")
            
            # Check if text is valid
            if not text or not isinstance(text, str):
                print(f"NLPProcessor: Invalid text input: {text}")
                return []
            
            # Preprocess the text
            print(f"NLPProcessor: Preprocessing text")
            processed_text = self.preprocess_text(text)
            print(f"NLPProcessor: Processed text: {processed_text}")
            
            # Check if processed text is empty
            if not processed_text:
                print(f"NLPProcessor: Processed text is empty")
                return []
            
            # Tokenize and count word frequencies
            tokens = processed_text.split()
            print(f"NLPProcessor: Tokens: {tokens}")
            
            word_freq = {}
            
            for token in tokens:
                if token in word_freq:
                    word_freq[token] += 1
                else:
                    word_freq[token] = 1
            
            print(f"NLPProcessor: Word frequencies: {word_freq}")
            
            # Sort words by frequency
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            print(f"NLPProcessor: Sorted words: {sorted_words}")
            
            # Return top N keywords
            keywords = [word for word, freq in sorted_words[:top_n]]
            print(f"NLPProcessor: Extracted keywords: {keywords}")
            
            return keywords
        except Exception as e:
            print(f"NLPProcessor: Error extracting keywords: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return empty list instead of raising an exception
            return []
