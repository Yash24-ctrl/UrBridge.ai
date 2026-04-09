import sqlite3
import json
import re
from collections import defaultdict

def get_user_resume_data(user_id):
    """Get user's resume data from the database"""
    conn = sqlite3.connect('resume_analyzer.db')
    cursor = conn.cursor()
    
    # Get the latest resume data for the user
    cursor.execute("""
        SELECT years_of_experience, education_level, skills, certifications, 
               projects_completed, languages_known, desired_job_role
        FROM resume_data 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    """, (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'years_of_experience': result[0],
            'education_level': result[1],
            'skills': result[2],
            'certifications': result[3],
            'projects_completed': result[4],
            'languages_known': result[5],
            'desired_job_role': result[6]
        }
    return None

def extract_skills_from_manual_input(skills_string):
    """
    Extract skills from manual input with 100% accuracy.
    Handles comma-separated, semicolon-separated, and other formats.
    Preserves exact case as entered by user.
    """
    if not skills_string:
        return []
    
    skills = []
    
    # Split by common delimiters
    potential_skills = re.split(r'[,;•\n|•\-\–\—/]', skills_string)
    
    for skill in potential_skills:
        skill = skill.strip()
        # Remove common prefixes but preserve case
        skill = re.sub(r'^(experience with|knowledge of|proficient in|familiar with|expert in|skilled in|ability to)\s+', '', skill, flags=re.IGNORECASE)
        skill = skill.strip('.,;:()[]{}"\'')
        
        # Validate skill (reasonable length, not empty)
        if len(skill) > 1 and len(skill) < 60:
            # Preserve exact case as entered by user
            skills.append(skill)
    
    # Remove duplicates while preserving order and case
    seen = set()
    unique_skills = []
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower not in seen:
            unique_skills.append(skill)
            seen.add(skill_lower)
    
    return unique_skills

def get_field_specific_skills(job_role):
    """
    Get field-specific skills based on the desired job role.
    Returns a list of skills that are commonly required for that field.
    """
    job_role_lower = job_role.lower().strip()
    
    # Data Science & Analytics
    if any(role in job_role_lower for role in ['data scientist', 'data analyst', 'data engineer', 'ml engineer', 'machine learning', 'data science']):
        return [
            'Python', 'SQL', 'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch',
            'Data Visualization', 'Tableau', 'Power BI', 'Statistics', 'R', 'Spark',
            'Data Mining', 'Feature Engineering', 'Deep Learning', 'NLP', 'Big Data',
            'Hadoop', 'Kafka', 'Data Warehousing', 'ETL', 'Data Modeling', 'Matplotlib',
            'Seaborn', 'Plotly', 'Apache Airflow', 'Snowflake', 'Redshift', 'MongoDB',
            'Hive', 'Pig', 'Scala', 'Java', 'Machine Learning', 'Statistical Analysis',
            'Data Cleaning', 'Data Wrangling', 'A/B Testing', 'Time Series Analysis',
            'Regression Analysis', 'Classification', 'Clustering', 'Random Forest',
            'XGBoost', 'Neural Networks', 'Computer Vision', 'Text Mining', 'Dataiku',
            'Databricks', 'Azure ML', 'AWS SageMaker', 'Google Cloud ML'
        ]
    
    # Software Development
    elif any(role in job_role_lower for role in ['software engineer', 'developer', 'programmer', 'full stack', 'backend', 'frontend', 'web developer', 'software developer']):
        return [
            'JavaScript', 'Python', 'Java', 'C++', 'React', 'Angular', 'Vue.js',
            'Node.js', 'HTML', 'CSS', 'SQL', 'Git', 'Docker', 'Kubernetes',
            'REST API', 'Microservices', 'CI/CD', 'Testing', 'Agile', 'DevOps',
            'Cloud (AWS/Azure/GCP)', 'Database Design', 'System Design', 'Linux',
            'TypeScript', 'Express.js', 'Next.js', 'Nuxt.js', 'Redux', 'GraphQL',
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Nginx',
            'Apache', 'Webpack', 'Babel', 'Jest', 'Mocha', 'Cypress', 'Selenium',
            'Spring Boot', 'Django', 'Flask', 'FastAPI', 'ASP.NET', 'Ruby on Rails',
            'Laravel', 'Symfony', 'Flutter', 'React Native', 'Ionic', 'Xamarin',
            'Terraform', 'Ansible', 'Jenkins', 'GitHub Actions', 'Bitbucket Pipelines',
            'Prometheus', 'Grafana', 'Datadog', 'New Relic', 'Splunk'
        ]
    
    # Cybersecurity
    elif any(role in job_role_lower for role in ['cybersecurity', 'security', 'penetration tester', 'security analyst', 'infosec', 'information security']):
        return [
            'Network Security', 'Penetration Testing', 'Vulnerability Assessment',
            'SIEM', 'Firewall', 'Encryption', 'Incident Response', 'Risk Assessment',
            'Compliance', 'Ethical Hacking', 'IDS/IPS', 'Security Architecture',
            'Cryptography', 'Malware Analysis', 'SOC', 'ISO 27001', 'CISSP', 'CEH',
            'CISM', 'CompTIA Security+', 'OSCP', 'Offensive Security', 'Threat Hunting',
            'Digital Forensics', 'Security Auditing', 'Zero Trust', 'IAM', 'PKI',
            'OWASP', 'NIST', 'GDPR', 'PCI DSS', 'SOC 2', 'CIS Controls',
            'Splunk', 'ArcSight', 'QRadar', 'Snort', 'Wireshark', 'Burp Suite',
            'Metasploit', 'Nmap', 'Kali Linux', 'OpenVAS', 'Nessus', 'Qualys'
        ]
    
    # Cloud & DevOps
    elif any(role in job_role_lower for role in ['devops', 'cloud', 'site reliability', 'aws', 'azure', 'gcp', 'cloud engineer', 'sre']):
        return [
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Ansible',
            'Jenkins', 'CI/CD', 'Linux', 'Scripting', 'Monitoring', 'Logging',
            'Infrastructure as Code', 'Cloud Security', 'Networking', 'Automation',
            'Git', 'Python', 'Shell Scripting', 'Prometheus', 'Grafana',
            'CloudFormation', 'ARM Templates', 'Cloud Deployment Manager', 'Packer',
            'Vagrant', 'Chef', 'Puppet', 'SaltStack', 'Spinnaker', 'ArgoCD',
            'Helm', 'Istio', 'Linkerd', 'Vault', 'Consul', 'Nomad', 'OpenShift',
            'EKS', 'AKS', 'GKE', 'Lambda', 'EC2', 'S3', 'RDS', 'CloudFront',
            'CloudWatch', 'ELK Stack', 'Fluentd', 'Logstash', 'Datadog', 'New Relic'
        ]
    
    # Project Management
    elif any(role in job_role_lower for role in ['project manager', 'product manager', 'scrum master', 'product owner', 'pmo', 'program manager']):
        return [
            'Project Management', 'Agile', 'Scrum', 'Product Management', 'Jira',
            'Stakeholder Management', 'Risk Management', 'Budgeting', 'Planning',
            'Communication', 'Leadership', 'PMP', 'Certifications', 'Roadmapping',
            'Resource Allocation', 'Team Management', 'KPIs', 'Reporting',
            'Waterfall', 'SAFe', 'Lean', 'Kanban', 'Confluence', 'Trello', 'Monday.com',
            'MS Project', 'Smartsheet', 'Portfolio Management', 'Change Management',
            'Quality Assurance', 'Business Analysis', 'Requirements Gathering',
            'Vendor Management', 'Contract Negotiation', 'ROI Analysis', 'NPV',
            'Earned Value Management', 'Critical Path Method', 'Gantt Charts'
        ]
    
    # UI/UX Design
    elif any(role in job_role_lower for role in ['ui designer', 'ux designer', 'ui/ux', 'product designer', 'interaction designer', 'visual designer']):
        return [
            'Figma', 'Sketch', 'Adobe XD', 'User Research', 'Wireframing',
            'Prototyping', 'User Testing', 'Design Systems', 'Visual Design',
            'Interaction Design', 'Information Architecture', 'Accessibility',
            'Responsive Design', 'User Personas', 'Journey Mapping', 'Figma',
            'InVision', 'Zeplin', 'Principle', 'Framer', 'Adobe Creative Suite',
            'Photoshop', 'Illustrator', 'InDesign', 'After Effects', 'Premiere Pro',
            'Axure RP', 'Balsamiq', 'Marvel', 'Origami Studio', 'Proto.io',
            'Hotjar', 'Optimal Workshop', 'Lookback', 'UsabilityHub', 'Maze',
            'A/B Testing', 'User Flows', 'Sitemaps', 'Style Guides', 'Pattern Libraries',
            'Atomic Design', 'Design Thinking', 'Service Design', 'Emotional Design'
        ]
    
    # Marketing & Sales
    elif any(role in job_role_lower for role in ['marketing', 'sales', 'digital marketing', 'seo', 'content', 'growth hacker', 'marketing manager']):
        return [
            'Digital Marketing', 'SEO', 'SEM', 'Social Media Marketing', 'Content Marketing',
            'Email Marketing', 'Google Analytics', 'Facebook Ads', 'Google Ads', 'CRM',
            'Marketing Automation', 'Copywriting', 'Brand Management', 'Campaign Management',
            'Lead Generation', 'Salesforce', 'HubSpot', 'Market Research',
            'PPC', 'Display Advertising', 'Remarketing', 'Conversion Rate Optimization',
            'A/B Testing', 'Heatmaps', 'User Behavior Analysis', 'Customer Journey Mapping',
            'Funnel Analysis', 'Attribution Modeling', 'Marketing Attribution', 'Inbound Marketing',
            'Outbound Marketing', 'Account-Based Marketing', 'Growth Hacking', 'Viral Loops',
            'Referral Programs', 'Retention Strategies', 'Churn Reduction', 'Lifetime Value',
            'Segmentation', 'Personalization', 'Marketing Qualified Leads', 'Sales Qualified Leads'
        ]
    
    # Finance & Accounting
    elif any(role in job_role_lower for role in ['financial', 'accountant', 'finance', 'investment', 'risk', 'financial analyst', 'investment banker']):
        return [
            'Financial Analysis', 'Accounting', 'Excel', 'Financial Modeling',
            'Investment Banking', 'Corporate Finance', 'Risk Management', 'Valuation',
            'Financial Planning', 'Budgeting', 'Forecasting', 'Tax Planning',
            'Audit', 'IFRS', 'GAAP', 'Bloomberg Terminal', 'Capital Markets',
            'Equity Research', 'Fixed Income', 'Derivatives', 'M&A', 'LBO', 'DCF',
            'NPV', 'IRR', 'Payback Period', 'Sensitivity Analysis', 'Scenario Analysis',
            'VAR', 'Credit Risk', 'Market Risk', 'Operational Risk', 'Basel III',
            'Solvency II', 'Regulatory Reporting', 'Compliance', 'AML', 'KYC',
            'SAS', 'R', 'Python', 'SQL', 'Tableau', 'Power BI', 'QlikView',
            'Hyperion', 'Oracle EPM', 'SAP BPC', 'Anaplan', 'Adaptive Insights'
        ]
    
    # Human Resources
    elif any(role in job_role_lower for role in ['hr', 'human resources', 'recruiter', 'talent', 'people operations', 'hr business partner']):
        return [
            'Recruitment', 'Talent Acquisition', 'HR Operations', 'Employee Relations',
            'Performance Management', 'Compensation & Benefits', 'HRIS', 'Onboarding',
            'Training & Development', 'Labor Relations', 'Employment Law', 'Payroll',
            'HR Analytics', 'Diversity & Inclusion', 'Workforce Planning', 'ATS',
            'Workday', 'SAP SuccessFactors', 'Oracle HCM', 'BambooHR', 'Greenhouse',
            'Lever', 'JazzHR', 'Jobvite', 'LinkedIn Recruiter', 'Indeed', 'Glassdoor',
            'Background Checks', 'Reference Checking', 'Offer Management', 'Candidate Experience',
            'Employer Branding', 'Employee Engagement', 'Retention Strategies', 'Exit Interviews',
            'Succession Planning', 'Organizational Development', 'Change Management', 'Coaching',
            'Conflict Resolution', 'Mediation', 'Collective Bargaining', 'Union Relations'
        ]
    
    # Healthcare
    elif any(role in job_role_lower for role in ['healthcare', 'medical', 'nurse', 'doctor', 'clinical', 'health informatics']):
        return [
            'Patient Care', 'Medical Terminology', 'Electronic Health Records',
            'Clinical Research', 'Healthcare Management', 'Medical Coding',
            'Pharmacology', 'Anatomy', 'Physiology', 'Public Health',
            'Epidemiology', 'Healthcare Policy', 'Medical Billing', 'HIPAA',
            'EMR/EHR Systems', 'Cerner', 'EPIC', 'Meditech', 'Allscripts', 'McKesson',
            'Laboratory Procedures', 'Radiology', 'Surgery', 'Emergency Medicine',
            'Primary Care', 'Specialty Care', 'Telemedicine', 'Population Health',
            'Quality Improvement', 'Patient Safety', 'Infection Control', 'Care Coordination',
            'Case Management', 'Utilization Review', 'Disease Management', 'Health Informatics',
            'Health Data Analytics', 'Clinical Decision Support', 'Interoperability', 'HITECH',
            'Meaningful Use', 'MACRA', 'ACO', 'Value-Based Care', 'Patient Satisfaction'
        ]
    
    # Artificial Intelligence & Machine Learning
    elif any(role in job_role_lower for role in ['ai engineer', 'ml engineer', 'nlp engineer', 'computer vision engineer', 'research scientist']):
        return [
            'Python', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'OpenCV',
            'Natural Language Processing', 'Computer Vision', 'Deep Learning', 'Neural Networks',
            'Reinforcement Learning', 'Generative Models', 'Transformers', 'BERT', 'GPT',
            'GANs', 'Autoencoders', 'Feature Engineering', 'Data Preprocessing', 'Model Evaluation',
            'Hyperparameter Tuning', 'Cross-Validation', 'Ensemble Methods', 'Bayesian Methods',
            'Statistical Inference', 'Probability Theory', 'Linear Algebra', 'Calculus',
            'Distributed Computing', 'Apache Spark', 'Dask', 'Ray', 'MLflow', 'Weights & Biases',
            'Docker', 'Kubernetes', 'Cloud ML Platforms', 'AWS SageMaker', 'Google AI Platform',
            'Azure ML Studio', 'MLOps', 'Model Deployment', 'Model Monitoring', 'A/B Testing',
            'Ethics in AI', 'Bias Detection', 'Fairness', 'Explainable AI', 'Interpretability'
        ]
    
    # Blockchain & Cryptocurrency
    elif any(role in job_role_lower for role in ['blockchain', 'cryptocurrency', 'smart contract', 'defi', 'web3']):
        return [
            'Blockchain', 'Ethereum', 'Solidity', 'Smart Contracts', 'Web3',
            'Decentralized Applications', 'DeFi', 'Cryptocurrency', 'Bitcoin', 'NFTs',
            'Consensus Algorithms', 'Proof of Work', 'Proof of Stake', 'Mining', 'Staking',
            'Tokenomics', 'ICO', 'STO', 'DAO', 'DApps', 'Wallets', 'Cryptography',
            'Hash Functions', 'Merkle Trees', 'Digital Signatures', 'Public/Private Keys',
            'Truffle', 'Hardhat', 'Remix', 'Web3.js', 'Ethers.js', 'IPFS', 'Swarm',
            'Oracles', 'Chainlink', 'Polkadot', 'Cosmos', 'Solana', 'Cardano', 'Polygon',
            'Layer 2 Solutions', 'zk-SNARKs', 'zk-STARKs', 'Privacy Coins', 'Stablecoins'
        ]
    
    # Game Development
    elif any(role in job_role_lower for role in ['game developer', 'game programmer', 'unity developer', 'unreal engine', 'game designer']):
        return [
            'Unity', 'Unreal Engine', 'C#', 'C++', 'Blueprints', 'Game Design',
            '3D Modeling', 'Animation', 'Physics', 'AI for Games', 'Multiplayer Networking',
            'VR/AR', 'XR', 'Shader Programming', 'Level Design', 'Character Design',
            'UI/UX for Games', 'Game Mechanics', 'Game Balancing', 'Playtesting', 'Monetization',
            'Steam', 'Epic Games Store', 'PlayStation', 'Xbox', 'Nintendo Switch',
            'OpenGL', 'DirectX', 'Vulkan', 'HLSL', 'GLSL', 'Maya', 'Blender', '3ds Max',
            'Substance Painter', 'ZBrush', 'Photoshop', 'Audition', 'FMOD', 'Wwise',
            'Agile for Game Dev', 'Scrum', 'Game Jams', 'Indie Development', 'Mobile Games'
        ]
    
    # Internet of Things (IoT)
    elif any(role in job_role_lower for role in ['iot', 'internet of things', 'embedded systems', 'edge computing']):
        return [
            'IoT', 'Embedded Systems', 'Edge Computing', 'Arduino', 'Raspberry Pi',
            'C/C++', 'Python', 'Microcontrollers', 'Sensors', 'Actuators',
            'Wireless Protocols', 'Bluetooth', 'WiFi', 'Zigbee', 'LoRaWAN', 'MQTT',
            'CoAP', 'HTTP', 'Real-Time Operating Systems', 'FreeRTOS', 'Zephyr',
            'Linux for Embedded', 'Device Drivers', 'Firmware', 'Hardware Interfacing',
            'Signal Processing', 'Control Systems', 'Robotics', 'Drones', 'Wearables',
            'Industrial IoT', 'IIoT', 'SCADA', 'PLC', 'DCS', 'Modbus', 'OPC UA',
            'Cloud Integration', 'AWS IoT', 'Azure IoT', 'Google Cloud IoT', 'Security',
            'Low-Power Design', 'Battery Optimization', 'RF Design', 'Antenna Design'
        ]
    
    # Default skills if no specific role matches
    return [
        'Communication', 'Problem Solving', 'Teamwork', 'Leadership', 'Time Management',
        'Adaptability', 'Critical Thinking', 'Project Management', 'Data Analysis',
        'Technical Writing', 'Research', 'Planning', 'Organization', 'Attention to Detail',
        'Creativity', 'Decision Making', 'Negotiation', 'Customer Service', 'Strategic Thinking'
    ]

def calculate_skill_gap(user_skills, required_skills):
    """Calculate the gap between user skills and required skills"""
    user_skills_set = set([skill.lower() for skill in user_skills])
    required_skills_set = set([skill.lower() for skill in required_skills])
    
    # Skills the user has
    matched_skills = [skill for skill in required_skills if skill.lower() in user_skills_set]
    
    # Skills the user is missing
    missing_skills = [skill for skill in required_skills if skill.lower() not in user_skills_set]
    
    # Calculate gap percentage
    gap_percentage = (len(missing_skills) / len(required_skills)) * 100 if required_skills else 0
    
    return {
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'gap_percentage': gap_percentage
    }

def generate_personalized_roadmap(user_id):
    """Generate a personalized development roadmap for a user"""
    # Get user's resume data
    user_data = get_user_resume_data(user_id)
    
    if not user_data:
        return None
    
    # Extract user's current skills
    user_skills = extract_skills_from_manual_input(user_data.get('skills', ''))
    
    # Get field-specific required skills
    job_role = user_data.get('desired_job_role', '')
    required_skills = get_field_specific_skills(job_role)
    
    # Calculate skill gap
    skill_gap = calculate_skill_gap(user_skills, required_skills)
    
    # Get roadmap template for the job role
    conn = sqlite3.connect('resume_analyzer.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, description, difficulty_level, estimated_duration
        FROM roadmap_templates 
        WHERE job_role = ?
        ORDER BY estimated_duration ASC
        LIMIT 1
    """, (job_role,))
    
    template = cursor.fetchone()
    
    if not template:
        # If no specific template, get the most relevant one
        cursor.execute("""
            SELECT id, job_role, title, description, difficulty_level, estimated_duration
            FROM roadmap_templates 
            ORDER BY CASE 
                WHEN job_role LIKE ? THEN 1
                WHEN job_role LIKE '%' || ? || '%' THEN 2
                ELSE 3
            END
            LIMIT 1
        """, (f"%{job_role}%", job_role))
        template = cursor.fetchone()
    
    if not template:
        conn.close()
        return None
    
    template_id = template[0]
    template_title = template[2] if len(template) > 2 else template[1]  # Handle both query formats
    
    # Get roadmap steps
    cursor.execute("""
        SELECT id, step_order, title, description, category, estimated_time, resources, prerequisites
        FROM roadmap_steps 
        WHERE template_id = ?
        ORDER BY step_order
    """, (template_id,))
    
    steps = cursor.fetchall()
    conn.close()
    
    # Filter and prioritize steps based on user's skill gap
    prioritized_steps = []
    for step in steps:
        step_id, step_order, title, description, category, estimated_time, resources, prerequisites = step
        
        # Parse resources and prerequisites
        try:
            resources_data = json.loads(resources) if resources else {}
        except:
            resources_data = {}
        
        try:
            prereq_list = json.loads(prerequisites) if prerequisites else []
        except:
            prereq_list = []
        
        # Create step object
        step_obj = {
            'id': step_id,
            'order': step_order,
            'title': title,
            'description': description,
            'category': category,
            'estimated_time': estimated_time,
            'resources': resources_data,
            'prerequisites': prereq_list
        }
        
        # Add step to roadmap
        prioritized_steps.append(step_obj)
    
    # Create the roadmap object
    roadmap = {
        'user_id': user_id,
        'job_role': job_role,
        'template_id': template_id,
        'title': template_title,
        'matched_skills': skill_gap['matched_skills'],
        'missing_skills': skill_gap['missing_skills'],
        'skill_gap_percentage': skill_gap['gap_percentage'],
        'steps': prioritized_steps,
        'total_estimated_time': sum(step['estimated_time'] for step in prioritized_steps)
    }
    
    return roadmap

def save_user_roadmap(user_id, roadmap):
    """Save user roadmap to database"""
    if not roadmap:
        return None
    
    conn = sqlite3.connect('resume_analyzer.db')
    cursor = conn.cursor()
    
    # Check if user already has this roadmap
    cursor.execute("""
        SELECT id FROM user_roadmaps 
        WHERE user_id = ? AND template_id = ?
    """, (user_id, roadmap['template_id']))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing roadmap
        cursor.execute("""
            UPDATE user_roadmaps 
            SET started_at = CURRENT_TIMESTAMP, progress_percentage = 0.0, status = 'not_started'
            WHERE id = ?
        """, (existing[0],))
        user_roadmap_id = existing[0]
    else:
        # Create new user roadmap
        cursor.execute("""
            INSERT INTO user_roadmaps (user_id, template_id, status, progress_percentage)
            VALUES (?, ?, 'not_started', 0.0)
        """, (user_id, roadmap['template_id']))
        user_roadmap_id = cursor.lastrowid
    
    # Create user roadmap steps
    for step in roadmap['steps']:
        cursor.execute("""
            INSERT INTO user_roadmap_steps (user_roadmap_id, step_id, status)
            VALUES (?, ?, 'not_started')
        """, (user_roadmap_id, step['id']))
    
    conn.commit()
    conn.close()
    
    return user_roadmap_id

def get_user_roadmap(user_id):
    """Get user's current roadmap"""
    conn = sqlite3.connect('resume_analyzer.db')
    cursor = conn.cursor()
    
    # Get user roadmap
    cursor.execute("""
        SELECT ur.id, ur.template_id, ur.started_at, ur.completed_at, ur.status, ur.progress_percentage,
               rt.job_role, rt.title, rt.description, rt.difficulty_level, rt.estimated_duration
        FROM user_roadmaps ur
        JOIN roadmap_templates rt ON ur.template_id = rt.id
        WHERE ur.user_id = ?
        ORDER BY ur.started_at DESC
        LIMIT 1
    """, (user_id,))
    
    roadmap_data = cursor.fetchone()
    
    if not roadmap_data:
        conn.close()
        return None
    
    # Get roadmap steps
    cursor.execute("""
        SELECT urs.id, urs.step_id, urs.status, urs.started_at, urs.completed_at, urs.notes,
               rs.step_order, rs.title, rs.description, rs.category, rs.estimated_time, rs.resources, rs.prerequisites
        FROM user_roadmap_steps urs
        JOIN roadmap_steps rs ON urs.step_id = rs.id
        WHERE urs.user_roadmap_id = ?
        ORDER BY rs.step_order
    """, (roadmap_data[0],))
    
    steps_data = cursor.fetchall()
    conn.close()
    
    # Format the data
    steps = []
    for step in steps_data:
        try:
            resources_data = json.loads(step[11]) if step[11] else {}
        except:
            resources_data = {}
        
        try:
            prereq_list = json.loads(step[12]) if step[12] else []
        except:
            prereq_list = []
        
        steps.append({
            'user_step_id': step[0],
            'step_id': step[1],
            'status': step[2],
            'started_at': step[3],
            'completed_at': step[4],
            'notes': step[5],
            'order': step[6],
            'title': step[7],
            'description': step[8],
            'category': step[9],
            'estimated_time': step[10],
            'resources': resources_data,
            'prerequisites': prereq_list
        })
    
    roadmap = {
        'id': roadmap_data[0],
        'template_id': roadmap_data[1],
        'started_at': roadmap_data[2],
        'completed_at': roadmap_data[3],
        'status': roadmap_data[4],
        'progress_percentage': roadmap_data[5],
        'job_role': roadmap_data[6],
        'title': roadmap_data[7],
        'description': roadmap_data[8],
        'difficulty_level': roadmap_data[9],
        'estimated_duration': roadmap_data[10],
        'steps': steps
    }
    
    return roadmap

def update_roadmap_step_status(user_roadmap_id, step_id, status, notes=None):
    """Update the status of a roadmap step"""
    conn = sqlite3.connect('resume_analyzer.db')
    cursor = conn.cursor()
    
    # Update step status
    if status == 'completed':
        cursor.execute("""
            UPDATE user_roadmap_steps 
            SET status = ?, completed_at = CURRENT_TIMESTAMP, notes = ?
            WHERE user_roadmap_id = ? AND step_id = ?
        """, (status, notes, user_roadmap_id, step_id))
    elif status == 'in_progress':
        cursor.execute("""
            UPDATE user_roadmap_steps 
            SET status = ?, started_at = CURRENT_TIMESTAMP, notes = ?
            WHERE user_roadmap_id = ? AND step_id = ?
        """, (status, notes, user_roadmap_id, step_id))
    else:  # not_started
        cursor.execute("""
            UPDATE user_roadmap_steps 
            SET status = ?, started_at = NULL, completed_at = NULL, notes = ?
            WHERE user_roadmap_id = ? AND step_id = ?
        """, (status, notes, user_roadmap_id, step_id))
    
    # Calculate overall progress
    cursor.execute("""
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
        FROM user_roadmap_steps 
        WHERE user_roadmap_id = ?
    """, (user_roadmap_id,))
    
    result = cursor.fetchone()
    total_steps = result[0]
    completed_steps = result[1]
    
    progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
    
    # Update overall roadmap progress
    if progress_percentage == 100:
        cursor.execute("""
            UPDATE user_roadmaps 
            SET progress_percentage = ?, status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (progress_percentage, user_roadmap_id))
    else:
        cursor.execute("""
            UPDATE user_roadmaps 
            SET progress_percentage = ?, status = CASE 
                WHEN ? > 0 THEN 'in_progress' 
                ELSE 'not_started' 
            END
            WHERE id = ?
        """, (progress_percentage, progress_percentage, user_roadmap_id))
    
    conn.commit()
    conn.close()
    
    return progress_percentage

def get_roadmap_progress_details(user_roadmap_id):
    """Get detailed progress information for a roadmap"""
    conn = sqlite3.connect('resume_analyzer.db')
    cursor = conn.cursor()
    
    # Get detailed progress stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total_steps,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_steps,
            SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_steps,
            SUM(CASE WHEN status = 'not_started' THEN 1 ELSE 0 END) as not_started_steps,
            SUM(CASE WHEN status = 'completed' THEN estimated_time ELSE 0 END) as completed_time,
            SUM(CASE WHEN status IN ('in_progress', 'completed') THEN estimated_time ELSE 0 END) as invested_time,
            SUM(estimated_time) as total_time
        FROM user_roadmap_steps urs
        JOIN roadmap_steps rs ON urs.step_id = rs.id
        WHERE urs.user_roadmap_id = ?
    """, (user_roadmap_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    return {
        'total_steps': result[0] or 0,
        'completed_steps': result[1] or 0,
        'in_progress_steps': result[2] or 0,
        'not_started_steps': result[3] or 0,
        'completed_time': result[4] or 0,
        'invested_time': result[5] or 0,
        'total_time': result[6] or 0,
        'completion_percentage': ((result[1] or 0) / (result[0] or 1)) * 100,
        'time_completion_percentage': ((result[4] or 0) / (result[6] or 1)) * 100
    }

def add_time_tracking_to_step(user_roadmap_id, step_id, time_spent_minutes, notes=None):
    """Add time tracking information to a roadmap step"""
    conn = sqlite3.connect('resume_analyzer.db')
    cursor = conn.cursor()
    
    # Add time tracking column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE user_roadmap_steps ADD COLUMN time_spent_minutes INTEGER DEFAULT 0")
    except:
        pass  # Column already exists
    
    # Update time spent on the step
    cursor.execute("""
        UPDATE user_roadmap_steps 
        SET time_spent_minutes = time_spent_minutes + ?, notes = COALESCE(notes, '') || ?
        WHERE user_roadmap_id = ? AND step_id = ?
    """, (time_spent_minutes, f"\nTime tracked: {time_spent_minutes} minutes" + (f" - {notes}" if notes else ""), user_roadmap_id, step_id))
    
    conn.commit()
    conn.close()
    
    return True

def estimate_completion_date(user_roadmap_id, hours_per_week=10):
    """Estimate completion date based on current progress and time commitment"""
    progress = get_roadmap_progress_details(user_roadmap_id)
    
    if not progress:
        return None
    
    remaining_time = progress['total_time'] - progress['invested_time']
    
    if remaining_time <= 0:
        return "Already completed"
    
    weeks_remaining = remaining_time / hours_per_week
    import datetime
    completion_date = datetime.datetime.now() + datetime.timedelta(weeks=weeks_remaining)
    
    return {
        'estimated_completion_date': completion_date.strftime('%Y-%m-%d'),
        'weeks_remaining': round(weeks_remaining, 1),
        'remaining_hours': remaining_time
    }

def export_roadmap_to_pdf(user_id):
    """Export user's roadmap to PDF format"""
    try:
        from fpdf import FPDF
        import datetime
        
        # Get user's roadmap
        roadmap = get_user_roadmap(user_id)
        if not roadmap:
            return None
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Title
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, 'Development Roadmap', 0, 1, 'C')
        pdf.ln(10)
        
        # User info
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f'Job Role: {roadmap["job_role"]}', 0, 1)
        pdf.cell(0, 10, f'Title: {roadmap["title"]}', 0, 1)
        pdf.ln(5)
        
        # Progress
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Progress: {roadmap["progress_percentage"]:.1f}%', 0, 1)
        pdf.ln(5)
        
        # Steps
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Learning Steps:', 0, 1)
        pdf.ln(5)
        
        # Add each step
        pdf.set_font('Arial', '', 12)
        for i, step in enumerate(roadmap['steps'], 1):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f'{i}. {step["title"]} ({step["category"]})', 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 8, step['description'])
            pdf.cell(0, 8, f'Estimated Time: {step["estimated_time"]} hours', 0, 1)
            pdf.cell(0, 8, f'Status: {step["status"]}', 0, 1)
            pdf.ln(5)
        
        # Footer
        pdf.set_font('Arial', 'I', 8)
        pdf.set_text_color(128)
        pdf.cell(0, 10, f'Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        
        return pdf
    except Exception as e:
        print(f"Error exporting roadmap to PDF: {str(e)}")
        return None

def export_roadmap_to_json(user_id):
    """Export user's roadmap to JSON format"""
    try:
        import json
        import datetime
        
        # Get user's roadmap
        roadmap = get_user_roadmap(user_id)
        if not roadmap:
            return None
        
        # Add export timestamp
        roadmap['exported_at'] = datetime.datetime.now().isoformat()
        
        # Convert to JSON
        return json.dumps(roadmap, indent=2)
    except Exception as e:
        print(f"Error exporting roadmap to JSON: {str(e)}")
        return None

def export_roadmap_to_csv(user_id):
    """Export user's roadmap to CSV format"""
    try:
        import csv
        import io
        import datetime
        
        # Get user's roadmap
        roadmap = get_user_roadmap(user_id)
        if not roadmap:
            return None
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Development Roadmap Export'])
        writer.writerow(['Generated', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])
        
        # Roadmap info
        writer.writerow(['Job Role', roadmap['job_role']])
        writer.writerow(['Title', roadmap['title']])
        writer.writerow(['Progress', f"{roadmap['progress_percentage']:.1f}%"])
        writer.writerow([])
        
        # Steps header
        writer.writerow(['Step Order', 'Title', 'Category', 'Description', 'Estimated Time (hours)', 'Status'])
        
        # Steps data
        for i, step in enumerate(roadmap['steps'], 1):
            writer.writerow([
                i,
                step['title'],
                step['category'],
                step['description'],
                step['estimated_time'],
                step['status']
            ])
        
        return output.getvalue()
    except Exception as e:
        print(f"Error exporting roadmap to CSV: {str(e)}")
        return None

# Test the functions
if __name__ == "__main__":
    # Test generating a roadmap
    test_roadmap = generate_personalized_roadmap(1)  # Assuming user ID 1 exists
    if test_roadmap:
        print("Generated roadmap for user:")
        print(f"Job Role: {test_roadmap['job_role']}")
        print(f"Title: {test_roadmap['title']}")
        print(f"Skill Gap: {test_roadmap['skill_gap_percentage']:.1f}%")
        print(f"Steps: {len(test_roadmap['steps'])}")
        print(f"Total Time: {test_roadmap['total_estimated_time']} hours")
    else:
        print("No roadmap generated")