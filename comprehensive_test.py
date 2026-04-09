import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions we need to test
from app import get_field_specific_skills, compare_resume_with_jd

print("=== Comprehensive Test of Field-Specific Skills Enhancement ===\n")

# Test 1: Field-specific skills extraction
print("1. Testing field-specific skills extraction:")

test_roles = [
    "Data Scientist",
    "Software Engineer", 
    "Cybersecurity Analyst",
    "DevOps Engineer",
    "Product Manager",
    "UI/UX Designer",
    "Digital Marketer",
    "Financial Analyst",
    "HR Specialist",
    "Unknown Role"
]

for role in test_roles:
    skills = get_field_specific_skills(role)
    print(f"   {role}: {skills[0]}, {skills[1]}, {skills[2]}...")

print("\n2. Testing skill comparison with field-specific enhancements:")

# Test case: Data Scientist
resume_data_ds = {
    'skills': 'Python, SQL, Machine Learning, Data Analysis, Statistics',
    'desired_job_role': 'Data Scientist'
}

job_description_ds = """
We are looking for a Data Scientist with expertise in:
- Python and R programming
- Deep Learning frameworks (TensorFlow, PyTorch)
- Data Visualization (Tableau, Power BI)
- Big Data technologies (Spark, Hadoop)
- Cloud platforms (AWS, GCP)
- Strong mathematical foundation
"""

print("\n   Test Case: Data Scientist")
print(f"   Resume Skills: {resume_data_ds['skills']}")
results_ds = compare_resume_with_jd(resume_data_ds, job_description_ds)
print(f"   Matched Skills: {len(results_ds['matched_skills'])} skills")
print(f"   Missing Skills: {len(results_ds['missing_skills'])} skills")
print(f"   Sample Missing Skills: {results_ds['missing_skills'][:3]}")

# Test case: Software Engineer
resume_data_se = {
    'skills': 'JavaScript, React, Node.js, HTML, CSS',
    'desired_job_role': 'Software Engineer'
}

job_description_se = """
We are looking for a Software Engineer with expertise in:
- Backend development (Python, Java, or Go)
- Database design and management (SQL, MongoDB)
- Cloud platforms (AWS, Azure)
- Containerization (Docker, Kubernetes)
- Testing frameworks (Jest, PyTest)
- Git and CI/CD pipelines
"""

print("\n   Test Case: Software Engineer")
print(f"   Resume Skills: {resume_data_se['skills']}")
results_se = compare_resume_with_jd(resume_data_se, job_description_se)
print(f"   Matched Skills: {len(results_se['matched_skills'])} skills")
print(f"   Missing Skills: {len(results_se['missing_skills'])} skills")
print(f"   Sample Missing Skills: {results_se['missing_skills'][:3]}")

print("\n=== Test Complete ===")