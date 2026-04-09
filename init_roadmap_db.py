import sqlite3
import os

def init_roadmap_tables():
    """Initialize roadmap tables in the database"""
    # Connect to the database
    conn = sqlite3.connect('resume_analyzer.db')
    cursor = conn.cursor()
    
    # Read the SQL schema file
    with open('roadmap_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Execute the schema SQL
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print("Roadmap tables created successfully!")
    except Exception as e:
        print(f"Error creating roadmap tables: {e}")
    finally:
        conn.close()

def insert_sample_roadmap_data():
    """Insert sample roadmap data for testing"""
    conn = sqlite3.connect('resume_analyzer.db')
    cursor = conn.cursor()
    
    # Insert sample roadmap templates
    roadmap_templates = [
        ('Data Scientist', 'Data Science Career Path', 'Complete roadmap to become a Data Scientist', 'intermediate', 24),
        ('Software Engineer', 'Software Engineering Career Path', 'Complete roadmap to become a Software Engineer', 'intermediate', 20),
        ('Product Manager', 'Product Management Career Path', 'Complete roadmap to become a Product Manager', 'intermediate', 18),
    ]
    
    cursor.executemany("""
        INSERT INTO roadmap_templates (job_role, title, description, difficulty_level, estimated_duration)
        VALUES (?, ?, ?, ?, ?)
    """, roadmap_templates)
    
    # Get the inserted template IDs
    cursor.execute("SELECT id, job_role FROM roadmap_templates")
    templates = cursor.fetchall()
    
    # Insert sample roadmap steps for Data Scientist
    ds_steps = [
        (templates[0][0], 1, 'Learn Python Programming', 'Master Python basics and advanced concepts', 'technical', 40, 
         '{"resources": ["Python.org", "Automate the Boring Stuff"]}', '[]'),
        (templates[0][0], 2, 'Statistics and Probability', 'Understand statistical concepts and probability theory', 'technical', 30, 
         '{"resources": ["Khan Academy Statistics", "Think Stats Book"]}', '[1]'),
        (templates[0][0], 3, 'Data Analysis with Pandas', 'Learn to manipulate and analyze data with Pandas', 'technical', 25, 
         '{"resources": ["Pandas Documentation", "Python for Data Analysis Book"]}', '[1, 2]'),
        (templates[0][0], 4, 'Data Visualization', 'Create compelling visualizations with Matplotlib and Seaborn', 'technical', 20, 
         '{"resources": ["Matplotlib Tutorials", "Seaborn Gallery"]}', '[3]'),
        (templates[0][0], 5, 'Machine Learning Fundamentals', 'Understand ML algorithms and scikit-learn', 'technical', 50, 
         '{"resources": ["Hands-On Machine Learning Book", "Andrew Ng Course"]}', '[2, 3]'),
        (templates[0][0], 6, 'Deep Learning Basics', 'Learn neural networks with TensorFlow/Keras', 'technical', 45, 
         '{"resources": ["Deep Learning Book", "TensorFlow Tutorials"]}', '[5]'),
        (templates[0][0], 7, 'SQL for Data Science', 'Query databases and perform data analysis with SQL', 'technical', 25, 
         '{"resources": ["SQL Zoo", "Mode Analytics SQL Tutorial"]}', '[1]'),
        (templates[0][0], 8, 'Build a Portfolio Project', 'Create and deploy a data science project', 'project', 60, 
         '{"resources": ["GitHub", "Heroku Deployment Guide"]}', '[1, 3, 4, 5]'),
    ]
    
    cursor.executemany("""
        INSERT INTO roadmap_steps (template_id, step_order, title, description, category, estimated_time, resources, prerequisites)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ds_steps)
    
    conn.commit()
    conn.close()
    print("Sample roadmap data inserted successfully!")

if __name__ == "__main__":
    init_roadmap_tables()
    insert_sample_roadmap_data()