"""
Resume Processor Module

This module contains the ResumeProcessor class that handles resume-related
functionality such as skill extraction, resume matching, and resume generation.
"""

import os
import re
import pandas as pd
from ..nlp_processor import NLPProcessor
from ..data_processor import DataProcessor

class ResumeProcessor(NLPProcessor):
    """
    Class for processing resumes and job descriptions.
    
    This class provides functionality for extracting skills from job descriptions,
    matching resumes with job requirements, and generating tailored resumes.
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Create a singleton instance of the ResumeProcessor.
        
        Returns:
            ResumeProcessor: Singleton instance
        """
        if cls._instance is None:
            cls._instance = super(ResumeProcessor, cls).__new__(cls)
            cls._instance._resume_initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialize the ResumeProcessor with required data and models.
        """
        super().__init__()
        
        if self._resume_initialized:
            return
            
        # Initialize data processor
        self.data_processor = DataProcessor()
        
        # Initialize job data
        self.job_data = None
        self.skills_data = None
        
        # Initialize models
        self.models_loaded = False
        
        self._resume_initialized = True
    
    def _load_models_and_data(self):
        """
        Load models and data required for resume processing.
        """
        if self.models_loaded:
            return
        
        # Load data from the data processor
        self.data_processor.load_data()
        
        # Get job skills data
        if hasattr(self.data_processor, 'job_skills_df') and self.data_processor.job_skills_df is not None:
            self.skills_data = self.data_processor.job_skills_df
        
        # Get job postings data
        if hasattr(self.data_processor, 'job_postings_df') and self.data_processor.job_postings_df is not None:
            self.job_data = self.data_processor.job_postings_df
        
        # If job data is not available, create a sample data file
        if self.job_data is None or self.job_data.empty:
            # Create a default data directory
            data_dir = self.data_processor.data_dir
            job_postings_path = os.path.join(data_dir, 'job_postings.csv')
            
            # Check if the directory exists
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            
            # Create a sample job postings file if it doesn't exist
            if not os.path.exists(job_postings_path):
                sample_data = {
                    'job_id': ['1', '2', '3'],
                    'job_title': ['Software Engineer', 'Data Scientist', 'Product Manager'],
                    'company_name': ['Tech Co', 'Data Inc', 'Product Corp'],
                    'job_location': ['San Francisco, CA', 'New York, NY', 'Remote'],
                    'job_description': [
                        'We are looking for a software engineer with experience in Python and JavaScript.',
                        'We are seeking a data scientist with expertise in machine learning and statistics.',
                        'We need a product manager with experience in agile methodologies and user research.'
                    ],
                    'job_skills': [
                        'python,javascript,react,node.js',
                        'python,r,machine learning,statistics,sql',
                        'agile,scrum,user research,product development'
                    ]
                }
                pd.DataFrame(sample_data).to_csv(job_postings_path, index=False)
                
                # Load the sample data
                self.job_data = pd.read_csv(job_postings_path)
        
        # Set models loaded flag
        self.models_loaded = True
    
    def extract_skills(self, job_description):
        """
        Extract skills from a job description.
        
        Args:
            job_description (str): Job description text
            
        Returns:
            dict: Dictionary containing extracted skills and other information
        """
        # Ensure models and data are loaded
        self._load_models_and_data()
        
        # Preprocess the job description
        processed_text = self.preprocess_text(job_description)
        
        # Common technical skills to look for
        common_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'express', 
            'django', 'flask', 'spring', 'html', 'css', 'sql', 'nosql', 'mongodb', 
            'postgresql', 'mysql', 'oracle', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'ci/cd', 'git', 'agile', 'scrum', 'leadership', 'communication', 'teamwork',
            'problem solving', 'critical thinking', 'data analysis', 'machine learning',
            'ai', 'artificial intelligence', 'deep learning', 'nlp', 'natural language processing',
            'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'rust', 'go', 'scala', 'typescript',
            'devops', 'cloud', 'microservices', 'rest api', 'graphql', 'redux', 'jquery',
            'bootstrap', 'sass', 'less', 'webpack', 'babel', 'jenkins', 'travis', 'circleci',
            'terraform', 'ansible', 'chef', 'puppet', 'kubernetes', 'docker swarm',
            'data science', 'big data', 'hadoop', 'spark', 'kafka', 'elasticsearch',
            'tableau', 'power bi', 'excel', 'statistics', 'r', 'matlab', 'numpy', 'pandas',
            'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'computer vision',
            'blockchain', 'cryptocurrency', 'smart contracts', 'solidity', 'ethereum',
            'product management', 'project management', 'marketing', 'sales', 'customer service',
            'leadership', 'management', 'strategy', 'analytics', 'research', 'design',
            'ui/ux', 'user experience', 'user interface', 'graphic design', 'photoshop',
            'illustrator', 'sketch', 'figma', 'adobe xd', 'indesign', 'after effects',
            'video editing', 'content creation', 'seo', 'sem', 'digital marketing',
            'social media', 'email marketing', 'content marketing', 'growth hacking',
            'a/b testing', 'conversion optimization', 'user research', 'usability testing'
        ]
        
        # Extract skills using pattern matching
        extracted_skills = []
        for skill in common_skills:
            if skill in processed_text or skill in job_description.lower():
                extracted_skills.append(skill)
        
        # Extract years of experience
        experience_pattern = r'(\d+)(?:\+)?\s*(?:year|yr)s?(?:\s+of)?(?:\s+experience)?'
        experience_matches = re.findall(experience_pattern, job_description.lower())
        experience = max([int(x) for x in experience_matches]) if experience_matches else 0
        
        # Extract education level
        education_levels = {
            'bachelor': 'Bachelor\'s Degree',
            'master': 'Master\'s Degree',
            'phd': 'PhD',
            'doctorate': 'PhD',
            'mba': 'MBA',
            'associate': 'Associate\'s Degree',
            'high school': 'High School Diploma'
        }
        
        education = []
        for key, value in education_levels.items():
            if key in job_description.lower():
                education.append(value)
        
        # Return the extracted information
        return {
            'skills': extracted_skills,
            'experience': experience,
            'education': education,
            'processed_text': processed_text
        }
    
    def match_resume(self, resume, job_skills):
        """
        Match a resume with job skills.
        
        Args:
            resume (str): Resume text
            job_skills (list): List of job skills
            
        Returns:
            dict: Dictionary containing match score and other information
        """
        # Ensure models and data are loaded
        self._load_models_and_data()
        
        # Preprocess the resume
        processed_resume = self.preprocess_text(resume)
        
        # Calculate match score
        matched_skills = []
        for skill in job_skills:
            if skill.lower() in processed_resume:
                matched_skills.append(skill)
        
        match_score = len(matched_skills) / len(job_skills) if job_skills else 0
        
        # Return the match result
        return {
            'match_score': match_score,
            'matched_skills': matched_skills,
            'missing_skills': [skill for skill in job_skills if skill not in matched_skills],
            'processed_resume': processed_resume
        }
    
    def generate_resume(self, resume, job_description, extracted_skills):
        """
        Generate a personalized resume based on job description and extracted skills.
        
        Args:
            resume (str): Original resume text
            job_description (str): Job description text
            extracted_skills (list): List of extracted skills
            
        Returns:
            dict: Dictionary containing the generated resume and other information
        """
        # Ensure models and data are loaded
        self._load_models_and_data()
        
        # Debug prints
        print(f"Generate Resume - Resume length: {len(resume)}")
        print(f"Generate Resume - Job description length: {len(job_description)}")
        print(f"Generate Resume - Skills count: {len(extracted_skills)}")
        
        # Preprocess the resume and job description
        processed_resume = self.preprocess_text(resume)
        processed_job = self.preprocess_text(job_description)
        
        print(f"Generate Resume - Processed resume length: {len(processed_resume)}")
        print(f"Generate Resume - Processed job length: {len(processed_job)}")
        
        # Extract sections from the resume
        print("Generate Resume - Extracting resume sections...")
        sections = self._extract_resume_sections(resume)
        
        print(f"Generate Resume - Extracted sections: {list(sections.keys())}")
        for section, content in sections.items():
            print(f"Generate Resume - Section '{section}' length: {len(content)}")
            print(f"Generate Resume - Section '{section}' first 50 chars: {content[:50]}")
        
        # Personalize each section based on the job description and skills
        print("Generate Resume - Personalizing sections...")
        personalized_sections = {}
        for section, content in sections.items():
            if section == 'skills':
                # Prioritize skills that match the job description
                print(f"Generate Resume - Personalizing skills section...")
                personalized_sections[section] = self._personalize_skills(content, extracted_skills)
            elif section == 'experience':
                # Highlight relevant experience
                print(f"Generate Resume - Personalizing experience section...")
                personalized_sections[section] = self._personalize_experience(content, processed_job, extracted_skills)
            else:
                # Keep other sections as is
                personalized_sections[section] = content
        
        print(f"Generate Resume - Personalized sections: {list(personalized_sections.keys())}")
        for section, content in personalized_sections.items():
            print(f"Generate Resume - Personalized section '{section}' length: {len(content)}")
            print(f"Generate Resume - Personalized section '{section}' first 50 chars: {content[:50]}")
        
        # Combine the personalized sections into a complete resume
        print("Generate Resume - Combining sections...")
        personalized_resume = self._combine_resume_sections(personalized_sections)
        
        print(f"Generate Resume - Final resume length: {len(personalized_resume)}")
        print(f"Generate Resume - Final resume first 100 chars: {personalized_resume[:100]}")
        
        # Return the generated resume
        return {
            'original_resume': resume,
            'personalized_resume': personalized_resume,
            'highlighted_skills': extracted_skills,
            'match_score': len([skill for skill in extracted_skills if skill.lower() in processed_resume]) / len(extracted_skills) if extracted_skills else 0
        }
    
    def _extract_resume_sections(self, resume):
        """
        Extract sections from a resume.
        
        Args:
            resume (str): Resume text
            
        Returns:
            dict: Dictionary containing resume sections
        """
        # Simple section extraction based on common section headers
        sections = {}
        current_section = 'summary'
        current_content = []
        
        # Common section headers and their variations
        section_headers = {
            'summary': ['summary', 'professional summary', 'profile', 'about me', 'objective', 'career objective'],
            'experience': ['experience', 'work experience', 'employment history', 'work history', 'professional experience'],
            'education': ['education', 'educational background', 'academic background', 'qualifications'],
            'skills': ['skills', 'technical skills', 'core competencies', 'key skills', 'expertise', 'proficiencies'],
            'projects': ['projects', 'project experience', 'key projects', 'relevant projects'],
            'certifications': ['certifications', 'certificates', 'professional certifications', 'licenses']
        }
        
        # If resume is empty, create default sections
        if not resume or resume.strip() == '':
            return {
                'summary': 'No summary available',
                'experience': 'No experience available',
                'education': 'No education available',
                'skills': 'No skills available'
            }
        
        # Split resume into lines
        lines = resume.split('\n')
        
        # Process each line
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            is_header = False
            for section, headers in section_headers.items():
                # Check if line matches any of the section headers
                if any(header.lower() in line.lower() for header in headers):
                    # Save the previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                        current_content = []
                    
                    # Start a new section
                    current_section = section
                    is_header = True
                    break
            
            # If not a header, add to current content
            if not is_header:
                current_content.append(line)
        
        # Save the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        # If no sections were found, create a simple structure from the entire resume
        if not sections:
            # Try to make a best guess at sections
            text_blocks = resume.split('\n\n')
            
            if len(text_blocks) >= 4:
                # Assume the first block is summary, then experience, education, and skills
                sections = {
                    'summary': text_blocks[0],
                    'experience': text_blocks[1],
                    'education': text_blocks[2],
                    'skills': text_blocks[3]
                }
            else:
                # Just put everything in summary
                sections = {
                    'summary': resume,
                    'experience': 'No experience information found',
                    'education': 'No education information found',
                    'skills': 'No skills information found'
                }
        
        # Ensure all required sections exist
        for section in ['summary', 'experience', 'education', 'skills']:
            if section not in sections:
                sections[section] = f'No {section} available'
        
        return sections
    
    def _personalize_skills(self, skills_content, job_skills):
        """
        Personalize the skills section based on job skills.
        
        Args:
            skills_content (str): Original skills content
            job_skills (list): List of job skills
            
        Returns:
            str: Personalized skills content
        """
        # Handle case where skills_content is empty or not a string
        if not skills_content or not isinstance(skills_content, str):
            # If we have job skills, use them as the skills content
            if job_skills and len(job_skills) > 0:
                return ', '.join(job_skills)
            return "No skills available"
            
        # Check if skills_content is already in a comma-separated format
        if ',' in skills_content:
            # Extract individual skills from the skills content
            resume_skills = [skill.strip() for skill in skills_content.split(',')]
        else:
            # Try to extract skills by splitting on newlines and other delimiters
            resume_skills = []
            for line in skills_content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Check if line contains multiple skills
                if ',' in line:
                    resume_skills.extend([s.strip() for s in line.split(',')])
                elif ';' in line:
                    resume_skills.extend([s.strip() for s in line.split(';')])
                elif '•' in line:
                    resume_skills.extend([s.strip() for s in line.split('•') if s.strip()])
                elif '-' in line:
                    resume_skills.extend([s.strip() for s in line.split('-') if s.strip()])
                else:
                    # Assume the whole line is a skill
                    resume_skills.append(line)
        
        # Remove empty skills
        resume_skills = [skill for skill in resume_skills if skill]
        
        # If no skills were extracted, use the original content
        if not resume_skills:
            # If we have job skills, use them as the skills content
            if job_skills and len(job_skills) > 0:
                return ', '.join(job_skills)
            return skills_content
        
        # Prioritize skills that match the job description
        matched_skills = []
        for skill in resume_skills:
            for job_skill in job_skills:
                if job_skill.lower() in skill.lower() or skill.lower() in job_skill.lower():
                    matched_skills.append(skill)
                    break
        
        # Get skills that didn't match
        other_skills = [skill for skill in resume_skills if skill not in matched_skills]
        
        # Combine the skills with matched skills first
        personalized_skills = matched_skills + other_skills
        
        # Return as a comma-separated list
        return ', '.join(personalized_skills)
    
    def _personalize_experience(self, experience_content, processed_job, job_skills):
        """
        Personalize the experience section based on job description and skills.
        
        Args:
            experience_content (str): Original experience content
            processed_job (str): Processed job description
            job_skills (list): List of job skills
            
        Returns:
            str: Personalized experience content
        """
        # Handle case where experience_content is empty or not a string
        if not experience_content or not isinstance(experience_content, str):
            return "No experience available"
            
        # Split experience into paragraphs (likely different jobs)
        experience_paragraphs = experience_content.split('\n\n')
        
        # If there's only one paragraph, try to split by newlines
        if len(experience_paragraphs) <= 1:
            experience_paragraphs = experience_content.split('\n')
            
        # If still only one paragraph, just return the original content
        if len(experience_paragraphs) <= 1:
            return experience_content
            
        # Calculate relevance score for each paragraph
        paragraph_scores = []
        for paragraph in experience_paragraphs:
            # Skip empty paragraphs
            if not paragraph.strip():
                paragraph_scores.append(0)
                continue
                
            # Calculate score based on job skills
            skill_score = 0
            for skill in job_skills:
                if skill.lower() in paragraph.lower():
                    skill_score += 1
                    
            # Calculate score based on job description keywords
            job_keywords = processed_job.split()
            keyword_score = 0
            for keyword in job_keywords:
                if len(keyword) > 3 and keyword.lower() in paragraph.lower():
                    keyword_score += 0.5
                    
            # Combine scores
            total_score = skill_score + (keyword_score / len(job_keywords) if job_keywords else 0)
            paragraph_scores.append(total_score)
            
        # Sort paragraphs by relevance score (highest first)
        sorted_experience = [p for _, p in sorted(zip(paragraph_scores, experience_paragraphs), key=lambda x: x[0], reverse=True)]
        
        # Highlight relevant skills in the experience
        highlighted_experience = []
        for paragraph in sorted_experience:
            # Add paragraph with highlighted skills
            highlighted_paragraph = paragraph
            for skill in job_skills:
                # Simple highlighting by adding asterisks around the skill
                if skill.lower() in highlighted_paragraph.lower():
                    # Find all occurrences of the skill (case-insensitive)
                    pattern = re.compile(re.escape(skill), re.IGNORECASE)
                    highlighted_paragraph = pattern.sub(f"*{skill}*", highlighted_paragraph)
                    
            highlighted_experience.append(highlighted_paragraph)
            
        # Join the paragraphs back together
        return '\n\n'.join(highlighted_experience)
    
    def _combine_resume_sections(self, sections):
        """
        Combine resume sections into a complete resume.
        
        Args:
            sections (dict): Dictionary containing resume sections
            
        Returns:
            str: Combined resume text
        """
        # Define the order of sections
        section_order = ['summary', 'experience', 'education', 'skills', 'projects', 'certifications']
        
        # Define section titles
        section_titles = {
            'summary': 'PROFESSIONAL SUMMARY',
            'experience': 'WORK EXPERIENCE',
            'education': 'EDUCATION',
            'skills': 'SKILLS',
            'projects': 'PROJECTS',
            'certifications': 'CERTIFICATIONS'
        }
        
        # Combine the sections in the defined order
        combined = []
        for section in section_order:
            if section in sections:
                # Add section title with proper formatting
                combined.append(f"{section_titles[section]}")
                combined.append("-" * len(section_titles[section]))
                
                # Add section content with proper formatting
                content = sections[section].strip()
                
                # Add a blank line after the section title
                combined.append("")
                
                # Add the content
                combined.append(content)
                
                # Add a blank line after the section
                combined.append("")
        
        # Join the sections with proper spacing
        return '\n'.join(combined)
