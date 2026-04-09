import re
import os
from PIL import Image
import io

def extract_text_from_pdf_with_ocr(pdf_path):
    """Extract text from PDF using OCR for image-based PDFs with enhanced capabilities."""
    text = ""
    
    # Method 1: Try standard text extraction methods first
    try:
        # Try PyPDF2
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += str(page_text) + "\n"
            if text and len(text.strip()) > 20:  # Reduced threshold
                return text
        except:
            pass
        
        # Try pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += str(page_text) + "\n"
            if text and len(text.strip()) > 20:
                return text
        except:
            pass
        
        # Try pymupdf
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text:
                    text += str(page_text) + "\n"
            doc.close()
            if text and len(text.strip()) > 20:
                return text
        except:
            pass
        
        # Try pdfminer
        try:
            from pdfminer.high_level import extract_text as pdfminer_extract
            text = pdfminer_extract(pdf_path)
            if text and len(str(text).strip()) > 20:
                return str(text)
        except:
            pass
    except Exception as e:
        pass
    
    # Method 2: If text extraction failed, try OCR (for scanned/image-based PDFs)
    try:
        import fitz  # PyMuPDF for converting PDF to images
        doc = fitz.open(pdf_path)
        ocr_text = ""
        
        # Try pytesseract first
        try:
            import pytesseract
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Convert page to image with higher resolution
                pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))  # 3x zoom for better OCR
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Perform OCR with better configuration
                page_ocr_text = pytesseract.image_to_string(img, lang='eng')
                if page_ocr_text:
                    ocr_text += str(page_ocr_text) + "\n"
            
            doc.close()
            if ocr_text and len(ocr_text.strip()) > 20:
                return ocr_text
        except ImportError:
            pass  # pytesseract not installed
        except Exception as e:
            pass
        
        # Try easyocr as fallback
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Convert PIL image to numpy array
                import numpy as np
                img_array = np.array(img)
                
                # Perform OCR with paragraph processing
                results = reader.readtext(img_array, paragraph=True)
                page_ocr_text = " ".join([str(result[1]) for result in results])
                if page_ocr_text:
                    ocr_text += str(page_ocr_text) + "\n"
            
            doc.close()
            if ocr_text and len(ocr_text.strip()) > 20:
                return ocr_text
        except ImportError:
            pass  # easyocr not installed
        except Exception as e:
            pass
        
        doc.close()
    except Exception as e:
        pass
    
    # Return whatever text we got, even if minimal
    return text if text else ""


