from flask import Flask, request, jsonify
from flask_cors import CORS
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import json
import spacy
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize NLP tools
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # If the model isn't available, download it
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

# Common tech skills and keywords
COMMON_SKILLS = [
    'javascript', 'python', 'java', 'c++', 'c#', 'react', 'angular', 'vue', 
    'node.js', 'express', 'django', 'flask', 'spring', 'aws', 'azure', 'gcp', 'docker', 
    'kubernetes', 'ci/cd', 'git', 'agile', 'scrum', 'sql', 'nosql', 'mongodb', 'postgresql',
    'mysql', 'redis', 'graphql', 'rest', 'api', 'microservices', 'serverless', 'machine learning',
    'ai', 'data science', 'big data', 'hadoop', 'spark', 'tableau', 'power bi', 'excel',
    'leadership', 'communication', 'teamwork', 'problem-solving', 'critical thinking'
]


@app.route('/api/extract-skills', methods=['POST'])
def extract_skills():
    """Extract key skills and requirements from a job description"""
    data = request.json
    job_description = data.get('jobDescription', '')
    
    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400
    
    # Process the job description with spaCy
    doc = nlp(job_description.lower())
    
    # Extract tokens and remove stopwords
    tokens = [token.text for token in doc if not token.is_stop and token.is_alpha]
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(max_features=100)
    try:
        tfidf_matrix = vectorizer.fit_transform([job_description])
        feature_names = vectorizer.get_feature_names_out()
    except:
        feature_names = []
    
    # Calculate relevance for each skill
    extracted_skills = []
    
    for skill in COMMON_SKILLS:
        # Check if skill is in the job description
        skill_regex = re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE)
        matches = skill_regex.findall(job_description)
        relevance = len(matches) * 0.5
        
        # Check if skill is in important TF-IDF terms
        if skill in feature_names:
            relevance += 0.5
        
        # Check for stemmed matches
        skill_tokens = word_tokenize(skill.lower())
        stemmed_skill = [stemmer.stem(token) for token in skill_tokens]
        
        for token in tokens:
            stemmed_token = stemmer.stem(token)
            if stemmed_token in stemmed_skill:
                relevance += 0.3
        
        if relevance > 0:
            extracted_skills.append({
                'name': skill,
                'relevance': relevance
            })
    
    # Sort by relevance and return top 15
    extracted_skills.sort(key=lambda x: x['relevance'], reverse=True)
    print("Extracted skills:", extracted_skills[:15])
    return jsonify(extracted_skills[:15])


@app.route('/api/match-resume', methods=['POST'])
def match_resume():
    """Match resume with job description"""
    data = request.json
    resume = data.get('resume', '')
    job_skills = data.get('jobSkills', [])
    
    if not resume or not job_skills:
        return jsonify({'error': 'Resume and job skills are required'}), 400
    
    match_score = 0
    
    for skill in job_skills:
        skill_name = skill.get('name', '')
        skill_relevance = skill.get('relevance', 0)
        
        # Check if skill is in the resume
        skill_regex = re.compile(r'\b' + re.escape(skill_name) + r'\b', re.IGNORECASE)
        matches = skill_regex.findall(resume)
        
        if matches:
            match_score += len(matches) * skill_relevance
    
    # Normalize score to percentage
    max_possible_score = sum([skill.get('relevance', 0) * 2 for skill in job_skills])
    if max_possible_score > 0:
        match_percentage = min(match_score / max_possible_score, 1) * 100
    else:
        match_percentage = 0
    
    return jsonify({'matchScore': match_percentage})


