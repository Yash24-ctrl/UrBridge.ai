#!/usr/bin/env python3
"""
Diagnostic script to analyze resume parsing issues
"""

from resume_parser import parse_resume_from_pdf, extract_resume_data_from_text, preprocess_text
import os
import sys

def diagnose_resume_parsing(pdf_path=None, text_sample=None):
    """Diagnose resume parsing issues."""
    
    print("Resume Parsing Diagnostic Tool")
    print("=" * 50)
    
    if pdf_path and os.path.exists(pdf_path):
        print(f"Analyzing PDF: {pdf_path}")
        print("-" * 30)
        
        # Parse the PDF
        try:
            data = parse_resume_from_pdf(pdf_path)
            print("Parsed Data:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            
    elif text_sample:
        print("Analyzing text sample...")
        print("-" * 30)
        
        print("Original text sample:")
        print(repr(text_sample[:200]) + "..." if len(text_sample) > 200 else repr(text_sample))
        print()
        
        # Show preprocessed text
        preprocessed = preprocess_text(text_sample)
        print("Preprocessed text (first 200 chars):")
        print(repr(preprocessed[:200]) + "..." if len(preprocessed) > 200 else repr(preprocessed))
        print()
        
        # Parse the text
        data = extract_resume_data_from_text(text_sample)
        print("Extracted Data:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        print()
        
        # Detailed analysis
        print("Detailed Analysis:")
        print(f"  Skills count: {len(data.get('skills', '').split(',')) if data.get('skills') else 0}")
        print(f"  Certifications count: {data.get('certifications', '0')}")
        print(f"  Projects count: {data.get('projects_completed', '0')}")
        print(f"  Education: {data.get('education_level', '')[:100]}{'...' if len(data.get('education_level', '')) > 100 else ''}")
        print(f"  Languages: {data.get('languages_known', '')}")
        
    else:
        # Provide a sample for testing
        sample_text = """
        JOHN SMITH
        Senior Software Engineer
        San Francisco, CA | john.smith@email.com | (555) 123-4567
        
        PROFESSIONAL SUMMARY
        Experienced software engineer with 5+ years of expertise in full-stack development, 
        cloud technologies, and agile methodologies. Passionate about building scalable 
        applications and mentoring junior developers.
        
        TECHNICAL SKILLS
        Languages: Python, JavaScript, Java, SQL
        Frameworks: React, Node.js, Django, Flask
        Tools: Git, Docker, Kubernetes, AWS, Jenkins
        Databases: PostgreSQL, MongoDB, Redis
        
        PROFESSIONAL EXPERIENCE
        Senior Software Engineer | Tech Corp | Jan 2020 - Present
        - Led development of microservices architecture serving 1M+ users
        - Implemented CI/CD pipeline reducing deployment time by 60%
        - Mentored 5 junior developers and conducted code reviews
        
        SOFTWARE ENGINEER | Startup Inc | Jun 2018 - Dec 2019
        - Developed RESTful APIs using Python and Django
        - Containerized applications using Docker and deployed on AWS ECS
        - Collaborated with UX team to implement responsive frontend designs
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of California, Berkeley | 2014 - 2018
        Relevant Coursework: Data Structures, Algorithms, Database Systems
        
        CERTIFICATIONS
        - AWS Certified Solutions Architect - Associate
        - Google Cloud Professional Developer
        - Certified Kubernetes Administrator
        
        PROJECTS
        - E-commerce Platform: Built full-stack platform using React and Node.js
        - Machine Learning Pipeline: Developed data pipeline for predictive analytics
        
        LANGUAGES
        English (Native), Spanish (Intermediate)
        
        ADDITIONAL INFORMATION
        - GitHub: github.com/johnsmith
        - LinkedIn: linkedin.com/in/johnsmith
        """
        
        print("Running diagnostic with sample text...")
        print("=" * 50)
        diagnose_resume_parsing(text_sample=sample_text)

if __name__ == "__main__":
    # Check if a PDF path was provided as command line argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        diagnose_resume_parsing(pdf_path=pdf_path)
    else:
        diagnose_resume_parsing()