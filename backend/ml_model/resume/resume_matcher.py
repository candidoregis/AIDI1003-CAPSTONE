import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import joblib
import os

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class ResumeMatcher:
    def __init__(self, model_dir):
        """
        Initialize the ResumeMatcher with the directory containing trained models.
        
        Args:
            model_dir (str): Path to the directory containing trained models
        """
        self.model_dir = model_dir
        self.skill_extractor = None
        self.resume_classifier = None
        self.word2vec_model = None
        self.tokenizer = None
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Load models
        self.load_models()
    
    def load_models(self):
        """
        Load all trained models.
        """
        print("Loading trained models...")
        
        # Load skill extractor
        skill_extractor_path = os.path.join(self.model_dir, 'skill_extractor.joblib')
        if os.path.exists(skill_extractor_path):
            self.skill_extractor = joblib.load(skill_extractor_path)
        else:
            print(f"Warning: Skill extractor model not found at {skill_extractor_path}")
        
        # Load resume classifier
        resume_classifier_path = os.path.join(self.model_dir, 'resume_classifier.joblib')
        if os.path.exists(resume_classifier_path):
            self.resume_classifier = joblib.load(resume_classifier_path)
        else:
            print(f"Warning: Resume classifier model not found at {resume_classifier_path}")
        
        # Load Word2Vec model
        try:
            from gensim.models import Word2Vec
            word2vec_path = os.path.join(self.model_dir, 'word2vec.model')
            if os.path.exists(word2vec_path):
                self.word2vec_model = Word2Vec.load(word2vec_path)
            else:
                print(f"Warning: Word2Vec model not found at {word2vec_path}")
        except ImportError:
            print("Warning: gensim not installed, Word2Vec model not loaded")
        
        # Load tokenizer
        tokenizer_path = os.path.join(self.model_dir, 'tokenizer.joblib')
        if os.path.exists(tokenizer_path):
            self.tokenizer = joblib.load(tokenizer_path)
        else:
            print(f"Warning: Tokenizer not found at {tokenizer_path}")
    
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
    
    def extract_skills(self, job_description):
        """
        Extract skills from a job description using the trained skill extractor.
        
        Args:
            job_description (str): Job description text
            
        Returns:
            list: List of extracted skills with relevance scores
        """
        if self.skill_extractor is None:
            print("Skill extractor model not loaded. Using fallback method.")
            return self.extract_skills_fallback(job_description)
        
        # Preprocess the job description
        processed_text = self.preprocess_text(job_description)
        
        # Transform the processed text using the TF-IDF vectorizer
        tfidf_matrix = self.skill_extractor.transform([processed_text])
        
        # Get feature names (terms) from the vectorizer
        feature_names = self.skill_extractor.get_feature_names_out()
        
        # Get the TF-IDF scores for each term
        tfidf_scores = tfidf_matrix.toarray()[0]
        
        # Create a list of (term, score) tuples and sort by score in descending order
        term_scores = [(feature_names[i], tfidf_scores[i]) for i in range(len(feature_names)) if tfidf_scores[i] > 0]
        term_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Extract the top skills (terms with highest TF-IDF scores)
        top_skills = term_scores[:30]  # Adjust the number as needed
        
        # Format the skills with relevance scores
        extracted_skills = [
            {
                'skill': skill,
                'relevance': float(score),
                'category': self.categorize_skill(skill)
            }
            for skill, score in top_skills
        ]
        
        return extracted_skills
    
    def extract_skills_fallback(self, job_description):
        """
        Fallback method to extract skills from a job description when the model is not available.
        
        Args:
            job_description (str): Job description text
            
        Returns:
            list: List of extracted skills
        """
        # Preprocess the job description
        processed_text = self.preprocess_text(job_description)
        
        # Split into tokens
        tokens = processed_text.split()
        
        # Count token frequencies
        token_counts = {}
        for token in tokens:
            if len(token) > 3:  # Filter out very short tokens
                token_counts[token] = token_counts.get(token, 0) + 1
        
        # Sort tokens by frequency
        sorted_tokens = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Extract the top tokens as skills
        top_skills = sorted_tokens[:30]  # Adjust the number as needed
        
        # Format the skills with relevance scores
        extracted_skills = [
            {
                'skill': skill,
                'relevance': float(count) / max(1, max([c for _, c in sorted_tokens])),
                'category': self.categorize_skill(skill)
            }
            for skill, count in top_skills
        ]
        
        return extracted_skills
    
    def categorize_skill(self, skill):
        """
        Categorize a skill into a skill category.
        
        Args:
            skill (str): Skill to categorize
            
        Returns:
            str: Skill category
        """
        # Define skill categories and keywords
        categories = {
            'Technical': ['programming', 'software', 'database', 'algorithm', 'code', 'develop', 'engineer', 'system', 'network', 'cloud', 'data', 'analysis'],
            'Soft Skills': ['communication', 'teamwork', 'leadership', 'problem', 'solving', 'critical', 'thinking', 'time', 'management', 'adaptability', 'creativity'],
            'Business': ['management', 'strategy', 'marketing', 'sales', 'finance', 'accounting', 'operations', 'project', 'planning', 'analysis', 'business'],
            'Other': []
        }
        
        # Check which category the skill belongs to
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in skill:
                    return category
        
        return 'Other'
    
    def match_resume(self, resume, job_skills):
        """
        Calculate the match score between a resume and job skills.
        
        Args:
            resume (str): Resume text
            job_skills (list): List of job skills
            
        Returns:
            dict: Match score and details
        """
        # Preprocess the resume
        processed_resume = self.preprocess_text(resume)
        
        # Extract resume tokens
        resume_tokens = set(processed_resume.split())
        
        # Calculate match score based on skill presence
        matches = []
        missing = []
        
        for skill_obj in job_skills:
            skill = skill_obj['skill']
            skill_tokens = set(self.preprocess_text(skill).split())
            
            # Check if any of the skill tokens are in the resume
            if any(token in resume_tokens for token in skill_tokens):
                matches.append(skill_obj)
            else:
                missing.append(skill_obj)
        
        # Calculate match percentage
        match_percentage = len(matches) / max(1, len(job_skills)) * 100
        
        return {
            'matchScore': round(match_percentage, 2),
            'matches': matches,
            'missing': missing
        }
    
    def generate_resume(self, resume, job_description, extracted_skills):
        """
        Generate a personalized resume based on the job description and extracted skills.
        
        Args:
            resume (str): Original resume text
            job_description (str): Job description text
            extracted_skills (list): List of extracted skills
            
        Returns:
            dict: Generated resume with sections
        """
        # Preprocess texts
        processed_resume = self.preprocess_text(resume)
        processed_job = self.preprocess_text(job_description)
        
        # Extract resume sections (simplified)
        sections = self.extract_resume_sections(resume)
        
        # Identify missing skills
        match_result = self.match_resume(resume, extracted_skills)
        missing_skills = match_result['missing']
        
        # Generate suggestions for improving the resume
        suggestions = self.generate_suggestions(sections, missing_skills)
        
        # Create a personalized resume
        personalized_resume = {
            'summary': self.generate_summary(sections.get('summary', ''), job_description, extracted_skills),
            'skills': self.prioritize_skills(sections.get('skills', ''), extracted_skills),
            'experience': self.enhance_experience(sections.get('experience', ''), extracted_skills),
            'education': sections.get('education', ''),
            'suggestions': suggestions,
            'matchScore': match_result['matchScore']
        }
        
        return personalized_resume
    
    def extract_resume_sections(self, resume):
        """
        Extract sections from a resume.
        
        Args:
            resume (str): Resume text
            
        Returns:
            dict: Dictionary of resume sections
        """
        # Simple section extraction based on common section headers
        sections = {}
        
        # Define common section headers
        section_patterns = {
            'summary': r'(?i)(summary|profile|objective|about me)',
            'skills': r'(?i)(skills|technical skills|core competencies|expertise)',
            'experience': r'(?i)(experience|work experience|employment|work history)',
            'education': r'(?i)(education|academic background|qualifications|training)'
        }
        
        # Extract content for each section
        for section_name, pattern in section_patterns.items():
            matches = re.finditer(pattern, resume)
            for match in matches:
                start_pos = match.end()
                
                # Find the next section header
                next_section_start = len(resume)
                for next_pattern in section_patterns.values():
                    next_matches = re.finditer(next_pattern, resume[start_pos:])
                    for next_match in next_matches:
                        next_section_pos = start_pos + next_match.start()
                        if next_section_pos < next_section_start:
                            next_section_start = next_section_pos
                
                # Extract the section content
                section_content = resume[start_pos:next_section_start].strip()
                sections[section_name] = section_content
                break  # Only use the first match for each section
        
        return sections
    
    def generate_summary(self, original_summary, job_description, extracted_skills):
        """
        Generate an enhanced summary based on the job description and extracted skills.
        
        Args:
            original_summary (str): Original summary section
            job_description (str): Job description text
            extracted_skills (list): List of extracted skills
            
        Returns:
            str: Enhanced summary
        """
        # If no original summary, create a basic one
        if not original_summary:
            return "Experienced professional with expertise in " + ", ".join([skill['skill'] for skill in extracted_skills[:5]])
        
        # Get top skills from the job
        top_skills = [skill['skill'] for skill in extracted_skills[:5]]
        
        # Enhance the original summary by emphasizing relevant skills
        enhanced_summary = original_summary
        
        # Add a sentence highlighting relevant skills if not already mentioned
        skill_sentence = f"Proficient in {', '.join(top_skills[:-1])} and {top_skills[-1]}."
        if skill_sentence not in enhanced_summary:
            enhanced_summary += " " + skill_sentence
        
        return enhanced_summary
    
    def prioritize_skills(self, original_skills, job_skills):
        """
        Prioritize skills based on the job requirements.
        
        Args:
            original_skills (str): Original skills section
            job_skills (list): List of job skills
            
        Returns:
            str: Prioritized skills section
        """
        # If no original skills, create a skills section from job skills
        if not original_skills:
            return "Key Skills:\n- " + "\n- ".join([skill['skill'] for skill in job_skills[:10]])
        
        # Extract skills from the original skills section
        skills_list = re.findall(r'[\w\s]+', original_skills)
        skills_list = [skill.strip() for skill in skills_list if skill.strip()]
        
        # Prioritize skills based on job requirements
        prioritized_skills = []
        remaining_skills = []
        
        for skill in skills_list:
            if any(job_skill['skill'].lower() in skill.lower() for job_skill in job_skills):
                prioritized_skills.append(skill)
            else:
                remaining_skills.append(skill)
        
        # Combine prioritized and remaining skills
        combined_skills = prioritized_skills + remaining_skills
        
        # Format the skills section
        formatted_skills = "Key Skills:\n- " + "\n- ".join(combined_skills)
        
        return formatted_skills
    
    def enhance_experience(self, original_experience, job_skills):
        """
        Enhance the experience section based on job skills.
        
        Args:
            original_experience (str): Original experience section
            job_skills (list): List of job skills
            
        Returns:
            str: Enhanced experience section
        """
        # If no original experience, return empty string
        if not original_experience:
            return ""
        
        # Get skill keywords
        skill_keywords = [skill['skill'].lower() for skill in job_skills]
        
        # Split experience into paragraphs (assuming each paragraph is a job)
        paragraphs = original_experience.split('\n\n')
        enhanced_paragraphs = []
        
        for paragraph in paragraphs:
            # Check if any skill keywords are in the paragraph
            has_skills = any(keyword in paragraph.lower() for keyword in skill_keywords)
            
            # If skills are already mentioned, keep the paragraph as is
            if has_skills:
                enhanced_paragraphs.append(paragraph)
                continue
            
            # Find relevant skills for this experience
            relevant_skills = []
            for skill in job_skills:
                # Simple heuristic: if any word in the skill is in the paragraph
                skill_words = skill['skill'].lower().split()
                if any(word in paragraph.lower() for word in skill_words):
                    relevant_skills.append(skill['skill'])
                    if len(relevant_skills) >= 3:
                        break
            
            # If relevant skills found, enhance the paragraph
            if relevant_skills:
                # Add a bullet point highlighting the skills
                skill_bullet = f"• Utilized expertise in {', '.join(relevant_skills)}"
                
                # Add the bullet point to the paragraph
                if '•' in paragraph or '-' in paragraph:
                    # If the paragraph already has bullet points, add another one
                    paragraph += f"\n{skill_bullet}"
                else:
                    # Otherwise, add a new line with the bullet point
                    paragraph += f"\n\n{skill_bullet}"
            
            enhanced_paragraphs.append(paragraph)
        
        # Combine the enhanced paragraphs
        enhanced_experience = '\n\n'.join(enhanced_paragraphs)
        
        return enhanced_experience
    
    def generate_suggestions(self, sections, missing_skills):
        """
        Generate suggestions for improving the resume based on missing skills.
        
        Args:
            sections (dict): Dictionary of resume sections
            missing_skills (list): List of missing skills
            
        Returns:
            list: List of suggestions
        """
        suggestions = []
        
        # Suggest adding missing skills
        if missing_skills:
            top_missing = missing_skills[:5]
            suggestions.append({
                'type': 'missing_skills',
                'message': f"Add these key skills to your resume: {', '.join([skill['skill'] for skill in top_missing])}",
                'skills': top_missing
            })
        
        # Suggest improving the summary
        if 'summary' not in sections or len(sections.get('summary', '')) < 100:
            suggestions.append({
                'type': 'improve_summary',
                'message': "Enhance your professional summary to highlight your relevant experience and key skills"
            })
        
        # Suggest quantifying achievements
        if 'experience' in sections and not re.search(r'\d+%|\d+\s+years', sections['experience']):
            suggestions.append({
                'type': 'quantify_achievements',
                'message': "Quantify your achievements with metrics and numbers (e.g., 'increased sales by 20%')"
            })
        
        return suggestions