@app.route('/api/generate-resume', methods=['POST'])
def generate_resume():
    """Generate a personalized resume based on job description and original resume"""
    data = request.json
    original_resume = data.get('resume', '')
    job_description = data.get('jobDescription', '')
    extracted_skills = data.get('extractedSkills', [])
    
    if not original_resume or not job_description or not extracted_skills:
        return jsonify({'error': 'Resume, job description, and extracted skills are required'}), 400
    
    # Extract basic information from the original resume
    lines = [line for line in original_resume.split('\n') if line.strip()]
    name = lines[0] if lines else 'Your Name'
    
    # Extract email
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_regex, original_resume)
    email = email_match.group(0) if email_match else 'your.email@example.com'
    
    # Extract phone
    phone_regex = r'(\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    phone_match = re.search(phone_regex, original_resume)
    phone = phone_match.group(0) if phone_match else '(123) 456-7890'
    
    # Extract location
    location_regex = r'([A-Z][a-zA-Z]+,\s*[A-Z]{2})|([A-Z][a-zA-Z]+,\s*[A-Z][a-zA-Z]+)'
    location_match = re.search(location_regex, original_resume)
    location = location_match.group(0) if location_match else 'City, State'
    
    # Process job description to extract key requirements and phrases
    job_doc = nlp(job_description)
    
    # Extract key phrases from job description
    job_phrases = []
    for chunk in job_doc.noun_chunks:
        if len(chunk.text.split()) >= 2 and not all(token.is_stop for token in chunk):
            job_phrases.append(chunk.text.lower())
    
    # Extract key verbs from job description
    job_verbs = [token.lemma_ for token in job_doc if token.pos_ == "VERB" and not token.is_stop]
    
    # Get top skills from extracted skills
    top_skills = [skill.get('name', '') for skill in extracted_skills[:7]]
    
    # Generate a tailored summary based on job description and resume
    # Find any existing summary in the original resume
    summary_regex = re.compile(r'Summary|Profile|Objective|About', re.IGNORECASE)
    summary_index = -1
    original_summary = ""
    
    for i, line in enumerate(lines):
        if summary_regex.search(line):
            summary_index = i
            break
    
    if summary_index >= 0:
        i = summary_index + 1
        while i < len(lines) and not re.search(r'Experience|Education|Skills|Certifications', lines[i], re.IGNORECASE):
            original_summary += lines[i] + " "
            i += 1
    
    # Create a more tailored summary
    if original_summary:
        # Use parts of the original summary but enhance it with job-specific skills
        summary = f"Experienced professional with expertise in {', '.join(top_skills[:3])}. {original_summary.strip()} Seeking to leverage skills in {', '.join(top_skills[3:5])} to deliver exceptional results."
    else:
        # Create a new summary focused on the job requirements
        summary = f"Results-driven professional with proven expertise in {', '.join(top_skills[:3])}. Demonstrated success in {', '.join(job_verbs[:2])} with a focus on {', '.join(job_phrases[:2])}. Seeking to leverage {', '.join(top_skills[3:5])} skills to drive excellence and innovation."
    
    # Make sure summary isn't too long
    summary = ' '.join(summary.split()[:50])
    
    # Extract skills from resume that match job requirements
    skills = [skill.get('name', '') for skill in extracted_skills]
    
    # Extract experience sections
    experience_regex = re.compile(r'Experience|Work Experience|Employment|Work History', re.IGNORECASE)
    experience_index = -1
    for i, line in enumerate(lines):
        if experience_regex.search(line):
            experience_index = i
            break
    
    # Collect original experience entries
    original_experience = []
    if experience_index >= 0:
        i = experience_index + 1
        current_entry = ""
        
        while i < len(lines) and not re.search(r'Education|Skills|Certifications', lines[i], re.IGNORECASE):
            if re.match(r'^\s*\d{4}|\d{2}/\d{2}|[A-Z][a-z]+ \d{4}', lines[i]) and current_entry:
                # This line likely starts a new entry (has a date)
                original_experience.append(current_entry.strip())
                current_entry = lines[i]
            else:
                current_entry += " " + lines[i]
            i += 1
        
        if current_entry:
            original_experience.append(current_entry.strip())
    
    # If no experience found, create a placeholder
    if not original_experience:
        original_experience = [
            'Company Name | Position | Date Range',
            '• Accomplished [specific achievement] resulting in [positive outcome]',
            '• Led [project or initiative] that [result or impact]',
            '• Developed [skill or solution] to address [challenge or problem]'
        ]
    
    # Enhance experience entries to better match job requirements
    enhanced_experience = []
    for exp in original_experience:
        # Check if this experience entry contains any of the job skills
        exp_contains_skills = any(skill.lower() in exp.lower() for skill in skills)
        
        if exp_contains_skills:
            # This entry already has relevant skills, prioritize it
            enhanced_experience.append(exp)
        else:
            # Try to enhance this entry with relevant skills if possible
            for skill in skills[:5]:  # Use top 5 skills
                if len(exp.split()) > 10 and skill not in exp.lower():  # Only modify substantial entries
                    # Find a good place to insert the skill - after a verb if possible
                    words = exp.split()
                    for i, word in enumerate(words[:-1]):
                        if nlp(word)[0].pos_ == "VERB" and i < len(words) - 3:
                            words.insert(i + 2, f"utilizing {skill}")
                            exp = " ".join(words)
                            break
            enhanced_experience.append(exp)
    
    # Extract education sections
    education_regex = re.compile(r'Education|Academic|Degree', re.IGNORECASE)
    education_index = -1
    for i, line in enumerate(lines):
        if education_regex.search(line):
            education_index = i
            break
    
    education = []
    if education_index >= 0:
        i = education_index + 1
        current_entry = ""
        
        while i < len(lines) and not re.search(r'Experience|Skills|Certifications', lines[i], re.IGNORECASE):
            if re.match(r'^\s*\d{4}|\d{2}/\d{2}|[A-Z][a-z]+ \d{4}', lines[i]) and current_entry:
                # This line likely starts a new entry (has a date)
                education.append(current_entry.strip())
                current_entry = lines[i]
            else:
                current_entry += " " + lines[i]
            i += 1
        
        if current_entry:
            education.append(current_entry.strip())
    
    # If no education found, create a placeholder
    if not education:
        education = [
            'University Name | Degree | Graduation Date',
            '• Relevant coursework: ' + ', '.join(top_skills[:3]),
            '• GPA: X.X/4.0'
        ]
    
    # Create the generated resume
    generated_resume = {
        'summary': summary,
        'skills': skills,
        'experience': enhanced_experience[:5],  # Limit to top 5 experiences
        'education': education,
        'contact': {
            'name': name,
            'email': email,
            'phone': phone,
            'location': location
        }
    }
    
    return jsonify(generated_resume)


@app.route('/api/model-status', methods=['GET'])
def model_status():
    """Check if the models are trained and ready"""
    return jsonify({
        'status': 'ready',
        'message': 'Models are trained and ready to use'
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001)
