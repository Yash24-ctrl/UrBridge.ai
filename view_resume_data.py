"""
Script to view stored resume data from the database
"""
import sqlite3
import json
from datetime import datetime

def view_all_resume_data():
    """View all resume data stored in the database"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Query all analysis history
        c.execute('''
            SELECT id, user_id, timestamp, input_type, resume_text, score, skills, 
                   experience_years, education_level, certifications, projects, 
                   languages, suggestions, analytics
            FROM analysis_history
            ORDER BY timestamp DESC
        ''')
        
        rows = c.fetchall()
        
        if not rows:
            print("No resume data found in the database.")
            return
        
        print(f"Found {len(rows)} resume analysis records:")
        print("="*80)
        
        for i, row in enumerate(rows, 1):
            print(f"\nRecord #{i}:")
            print(f"  ID: {row[0]}")
            print(f"  User ID: {row[1]}")
            print(f"  Timestamp: {row[2]}")
            print(f"  Input Type: {row[3]}")
            print(f"  Score: {row[5]:.1f}")
            print(f"  Experience: {row[7]} years")
            print(f"  Education: {row[8]}")
            print(f"  Certifications: {row[9]}")
            print(f"  Projects: {row[10]}")
            print(f"  Languages: {row[11]}")
            
            # Parse and display skills
            try:
                skills = json.loads(row[6]) if row[6] else []
                if isinstance(skills, list):
                    print(f"  Skills: {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")  # Show first 5 skills
                else:
                    print(f"  Skills: {skills}")
            except:
                print(f"  Skills: {row[6][:50]}...")  # Show first 50 chars if not JSON
            
            # Show a snippet of resume content (first 100 characters)
            resume_snippet = row[4][:100] if row[4] else "No content"
            print(f"  Resume Snippet: {resume_snippet}...")
            
            print("-" * 40)
        
        conn.close()
        
    except Exception as e:
        print(f"Error reading database: {e}")

def view_user_resume_data(user_id):
    """View resume data for a specific user"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('''
            SELECT id, timestamp, input_type, resume_text, score, skills, 
                   experience_years, education_level, certifications, projects, 
                   languages, suggestions
            FROM analysis_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (user_id,))
        
        rows = c.fetchall()
        
        if not rows:
            print(f"No resume data found for user ID {user_id}.")
            return
        
        print(f"Found {len(rows)} resume analysis records for user {user_id}:")
        print("="*80)
        
        for i, row in enumerate(rows, 1):
            print(f"\nRecord #{i}:")
            print(f"  Analysis ID: {row[0]}")
            print(f"  Timestamp: {row[1]}")
            print(f"  Input Type: {row[2]}")
            print(f"  Score: {row[4]:.1f}")
            print(f"  Experience: {row[6]} years")
            print(f"  Education: {row[7]}")
            print(f"  Certifications: {row[8]}")
            print(f"  Projects: {row[9]}")
            print(f"  Languages: {row[10]}")
            
            # Parse and display skills
            try:
                skills = json.loads(row[5]) if row[5] else []
                if isinstance(skills, list):
                    print(f"  Skills: {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")
                else:
                    print(f"  Skills: {skills}")
            except:
                print(f"  Skills: {row[5][:50]}...")
            
            print("-" * 40)
        
        conn.close()
        
    except Exception as e:
        print(f"Error reading database: {e}")

def get_user_info(user_id):
    """Get user information from the users table"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        
        if user:
            print(f"User Info - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
        else:
            print(f"User with ID {user_id} not found.")
        
        conn.close()
    except Exception as e:
        print(f"Error reading user info: {e}")

if __name__ == "__main__":
    print("AI Resume Analyzer - Database Viewer")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1. View all resume data")
        print("2. View resume data for specific user")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            view_all_resume_data()
        elif choice == "2":
            try:
                user_id = int(input("Enter user ID: "))
                get_user_info(user_id)
                print()
                view_user_resume_data(user_id)
            except ValueError:
                print("Please enter a valid user ID (number).")
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")