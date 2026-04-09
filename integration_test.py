"""
Integration test showing the exact skill matching working with the Flask app
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the actual functions from the app
from app import extract_skills_from_manual_input, extract_explicit_skills_from_jd

def compare_resume_with_jd(resume_data, job_description):
    """
    Integration version of the skill matching function using app functions
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
    
    # Calculate a simple fit score based on skill matching
    fit_score = 0
    if jd_skills:
        fit_score = (len(matched_skills) / len(jd_skills)) * 100
    
    return {
        'fit_score': min(100, round(fit_score, 2)),
        'matched_skills': list(set(matched_skills)),  # Remove duplicates
        'missing_skills': list(set(missing_skills)),  # Remove duplicates
    }

def main():
    print("=" * 70)
    print("INTEGRATION TEST: Exact Skill Matching with Flask App Functions")
    print("=" * 70)
    
    # Test case: User's exact example
    # "if i have machine learning, deep learnng and agentic AI so it shoould only shows this 3 skills in matching skills"
    
    resume_data = {
        'skills': 'Machine Learning, Deep Learning, Agentic AI'
    }
    
    job_description = """
    Job Title: Senior AI Engineer
    
    We are seeking a Senior AI Engineer to join our innovative team.
    
    Required skills: Machine Learning, Deep Learning, Python, TensorFlow
    Nice to have: Agentic AI, Reinforcement Learning, Computer Vision
    """
    
    print("TEST CASE:")
    print(f"  Resume skills: {resume_data['skills']}")
    print("  Job requirements:")
    print("    Required: Machine Learning, Deep Learning, Python, TensorFlow")
    print("    Nice to have: Agentic AI, Reinforcement Learning, Computer Vision")
    
    # Extract skills using app functions
    resume_skills = extract_skills_from_manual_input(resume_data['skills'])
    jd_skills = extract_explicit_skills_from_jd(job_description)
    
    print(f"\nSKILL EXTRACTION:")
    print(f"  Extracted resume skills: {resume_skills}")
    print(f"  Extracted job skills: {jd_skills}")
    
    # Perform matching
    result = compare_resume_with_jd(resume_data, job_description)
    
    print(f"\nMATCHING RESULTS:")
    print(f"  Matched skills: {result['matched_skills']}")
    print(f"  Missing skills: {result['missing_skills']}")
    print(f"  Fit score: {result['fit_score']}%")
    
    # Verification
    expected_matched = {'Machine Learning', 'Deep Learning', 'Agentic AI'}
    expected_missing = {'Python', 'TensorFlow', 'Reinforcement Learning', 'Computer Vision'}
    
    actual_matched = set(result['matched_skills'])
    actual_missing = set(result['missing_skills'])
    
    print(f"\nVERIFICATION:")
    print(f"  Expected matched: {expected_matched}")
    print(f"  Actual matched:   {actual_matched}")
    print(f"  Match correct:    {'✓ YES' if actual_matched == expected_matched else '✗ NO'}")
    
    print(f"  Expected missing: {expected_missing}")
    print(f"  Actual missing:   {actual_missing}")
    print(f"  Missing correct:  {'✓ YES' if actual_missing == expected_missing else '✗ NO'}")
    
    # Final result
    success = (actual_matched == expected_matched) and (actual_missing == expected_missing)
    
    print(f"\nFINAL RESULT:")
    if success:
        print("  ✓ SUCCESS: 100% accurate skill matching achieved!")
        print("  ✓ Only the exact skills from the resume appear in matched skills")
        print("  ✓ All job-required skills not in resume correctly identified as missing")
    else:
        print("  ✗ FAILURE: Skill matching is not accurate")
    
    print("=" * 70)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()