def extract_skills(text):
    """Enhanced skills extraction with improved pattern matching and expanded limits."""
    # Look for skills section
    skills_section_patterns = [
        r'skills\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'technical skills\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'expertise\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'competencies\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'proficiencies\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'abilities\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'skills[\s\S]*?(?=\n\n|\n[A-Z][a-z]|work experience|employment|certifications|projects|\Z)',
        r'technical expertise\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'core skills\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'specialized skills\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'hard skills\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'soft skills\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))'
    ]
    
    skills_text = ''
    for pattern in skills_section_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            skills_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
            break
    
    # If no skills section found, try to extract skills from bullet points or lists
    if not skills_text:
        # Look for bulleted lists that might contain skills
        bullet_patterns = [
            r'[•\-\*]\s*([^\n\r]+)',  # Bullet points
            r'\d+\.\s*([^\n\r]+)'      # Numbered lists
        ]
        
        skills_list = []
        for pattern in bullet_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills_list.extend(matches)
        
        if len(skills_list) > 3:  # Likely a skills section if we have multiple bullet points
            skills_text = ', '.join(skills_list[:20])  # Take first 20 items (increased from 15)
    
    # If still no skills found, use a comprehensive approach
    if not skills_text:
        # Use a comprehensive list of common skills
        common_skills = [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'swift', 'kotlin',
            'sql', 'nosql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'html', 'css', 'sass', 'scss', 'bootstrap', 'tailwind', 'react', 'angular', 'vue',
            'node.js', 'express', 'django', 'flask', 'spring', 'laravel', 'ruby on rails',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible',
            'git', 'jenkins', 'github actions', 'gitlab ci', 'linux', 'bash', 'shell scripting',
            'machine learning', 'deep learning', 'neural networks', 'tensorflow', 'pytorch',
            'data analysis', 'data visualization', 'pandas', 'numpy', 'matplotlib', 'seaborn',
            'tableau', 'power bi', 'excel', 'statistics', 'r', 'spark',
            'project management', 'agile', 'scrum', 'kanban', 'jira', 'confluence',
            'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
            'design thinking', 'ux research', 'ui design', 'figma', 'sketch', 'adobe creative suite',
            'seo', 'sem', 'google analytics', 'facebook ads', 'google ads', 'content marketing',
            'salesforce', 'hubspot', 'crm', 'erp', 'sap', 'oracle',
            'ansible', 'puppet', 'chef', 'jenkins', 'circleci', 'travis', 'docker', 'kubernetes',
            'postgresql', 'oracle', 'sql server', 'sqlite', 'cassandra', 'hadoop', 'spark',
            'android', 'ios', 'flutter', 'react native', 'xamarin', 'ionic',
            'unity', 'unreal engine', 'game development', 'cocos2d', 'corona',
            'photoshop', 'illustrator', 'indesign', 'premiere', 'after effects', 'lightroom',
            'autocad', 'solidworks', 'catia', 'proe', 'fusion 360',
            'matlab', 'sas', 'spss', 'tableau', 'qlikview', 'looker',
            'cybersecurity', 'infosec', 'cissp', 'ceh', 'comptia', 'cism', 'cisa',
            'blockchain', 'ethereum', 'solidity', 'web3', 'defi', 'smart contracts',
            'iot', 'embedded systems', 'arduino', 'raspberry pi', 'microcontrollers',
            'devops', 'ci/cd', 'azure devops', 'aws codepipeline', 'bitbucket',
            'agile', 'scrum', 'kanban', 'lean', 'six sigma', 'pmp', 'capm'
        ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in common_skills:
            # Use word boundaries to avoid partial matches
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower, re.IGNORECASE):
                found_skills.append(skill.title())
        
        skills_text = ', '.join(found_skills)
    
    # Clean and format the skills
    if skills_text:
        # Split by common delimiters
        delimiters = [',', ';', '\n', '\r', '/', '|', '\\', 'and']
        skills_list = [skills_text]
        
        for delimiter in delimiters:
            temp_list = []
            for item in skills_list:
                # Split and clean each item
                parts = item.split(delimiter)
                for part in parts:
                    part = part.strip()
                    if part:  # Only add non-empty parts
                        temp_list.append(part)
            skills_list = temp_list
        
        # Clean each skill
        cleaned_skills = []
        for skill in skills_list:
            skill = skill.strip()
            # Remove trailing punctuation
            skill = re.sub(r'[.,;:]+$', '', skill)
            # Filter out very short items and common non-skills
            if len(skill) > 1 and not re.match(r'^\d+$', skill) and skill.lower() not in ['and', 'or', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'a', 'an', 'is', 'are', 'was', 'were', 'has', 'have', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall']:
                # Try to exclude company names and dates
                if not re.match(r'\d{4}', skill) and len(skill) < 50:  # Reasonable length limit
                    # Additional filtering to exclude common non-skills
                    if not any(word in skill.lower() for word in ['company', 'university', 'college', 'school', 'year', 'years', 'month', 'months', 'day', 'days', 'experience', 'experienced', 'worked', 'worked as', 'worked in', 'worked with', 'worked on']):
                        cleaned_skills.append(skill)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in cleaned_skills:
            skill_lower = skill.lower().replace(' ', '').replace('-', '').replace('_', '')
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill)
        
        # Limit to 20 skills (enhanced from 15)
        return ', '.join(unique_skills[:20])
    
    return ''


