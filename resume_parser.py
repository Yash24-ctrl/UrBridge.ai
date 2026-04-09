import re
import os
from PIL import Image
import io

def extract_text_from_pdf_with_ocr(pdf_path):
    """Extract text from PDF using OCR for image-based PDFs."""
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
            if text and len(text.strip()) > 30:
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
            if text and len(text.strip()) > 30:
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
            if text and len(text.strip()) > 30:
                return text
        except:
            pass
        
        # Try pdfminer
        try:
            from pdfminer.high_level import extract_text as pdfminer_extract
            text = pdfminer_extract(pdf_path)
            if text and len(str(text).strip()) > 30:
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
                # Convert page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Perform OCR
                page_ocr_text = pytesseract.image_to_string(img, lang='eng')
                if page_ocr_text:
                    ocr_text += str(page_ocr_text) + "\n"
            
            doc.close()
            if ocr_text and len(ocr_text.strip()) > 30:
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
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Convert PIL image to numpy array
                import numpy as np
                img_array = np.array(img)
                
                # Perform OCR
                results = reader.readtext(img_array)
                page_ocr_text = " ".join([str(result[1]) for result in results])
                if page_ocr_text:
                    ocr_text += str(page_ocr_text) + "\n"
            
            doc.close()
            if ocr_text and len(ocr_text.strip()) > 30:
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