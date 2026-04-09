"""
Quick test to verify accuracy improvements
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions we need
from app import compare_resume_with_jd

# Simple test case
sample_resume = {
    'skills': 'Python, JavaScript, React, Node.js, SQL'
}

sample_job_description = """
Looking for a Full Stack Developer with skills in Python, JavaScript, React, Node.js, MongoDB
Required skills: Python, JavaScript, React, Node.js
"""

result = compare_resume_with_jd(sample_resume, sample_job_description)
print(f"Score: {result['fit_score']}/10")
print(f"Percentage: {result['fit_score_percentage']}%")
print(f"Matched: {result['matched_skills']}")
print(f"Missing: {result['missing_skills']}")