def extract_education_level(text):
    """Enhanced education extraction with expanded patterns and improved accuracy."""
    # Look for education section first
    education_section_patterns = [
        r'education[\s\S]{0,2000}?(?=\n\n|\n[A-Z][a-z]|work experience|employment|skills|certifications|projects|\Z)',
        r'academic[\s\S]{0,2000}?(?=\n\n|\n[A-Z][a-z]|work experience|employment|skills|certifications|projects|\Z)',
        r'qualification[\s\S]{0,2000}?(?=\n\n|\n[A-Z][a-z]|work experience|employment|skills|certifications|projects|\Z)',
        r'degree[\s\S]{0,2000}?(?=\n\n|\n[A-Z][a-z]|work experience|employment|skills|certifications|projects|\Z)',
        r'academic background[\s\S]{0,2000}?(?=\n\n|\n[A-Z][a-z]|work experience|employment|skills|certifications|projects|\Z)',
        r'education background[\s\S]{0,2000}?(?=\n\n|\n[A-Z][a-z]|work experience|employment|skills|certifications|projects|\Z)',
        r'academic qualifications[\s\S]{0,2000}?(?=\n\n|\n[A-Z][a-z]|work experience|employment|skills|certifications|projects|\Z)',
        r'education qualifications[\s\S]{0,2000}?(?=\n\n|\n[A-Z][a-z]|work experience|employment|skills|certifications|projects|\Z)'
    ]
    
    education_text = ''
    for pattern in education_section_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            education_text = match.group(0)
            break
    
    # If no education section found, use entire text
    if not education_text:
        education_text = text
    
    # Extract education level with more comprehensive patterns
    education_keywords = {
        'phd': ['phd', 'doctorate', 'ph.d', 'doctoral', 'phd degree', 'doctorate degree'],
        'master': ['master', 'ms', 'ma', 'm.sc', 'm.s', 'master\'s', 'mba', 'm.tech', 'm.eng', 'm.sc.', 'm.a.', 'm.s.', 'm.b.a', 'master\'s degree', 'graduate', 'post graduate', 'postgraduate'],
        'bachelor': ['bachelor', 'bs', 'ba', 'b.sc', 'b.a', 'b.e', 'b.tech', 'b.eng', 'b.sc.', 'b.a.', 'b.e.', 'b.tech.', 'bachelor\'s', 'bachelor\'s degree', 'undergraduate', 'bachelor degree'],
        'diploma': ['diploma', 'associate degree', 'associate\'s degree', 'certificate', 'certification', 'high school', 'secondary education', '12th', '10th', 'ssc', 'hsc', 'diploma degree'],
        'high school': ['high school', 'secondary', '12th', 'hsc', 'higher secondary', 'intermediate', '10th', 'ssc', 'matriculation', 'secondary school', 'high school diploma']
    }
    
    # Look for education level from the education text
    education_level = ''
    for level, keywords in education_keywords.items():
        for keyword in keywords:
            # Use word boundaries for better matching
            if re.search(r'\b' + re.escape(keyword) + r'\b', education_text, re.IGNORECASE):
                # Try to get more specific education information
                edu_match = re.search(rf'{re.escape(keyword)}[\s\S]*?(?:in|of|:\s*)([^\n\r\.]{5,100})', education_text, re.IGNORECASE)
                if edu_match:
                    field_of_study = edu_match.group(1).strip()
                    # Clean the field of study
                    field_of_study = re.sub(r'[.,;:]+$', '', field_of_study)
                    field_of_study = field_of_study.title()
                    education_level = f'{level.title()} in {field_of_study}'
                else:
                    # Look for institution name
                    inst_pos = education_text.lower().find(keyword.lower())
                    if inst_pos != -1:
                        remaining_text = education_text[inst_pos:]
                        inst_match = re.search(r'(?:from|at|\\-|:)?\s*([A-Za-z\s&.]{5,50})', remaining_text)
                        if inst_match and len(inst_match.group(1).strip()) > 3:
                            institution = inst_match.group(1).strip()
                            education_level = f'{level.title()} from {institution}'
                        else:
                            education_level = f'{level.title()} Degree' if level in ['bachelor', 'master'] else level.title()
                break
        if education_level:
            break
    
    # If no specific education found, try to extract from degree + field patterns
    if not education_level:
        # Look for patterns like "Bachelor of Science in Computer Science"
        degree_field_pattern = r'(?:bachelor|bsc|ba|btech|master|msc|ma|mtech|mba|phd)\s+(?:of|in)?\s+([A-Za-z\s&.]{5,50})'
        field_match = re.search(degree_field_pattern, education_text, re.IGNORECASE)
        if field_match:
            field = field_match.group(1).strip()
            education_level = f'Degree in {field.title()}'
    
    return education_level if education_level else 'Not specified'


