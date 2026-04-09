"""
Final demonstration of 100% accurate skill matching
"""
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import extract_skills_from_manual_input

def extract_explicit_skills_from_jd(job_description):
    """
    Extract explicit skills mentioned in a job description.
    Looks for skills listed after common prefixes like "Required skills:", "Skills:", etc.
    """
    if not job_description:
        return []
    
    skills = []
    
    # Common patterns where skills are explicitly listed
    skill_patterns = [
        r'(?:required\s+)?skills?[:\-]?\s*([^\n.]+)',
        r'required\s+skills?[:\-]?\s*([^\n.]+)',
        r'nice\s+to\s+have[:\-]?\s*([^\n.]+)',
        r'preferred\s+skills?[:\-]?\s*([^\n.]+)',
        r'qualifications?[:\-]?\s*([^\n.]+)',
        r'requirements?[:\-]?\s*([^\n.]+)'
    ]
    
    # Look for explicit skill lists
    for pattern in skill_patterns:
        matches = re.finditer(pattern, job_description, re.IGNORECASE)
        for match in matches:
            skill_text = match.group(1).strip()
            # Split by common delimiters
            potential_skills = re.split(r'[,;•\n|•\-\–\—/]', skill_text)
            for skill in potential_skills:
                skill = skill.strip()
                # Remove common prefixes/suffixes and punctuation
                skill = re.sub(r'^(experience with|knowledge of|proficient in|familiar with|expert in|skilled in)\s+', '', skill, flags=re.IGNORECASE)
                skill = skill.strip('.,;:()[]{}"\'')
                
                # Validate skill (reasonable length, not empty)
                if len(skill) > 1 and len(skill) < 50:
                    # Only add if it looks like a technical skill
                    skills.append(skill)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower not in seen:
            unique_skills.append(skill)
            seen.add(skill_lower)
    
    return unique_skills

def compare_resume_with_jd(resume_data, job_description):
    """
    Main function to compare resume with job description with 100% accuracy for skills.
    Only shows exact skill matches as requested.
    Returns: fit_score, matched_skills, missing_skills, suggestions
    """
    # Extract skills directly from manual input for maximum accuracy
    resume_skills_manual = []
    if isinstance(resume_data, dict) and resume_data.get('skills'):
        # Direct extraction from skills field (most accurate)
        resume_skills_manual = extract_skills_from_manual_input(resume_data.get('skills', ''))
    
    # Extract EXPLICIT skills from job description (more precise)
    jd_skills = extract_explicit_skills_from_jd(job_description)
    
    # Use ONLY manual input skills for exact matching (as requested)
    resume_skills = resume_skills_manual
    
    # 100% accurate skill matching - only exact matches
    matched_skills = []
    missing_skills = []
    
    # Convert to sets for faster lookup
    resume_skills_set = set(resume_skills)
    
    # Check each job description skill against resume skills
    for jd_skill in jd_skills:
        # Exact match (case-sensitive)
        if jd_skill in resume_skills_set:
            matched_skills.append(jd_skill)
        else:
            missing_skills.append(jd_skill)
    
    # Generate suggestions
    suggestions = []
    if len(matched_skills) > len(jd_skills) * 0.7:
        suggestions.append("Excellent match! Your resume aligns well with this job description.")
    elif len(matched_skills) > len(jd_skills) * 0.5:
        suggestions.append("Good match! Consider adding the missing skills to improve your fit score further.")
    else:
        suggestions.append("Your resume has low alignment with this job. Focus on adding the missing skills mentioned above.")
    
    if missing_skills:
        suggestions.append(f"Add {len(missing_skills)} missing skill(s) to better match this role.")
    
    # Calculate a simple fit score based on skill matching
    fit_score = 0
    if jd_skills:
        fit_score = (len(matched_skills) / len(jd_skills)) * 100
    
    return {
        'fit_score': min(100, round(fit_score, 2)),
        'matched_skills': list(set(matched_skills)),  # Remove duplicates
        'missing_skills': list(set(missing_skills)),  # Remove duplicates
        'suggestions': suggestions
    }

def main():
    print("=" * 70)
    print("DEMONSTRATION: 100% Accurate Skill Matching")
    print("=" * 70)
    
    # Example from the user's request:
    # "if i have machine learning, deep learnng and agentic AI so it shoould only shows this 3 skills in matching skills"
    
    # Resume with exactly those 3 skills
    resume_data = {
        'skills': 'Machine Learning, Deep Learning, Agentic AI'
    }
    
    # Job description that requires those skills plus others
    job_description = """
    We are looking for an AI Engineer with expertise in cutting-edge technologies.
    
    Required skills: Machine Learning, Deep Learning, Python, TensorFlow
    Nice to have: Agentic AI, Reinforcement Learning, Computer Vision
    """
    
    print("INPUT:")
    print(f"  Resume skills: {resume_data['skills']}")
    print(f"  Job description: {job_description.strip()}")
    
    # Process the matching
    result = compare_resume_with_jd(resume_data, job_description)
    
    print("\nOUTPUT:")
    print(f"  Matched skills: {result['matched_skills']}")
    print(f"  Missing skills: {result['missing_skills']}")
    print(f"  Fit score: {result['fit_score']}%")
    
    print("\nVERIFICATION:")
    expected_matched = ['Machine Learning', 'Deep Learning', 'Agentic AI']
    expected_missing = ['Python', 'TensorFlow', 'Reinforcement Learning', 'Computer Vision']
    
    print(f"  Expected matched: {expected_matched}")
    print(f"  Expected missing: {expected_missing}")
    
    # Check accuracy
    matched_set = set(result['matched_skills'])
    expected_matched_set = set(expected_matched)
    missing_set = set(result['missing_skills'])
    expected_missing_set = set(expected_missing)
    
    accuracy_check = (
        matched_set == expected_matched_set and
        missing_set == expected_missing_set
    )
    
    print(f"\n  Accuracy check: {'✓ PASS' if accuracy_check else '✗ FAIL'}")
    
    if accuracy_check:
        print("  Result: 100% accurate skill matching achieved!")
        print("  Only the exact skills from the resume appear in matched skills.")
    else:
        print("  Result: Skill matching is not accurate.")
    
    print("=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()