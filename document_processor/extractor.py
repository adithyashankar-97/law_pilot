"""
Document Text Extraction Module

Handles PDF and document text extraction for GST legal documents.
"""

import os
from typing import List, Dict, Any
import PyPDF2
import pdfplumber
from pathlib import Path
import logging
from docling.document_converter import DocumentConverter

# OCR imports
try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Configure logging to suppress pdfplumber warnings
logging.getLogger("pdfplumber").setLevel(logging.ERROR)


class DocumentExtractor:
    """Extract text content from various document formats."""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt']
    
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from a document file.
        
        Args:
            file_path (str): Path to the document file
            
        Returns:
            Dict containing extracted text and metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return self._extract_pdf_text(file_path)
        elif file_extension == '.txt':
            return self._extract_txt_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def extract_docling(self, file_path: str) -> Dict[str, Any]:
        converter = DocumentConverter()
        result = converter.convert(file_path)
        return result.document

    def _extract_pdf_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF using multiple methods."""
        text_content = ""
        metadata = {
            'file_path': file_path,
            'file_type': 'pdf',
            'pages': 0,
            'extraction_method': 'docling',
            'extraction_issues': []
        }
        # Method 1: Try docling first
        try:
            docling_doc = self.extract_docling(file_path)
            text_content = docling_doc.export_to_markdown()
            metadata["pages"] = docling_doc.num_pages()
        except Exception as e:
            metadata["extraction_issues"].append(f"docling failed: {str(e)}")
        
            # Method 2: Try pdfplumber first
            try:
                with pdfplumber.open(file_path) as pdf:
                    metadata['pages'] = len(pdf.pages)
                    metadata["extraction_method"] = "pdfplumber"
                    for i, page in enumerate(pdf.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text and page_text.strip():
                                text_content += page_text + "\n"
                            else:
                                # Try alternative extraction methods for this page
                                page_text = page.extract_text(layout=True)
                                if page_text and page_text.strip():
                                    text_content += page_text + "\n"
                        except Exception as page_error:
                            metadata['extraction_issues'].append(f"Page {i+1}: {str(page_error)}")
                            continue
                            
            except Exception as e:
                metadata['extraction_issues'].append(f"pdfplumber failed: {str(e)}")
                
                # Method 3: Fallback to PyPDF2
                try:
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        metadata['pages'] = len(pdf_reader.pages)
                        metadata['extraction_method'] = 'PyPDF2'
                        
                        for i, page in enumerate(pdf_reader.pages):
                            try:
                                page_text = page.extract_text()
                                if page_text and page_text.strip():
                                    text_content += page_text + "\n"
                            except Exception as page_error:
                                metadata['extraction_issues'].append(f"PyPDF2 Page {i+1}: {str(page_error)}")
                                continue
                                
                except Exception as fallback_error:
                    metadata['extraction_issues'].append(f"PyPDF2 failed: {str(fallback_error)}")
            
        # Check if we got any text
        if not text_content.strip():
            # Method 4: Try OCR if available
            if OCR_AVAILABLE:
                metadata['extraction_issues'].append("Attempting OCR extraction for image-based PDF")
                try:
                    ocr_text = self._extract_pdf_with_ocr(file_path)
                    if ocr_text and ocr_text.strip():
                        text_content = ocr_text
                        metadata['extraction_method'] = 'OCR'
                        metadata['extraction_issues'].append("Successfully extracted text using OCR")
                    else:
                        metadata['extraction_issues'].append("OCR extraction failed - no text found")
                        text_content = "[PDF processed with OCR but no text could be extracted.]"
                except Exception as ocr_error:
                    metadata['extraction_issues'].append(f"OCR failed: {str(ocr_error)}")
                    text_content = "[PDF appears to be image-based. OCR processing failed.]"
            else:
                metadata['extraction_method'] = 'failed'
                metadata['extraction_issues'].append("No text extracted - PDF may be image-based. OCR libraries not available.")
                text_content = "[PDF appears to be image-based. OCR libraries not installed.]"
        
        return {
            'text': text_content.strip(),
            'metadata': metadata
        }
    
    def _extract_pdf_with_ocr(self, file_path: str) -> str:
        """Extract text from PDF using OCR."""
        if not OCR_AVAILABLE:
            raise ImportError("OCR libraries not available")
        
        try:
            # Convert PDF to images
            images = convert_from_path(file_path, dpi=300, fmt='jpeg')
            
            extracted_text = ""
            for i, image in enumerate(images):
                try:
                    # Try multiple OCR configurations for better results
                    configs = [
                        r'--oem 3 --psm 6',  # Default configuration
                        r'--oem 3 --psm 4',  # Single column of text
                        r'--oem 3 --psm 3',  # Fully automatic page segmentation
                        r'--oem 1 --psm 6',  # Neural nets LSTM engine
                    ]
                    
                    page_text = ""
                    for config in configs:
                        try:
                            text = pytesseract.image_to_string(image, config=config, lang='eng')
                            if text and text.strip() and len(text.strip()) > len(page_text.strip()):
                                page_text = text
                        except:
                            continue
                    
                    if page_text and page_text.strip():
                        extracted_text += f"\n--- Page {i+1} ---\n"
                        extracted_text += page_text.strip() + "\n"
                    else:
                        extracted_text += f"\n--- Page {i+1} (No text detected) ---\n"
                        
                except Exception as page_error:
                    # Continue with other pages even if one fails
                    extracted_text += f"\n--- Page {i+1} (OCR Error: {str(page_error)}) ---\n"
                    continue
            
            return extracted_text.strip()
            
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")
    
    def _extract_txt_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                text_content = file.read()
        
        metadata = {
            'file_path': file_path,
            'file_type': 'txt',
            'extraction_method': 'direct_read'
        }
        
        return {
            'text': text_content.strip(),
            'metadata': metadata
        }
    
    def extract_multiple(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Extract text from multiple documents.
        
        Args:
            file_paths (List[str]): List of file paths
            
        Returns:
            List of extraction results
        """
        results = []
        for file_path in file_paths:
            try:
                result = self.extract_text(file_path)
                results.append(result)
            except Exception as e:
                results.append({
                    'text': '',
                    'metadata': {
                        'file_path': file_path,
                        'error': str(e),
                        'extraction_failed': True
                    }
                })
        return results