def extract_certifications(text):
    """Enhanced certifications extraction with improved pattern matching and expanded limits."""
    # Look for certifications section
    cert_patterns = [
        r'certifications?\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'certificates?\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'certifications?[\s\S]{0,1000}?(?=\n\n|\n[A-Z][a-z]|work experience|skills|projects|\Z)',
        r'credentials?\s*[:\-]?\s*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))'
    ]
    
    cert_text = ''
    for pattern in cert_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cert_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
            break
    
    # Count certifications with improved logic
    if cert_text:
        # Look for specific certification names
        cert_count = len(re.findall(r'\b(?:certification|certificate|certified|credential|exam|passed)\b', cert_text, re.IGNORECASE))
        if cert_count == 0:
            # If no explicit mentions, count items that look like certifications
            cert_items = re.findall(r'[A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*){1,5}', cert_text)
            cert_count = len([item for item in cert_items if len(item) > 5 and len(item) < 100])
        
        # Enhanced count with specific certification patterns
        specific_certs = [
            'AWS', 'Google', 'Microsoft', 'Cisco', 'Oracle', 'CompTIA', 'PMP', 'CISSP', 'CEH', 'CISA', 'CISM',
            'CCNA', 'CCNP', 'OCP', 'MCSE', 'ITIL', 'PRINCE2', 'Six Sigma', 'CRISC', 'CAPM', 'CSM', 'CBAP',
            'PMI', 'Scrum', 'Agile', 'SAFe', 'TOGAF', 'Architect', 'Professional', 'Associate', 'Expert'
        ]
        
        specific_count = 0
        for cert in specific_certs:
            specific_count += len(re.findall(r'\b' + re.escape(cert) + r'\b', cert_text, re.IGNORECASE))
        
        # Use the higher of the two counts, but cap at 30 (enhanced from 20)
        final_count = min(30, max(1, cert_count, specific_count))
        return str(final_count)
    else:
        # If no certification section found, look for certifications in the entire text
        cert_count = len(re.findall(r'\b(?:AWS|Google|Microsoft|Cisco|Oracle|CompTIA|PMP|CISSP|CEH|CISA|CISM|CCNA|CCNP|OCP|MCSE|ITIL|PRINCE2|Six Sigma|CRISC|CAPM|CSM|CBAP|PMI|Scrum|Agile|SAFe|TOGAF)\b', text, re.IGNORECASE))
        return str(min(30, cert_count))  # Cap at 30


