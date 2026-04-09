#!/usr/bin/env python3
"""
Create a test PDF file from text content
"""

from fpdf import FPDF

def create_test_pdf():
    """Create a test PDF file from the sample resume text"""
    
    # Read the test resume text
    with open('test_resume.txt', 'r') as f:
        lines = f.readlines()
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add content to PDF
    for line in lines:
        # Handle encoding issues
        try:
            pdf.cell(200, 10, txt=line.strip(), ln=True, align='L')
        except:
            # If there are encoding issues, skip the line or use a placeholder
            pdf.cell(200, 10, txt="Line with special characters", ln=True, align='L')
    
    # Save the PDF
    pdf.output("test_resume.pdf")
    print("Test PDF created successfully: test_resume.pdf")

if __name__ == "__main__":
    create_test_pdf()