def extract_projects(text):
    """Enhanced projects extraction with improved pattern matching and expanded limits."""
    # Look for projects section
    project_patterns = [
        r'projects[\s\S]{0,1000}?(?=\n\n|\n[A-Z][a-z]|skills|certifications|\Z)',
        r'project experience[\s\S]{0,1000}?(?=\n\n|\n[A-Z][a-z]|skills|certifications|\Z)',
        r'key projects[\s\S]{0,1000}?(?=\n\n|\n[A-Z][a-z]|skills|certifications|\Z)',
        r'portfolio[\s\S]{0,1000}?(?=\n\n|\n[A-Z][a-z]|skills|certifications|\Z)'
    ]
    
    projects_text = ''
    for pattern in project_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            projects_text = match.group(0)
            break
    
    # Count projects based on project descriptions
    if projects_text:
        # Count paragraphs or substantial sections that look like project descriptions
        project_descriptions = re.findall(r'[A-Z][^.\n\r]{20,}', projects_text)
        project_count = len(project_descriptions)
        
        # Also look for project items in lists
        list_patterns = [
            r'[•\-\*]\s*[A-Z][^\n\r]{10,}',
            r'\d+\.\s*[A-Z][^\n\r]{10,}'
        ]
        
        list_count = 0
        for pattern in list_patterns:
            matches = re.findall(pattern, projects_text)
            list_count += len(matches)
        
        # Enhanced project counting with specific keywords
        project_keywords = [
            'web app', 'mobile app', 'application', 'platform', 'system', 'solution', 'dashboard', 
            'api', 'integration', 'migration', 'development', 'implementation', 'automation',
            'pipeline', 'architecture', 'framework', 'library', 'tool', 'service'
        ]
        
        keyword_count = 0
        for keyword in project_keywords:
            keyword_count += len(re.findall(r'\b' + re.escape(keyword) + r'\b', projects_text, re.IGNORECASE))
        
        # Use the highest count, but cap at 20 (enhanced from 10)
        final_count = min(20, max(project_count, list_count // 2, keyword_count // 3))
        return str(max(1, final_count)) if final_count > 0 else '0'
    else:
        # Fallback to simple keyword matching
        project_count = len(re.findall(r'\bproject\b', text, re.IGNORECASE))
        return str(min(20, project_count))  # Cap at 20


def extract_resume_data_from_text(text):
    """Extract resume data from text using enhanced parsing functions with improved accuracy."""
    data = {
        'years_of_experience': '0',
        'education_level': '',
        'skills': '',
        'certifications': '0',
        'projects_completed': '0',
        'languages_known': '',
        'availability_days': '0',
        'desired_job_role': '',
        'current_location_city': '',
        'previous_job_title': '',
        'notice_period_days_IT': '0'
    }
    
    # Convert to lowercase for easier matching
    text_lower = text.lower()
    
    # Extract years of experience with more comprehensive patterns
    exp_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?|\+\s*years?)\s*(?:of\s*)?experience',
        r'experience[\s\S]*?(\d+(?:\.\d+)?)\s*(?:years?|yrs?|\+\s*years?)',
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
        r'(\d+(?:\.\d+)?)\s*(?:\+\s*)?(?:years?|yrs?)\s*(?:of\s*experience|experience)',
        r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:total|cumulative)',
        r'over\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
        r'about\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
        r'around\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)'
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, text_lower)
        if match:
            # Ensure the experience value is reasonable (not too high)
            exp_val = float(match.group(1))
            if exp_val <= 50:  # Max reasonable experience
                data['years_of_experience'] = str(exp_val)
                break
    
    # Extract education level using enhanced function
    data['education_level'] = extract_education_level(text)
    
    # Extract skills using enhanced function
    data['skills'] = extract_skills(text)
    
    # Extract certifications using enhanced function
    data['certifications'] = extract_certifications(text)
    
    # Extract projects using enhanced function
    data['projects_completed'] = extract_projects(text)
    
    # Extract languages with improved pattern matching
    language_patterns = [
        r'languages?[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'language proficiency[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'languages known[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'fluent in[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'native language[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))'
    ]
    
    lang_text = ''
    for pattern in language_patterns:
        match = re.search(pattern, text_lower)
        if match:
            lang_text = match.group(1)
            break
    
    # If no language section found, look for common language mentions
    if not lang_text:
        common_languages = ['english', 'spanish', 'french', 'german', 'chinese', 'japanese', 'korean', 'hindi', 'arabic', 'portuguese', 'italian', 'dutch', 'russian', 'swedish', 'norwegian']
        found_languages = []
        for lang in common_languages:
            if lang in text_lower:
                found_languages.append(lang.title())
        lang_text = ', '.join(found_languages) if found_languages else 'English'
    
    data['languages_known'] = lang_text if lang_text else 'English'
    
    # Extract job role with improved pattern matching
    job_role_patterns = [
        r'(?:seeking|looking for|interested in|target role|desired position)\s+(.*?)(?:position|role|job)',
        r'(?:objective|summary|career objective)[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'(?:professional summary|profile)[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'currently working as[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'current role[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))'
    ]
    
    job_role_text = ''
    for pattern in job_role_patterns:
        match = re.search(pattern, text_lower)
        if match:
            job_role_text = match.group(1)
            break
    
    # If no specific job role found, look for job titles in work experience section
    if not job_role_text:
        work_exp_patterns = [
            r'work experience[\s\S]*?(?=\n\n|\n[A-Z][a-z]|skills|projects|\Z)',
            r'employment[\s\S]*?(?=\n\n|\n[A-Z][a-z]|skills|projects|\Z)',
            r'professional experience[\s\S]*?(?=\n\n|\n[A-Z][a-z]|skills|projects|\Z)',
            r'professional background[\s\S]*?(?=\n\n|\n[A-Z][a-z]|skills|projects|\Z)'
        ]
        
        work_text = ''
        for pattern in work_exp_patterns:
            match = re.search(pattern, text_lower)
            if match:
                work_text = match.group(0)
                break
        
        if work_text:
            # Look for job titles (capitalized phrases that might be job titles)
            job_titles = re.findall(r'[A-Z][A-Za-z\s]{3,30}(?:\s+[A-Z][A-Za-z\s]*){0,4}', work_text)
            if job_titles:
                # Filter and take the most likely job title
                for title in job_titles:
                    title = title.strip()
                    # Common job title keywords to look for
                    job_keywords = ['engineer', 'developer', 'manager', 'analyst', 'director', 'lead', 'specialist', 'consultant', 'architect', 'scientist', 'designer', 'coordinator', 'executive', 'officer', 'supervisor', 'associate', 'assistant', 'intern', 'senior', 'principal', 'vp', 'cto', 'ceo', 'cfo', 'cio', 'pmo', 'admin', 'administrator', 'technician', 'programmer', 'tester', 'coordinator', 'advisor', 'representative', 'coordinator']
                    if any(keyword in title.lower() for keyword in job_keywords) and len(title) > 3 and len(title) < 50:
                        job_role_text = title
                        break
    
    # Extract location
    location_patterns = [
        r'location[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'current location[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'based in[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'reside in[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'address[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))'
    ]
    
    location_text = ''
    for pattern in location_patterns:
        match = re.search(pattern, text_lower)
        if match:
            location_text = match.group(1).strip()
            break
    
    # If no location found in specific sections, look for city names
    if not location_text:
        # Common city names to look for
        common_cities = ['new york', 'london', 'tokyo', 'paris', 'berlin', 'mumbai', 'delhi', 'bangalore', 'pune', 'hyderabad', 'chennai', 'kolkata', 'san francisco', 'seattle', 'austin', 'dallas', 'chicago', 'boston', 'washington', 'atlanta', 'los angeles', 'toronto', 'vancouver', 'sydney', 'melbourne', 'singapore', 'dubai', 'mumbai', 'pune', 'hyderabad', 'bangalore', 'delhi', 'mexico city', 'sao paulo', 'moscow', 'beijing', 'shanghai', 'hong kong', 'singapore', 'seoul', 'bangkok', 'kuala lumpur']
        for city in common_cities:
            if city in text_lower:
                location_text = city.title()
                break
    
    data['current_location_city'] = location_text if location_text else 'Not specified'
    
    # Extract notice period
    notice_patterns = [
        r'notice period[:\-\s]*(\d+)',
        r'available in[:\-\s]*(\d+)',
        r'can join in[:\-\s]*(\d+)',
        r'joining time[:\-\s]*(\d+)',
        r'available after[:\-\s]*(\d+)',
        r'notice[:\-\s]*(\d+)',
        r'(\d+)\s*(?:days?|months?)\s*(?:notice|available|joining)'
    ]
    
    for pattern in notice_patterns:
        match = re.search(pattern, text_lower)
        if match:
            notice_val = match.group(1)
            # Validate notice period (should be reasonable)
            if 0 <= int(notice_val) <= 365:
                data['notice_period_days_IT'] = notice_val
                break
    
    # Extract availability days
    availability_patterns = [
        r'available\s+(?:immediately|right away|now|asap)',
        r'can start\s+(?:immediately|right away|now|asap)',
        r'available\s+(\d+)',
        r'can join\s+(\d+)',
        r'available after\s+(\d+)',
    ]
    
    for pattern in availability_patterns:
        match = re.search(pattern, text_lower)
        if match:
            if 'immediately' in match.group(0) or 'now' in match.group(0) or 'asap' in match.group(0):
                data['availability_days'] = '0'
                break
            elif match.group(1):
                availability_val = match.group(1)
                if 0 <= int(availability_val) <= 365:
                    data['availability_days'] = availability_val
                    break
    
    # Extract previous job title
    prev_job_patterns = [
        r'previous position[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'former role[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'previous job[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))',
        r'last position[:\-\s]*([^\n\r]*?(?=\n\n|\n[A-Z][a-z]|\Z))'
    ]
    
    prev_job_text = ''
    for pattern in prev_job_patterns:
        match = re.search(pattern, text_lower)
        if match:
            prev_job_text = match.group(1).strip()
            break
    
    # If no previous job found in specific sections, try to extract from work experience
    if not prev_job_text and work_text:
        # Look for the first job title in work experience
        job_titles = re.findall(r'[A-Z][A-Za-z\s]{3,30}(?:\s+[A-Z][A-Za-z\s]*){0,4}', work_text)
        for title in job_titles:
            title = title.strip()
            job_keywords = ['engineer', 'developer', 'manager', 'analyst', 'director', 'lead', 'specialist', 'consultant', 'architect', 'scientist', 'designer', 'coordinator', 'executive', 'officer', 'supervisor', 'associate', 'assistant', 'intern', 'senior', 'principal', 'vp', 'cto', 'ceo', 'cfo', 'cio', 'pmo', 'admin', 'administrator', 'technician', 'programmer', 'tester', 'coordinator', 'advisor', 'representative', 'coordinator']
            if any(keyword in title.lower() for keyword in job_keywords) and len(title) > 3 and len(title) < 50:
                prev_job_text = title
                break
    
    data['previous_job_title'] = prev_job_text if prev_job_text else 'Not specified'
    
    data['desired_job_role'] = job_role_text.strip() if job_role_text else 'General Professional'
    
    return data