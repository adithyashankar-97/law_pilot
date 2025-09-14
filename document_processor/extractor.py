"""
Document Text Extraction Module

Handles PDF and document text extraction for GST legal documents.
Enhanced with advanced docling integration using latest API patterns.
"""

import os
from typing import List, Dict, Any
import PyPDF2
import pdfplumber
from pathlib import Path
import logging
import pickle
# Enhanced docling imports with latest API
try:
    from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption, PowerpointFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
    from docling.datamodel.base_models import InputFormat
    from docling_core.types.doc import ImageRefMode
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

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
    """Extract text content from various document formats with enhanced docling support."""
    
    def __init__(self, save_images=True, image_descriptions=True):
        self.supported_formats = ['.pdf', '.txt', '.docx', '.pptx']
        self.save_images = save_images
        self.image_descriptions = image_descriptions
        
        # Add folder paths
        # self.source_dir = Path(source_dir)
        # self.markdown_dir = Path(markdown_dir)
        
        # Create directories
        # self.images_dir = Path("data/extracted_images")
        # self.images_dir.mkdir(parents=True, exist_ok=True)
        # self.source_dir.mkdir(parents=True, exist_ok=True)
        # self.markdown_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup docling converter once
        self._setup_docling_converter()
    def extract_folder(self, skip_existing=True) -> List[Dict[str, Any]]:
        """
        Extract text from all documents in source folder (like script_insert)
        
        Args:
            skip_existing (bool): Skip if markdown file already exists
            
        Returns:
            List of extraction results with metadata
        """
        print(f"🚀 Processing documents from: {self.source_dir}")
        
        # Find all documents
        source_files = []
        for ext in self.supported_formats:
            pattern = f"*{ext}"
            source_files.extend(self.source_dir.glob(pattern))
        
        if not source_files:
            print(f"📄 No documents found in {self.source_dir}")
            return []
        
        print(f"📄 Found {len(source_files)} documents to process")
        
        results = []
        
        for file_path in source_files:
            try:
                # Check if we should skip
                markdown_path = self.markdown_dir / f"{file_path.stem}.md"
                
                if skip_existing and markdown_path.exists():
                    print(f"⏭️  Skipping {file_path.name} (markdown exists)")
                    results.append({
                        'source_file': str(file_path),
                        'markdown_file': str(markdown_path),
                        'status': 'skipped',
                        'reason': 'already_exists'
                    })
                    continue
                
                print(f"🔄 Processing {file_path.name}...")
                
                # Extract using your existing method
                result = self.extract_text(str(file_path))
                
                # Move the markdown file to proper location
                self._move_markdown_to_folder(file_path, result)
                
                results.append({
                    'source_file': str(file_path),
                    'markdown_file': str(markdown_path),
                    'status': 'success',
                    'text_length': len(result['text']),
                    'extraction_method': result['metadata'].get('extraction_method'),
                    'metadata': result['metadata']
                })
                
                print(f"✅ Processed {file_path.name}")
                
            except Exception as e:
                print(f"❌ Failed to process {file_path.name}: {str(e)}")
                results.append({
                    'source_file': str(file_path),
                    'status': 'error',
                    'error': str(e)
                })
        
        # Summary
        success_count = sum(1 for r in results if r['status'] == 'success')
        skipped_count = sum(1 for r in results if r['status'] == 'skipped')
        error_count = sum(1 for r in results if r['status'] == 'error')
        
        print(f"\n📊 Processing Summary:")
        print(f"   ✅ Processed: {success_count}")
        print(f"   ⏭️  Skipped: {skipped_count}")
        print(f"   ❌ Errors: {error_count}")
        
        return results

    def _move_markdown_to_folder(self, source_path: Path, extraction_result: Dict):
        """Move markdown file from current directory to markdown folder"""
        
        # Current markdown file location (your existing code saves here)
        current_md = Path.cwd() / f"{source_path.stem}.md"
        
        # Target location
        target_md = self.markdown_dir / f"{source_path.stem}.md"
        
        try:
            if current_md.exists():
                # Move to proper folder
                current_md.rename(target_md)
                
                # Update metadata to reflect new location
                if 'metadata' in extraction_result:
                    extraction_result['metadata']['markdown_saved'] = str(target_md)
        
        except Exception as e:
            logging.warning(f"Failed to move markdown file: {e}")

    def get_markdown_files(self) -> List[Dict[str, Any]]:
        """
        Get all processed markdown files (for LightRAG)
        
        Returns:
            List of markdown files with content and metadata
        """
        markdown_files = []
        
        for md_path in self.markdown_dir.glob("*.md"):
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                markdown_files.append({
                    'file_path': str(md_path),
                    'file_name': md_path.name,
                    'content': content,
                    'doc_id': md_path.stem,  # For LightRAG
                    'size': md_path.stat().st_size
                })
                
            except Exception as e:
                logging.error(f"Error reading {md_path}: {e}")
        
        print(f"📝 Found {len(markdown_files)} markdown files")
        return markdown_files
    def _setup_docling_converter(self):
        """Setup the docling converter with enhanced options."""
        if not DOCLING_AVAILABLE:
            self.docling_converter = None
            return
        
        try:
            # Setup enhanced pipeline options
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_table_structure = True
            pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
            pipeline_options.generate_picture_images = True
            pipeline_options.generate_page_images = True
            pipeline_options.images_scale = 2.0
            pipeline_options.do_picture_classification = True
            
            # Create converter with all format support
            format_options = {
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
            
            # Add office formats if available
            try:
                format_options.update({
                    InputFormat.DOCX: WordFormatOption(),
                    InputFormat.PPTX: PowerpointFormatOption()
                })
            except Exception:
                pass  # Office formats not available
            
            self.docling_converter = DocumentConverter(format_options=format_options)
            
        except Exception as e:
            logging.warning(f"Failed to setup docling converter: {str(e)}")
            self.docling_converter = None
    
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
        elif file_extension in ['.docx', '.pptx']:
            return self._extract_office_text(file_path)
        elif file_extension == '.txt':
            return self._extract_txt_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _extract_office_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from Office documents (DOCX, PPTX) using docling."""
        metadata = {
            'file_path': file_path,
            'file_type': Path(file_path).suffix.lower()[1:],  # Remove the dot
            'extraction_issues': []
        }
        
        if DOCLING_AVAILABLE and self.docling_converter:
            # try:
            text_content, docling_metadata = self._extract_with_docling_latest(file_path)
            metadata.update(docling_metadata)
            metadata['extraction_method'] = 'docling_enhanced'
            
            if text_content and text_content.strip():
                return {
                    'text': text_content.strip(),
                    'metadata': metadata
                }
            else:
                metadata['extraction_issues'].append("Docling returned empty content")
        #     except Exception as e:
        #         metadata['extraction_issues'].append(f"Docling enhanced failed: {str(e)}")
        else:
            metadata['extraction_issues'].append("Docling not available")
        
        # Fallback for office documents
        metadata['extraction_method'] = 'failed'
        metadata['extraction_issues'].append("No suitable extraction method for office documents without docling")
        text_content = f"[{metadata['file_type'].upper()} file - requires docling for processing]"
        
        return {
            'text': text_content,
            'metadata': metadata
        }
    
    def _extract_pdf_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF using 4-tier strategy with enhanced docling primary."""
        metadata = {
            'file_path': file_path,
            'file_type': 'pdf',
            'extraction_issues': []
        }
        
        # Method 1: Enhanced Docling (Primary) - using latest API
        if DOCLING_AVAILABLE and self.docling_converter:
            # try:
            text_content, docling_metadata = self._extract_with_docling_latest(file_path)
            metadata.update(docling_metadata)
            metadata['extraction_method'] = 'docling_enhanced'
            
            if text_content and text_content.strip():
                return {
                    'text': text_content.strip(),
                    'metadata': metadata
                }
            else:
                metadata['extraction_issues'].append("Docling returned empty content")
            # except Exception as e:
            #     metadata['extraction_issues'].append(f"Docling enhanced failed: {str(e)}")
        else:
            metadata['extraction_issues'].append("Docling not available")
        
        # Method 2: pdfplumber (Fallback 1)
        try:
            with pdfplumber.open(file_path) as pdf:
                text_content = ""
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                    except Exception:
                        continue
                
                metadata['pages'] = len(pdf.pages)
                
                if text_content and text_content.strip():
                    metadata['extraction_method'] = 'pdfplumber'
                    return {
                        'text': text_content.strip(),
                        'metadata': metadata
                    }
                else:
                    metadata['extraction_issues'].append("pdfplumber returned empty content")
        except Exception as e:
            metadata['extraction_issues'].append(f"pdfplumber failed: {str(e)}")
        
        # Method 3: PyPDF2 (Fallback 2)
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                for page in pdf_reader.pages:
                    try:
                        text_content += page.extract_text() + "\n"
                    except Exception:
                        continue
                
                metadata['pages'] = len(pdf_reader.pages)
                
                if text_content and text_content.strip():
                    metadata['extraction_method'] = 'pypdf2'
                    return {
                        'text': text_content.strip(),
                        'metadata': metadata
                    }
                else:
                    metadata['extraction_issues'].append("PyPDF2 returned empty content")
        except Exception as e:
            metadata['extraction_issues'].append(f"PyPDF2 failed: {str(e)}")
        
        # Method 4: OCR (Final Fallback)
        if OCR_AVAILABLE:
            try:
                text_content = self._extract_pdf_with_ocr(file_path)
                metadata['extraction_method'] = 'ocr'
                
                if text_content and text_content.strip():
                    return {
                        'text': text_content.strip(),
                        'metadata': metadata
                    }
                else:
                    metadata['extraction_issues'].append("OCR returned empty content")
            except Exception as e:
                metadata['extraction_issues'].append(f"OCR failed: {str(e)}")
                text_content = "[PDF appears to be image-based. OCR processing failed.]"
        else:
            metadata['extraction_method'] = 'failed'
            metadata['extraction_issues'].append("No text extracted - PDF may be image-based. OCR libraries not available.")
            text_content = "[PDF appears to be image-based. OCR libraries not installed.]"
        
        return {
            'text': text_content.strip(),
            'metadata': metadata
        }
    
    def _extract_with_docling_latest(self, file_path: str) -> tuple[str, Dict[str, Any]]:
        """Extract text using latest docling API with automatic image handling."""
        # try:
        # Convert document using the pre-configured converter
        doc_name = Path(file_path).stem
        output_dir = os.path.join(Path(file_path).parent, doc_name.split(".")[0])
        markdown_file = Path(output_dir) / f"{doc_name}.md"
        if not os.path.exists(markdown_file):
            os.makedirs(output_dir, exist_ok=True)  # Use markdown_dir instead of current directory                
            result = self.docling_converter.convert(file_path)
            doc = result.document
            # Create document-specific output directory for markdown and images
            if self.save_images:
                # Use REFERENCED mode to save images separately and create references
                doc.save_as_markdown(
                    filename=str(markdown_file), 
                    image_mode=ImageRefMode.REFERENCED
                )
            else:
                # Use PLACEHOLDER mode for image placeholders without saving files
                doc.save_as_markdown(
                    filename=str(markdown_file), 
                    image_mode=ImageRefMode.PLACEHOLDER
                )
            
        # Read the generated markdown content
        with open(markdown_file, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        
        # Count images and tables for metadata
        image_count = self._count_markdown_images(markdown_content)
        table_count = self._count_markdown_tables(markdown_content)
        
        # Prepare metadata
        metadata = {
            'extraction_method': 'docling_enhanced',
            # 'pages': len(doc.pages) if hasattr(doc, 'pages') else None,
            'tables_found': table_count,
            'images_extracted': image_count,
            'markdown_saved': str(markdown_file),
            'extraction_issues': []
        }
        
        return markdown_content, metadata
            
        # except Exception as e:
        #     raise Exception(f"Enhanced docling extraction failed: {str(e)}")
    
    def _count_markdown_images(self, markdown_content: str) -> int:
        """Count image references in markdown content."""
        try:
            # Count ![...] patterns (markdown image syntax)
            import re
            image_pattern = r'!\[.*?\]\(.*?\)'
            images = re.findall(image_pattern, markdown_content)
            return len(images)
        except:
            return 0
    
    def _count_markdown_tables(self, markdown_content: str) -> int:
        """Count tables in markdown content."""
        try:
            # Count markdown table patterns (lines with |)
            lines = markdown_content.split('\n')
            table_lines = [line for line in lines if '|' in line and '---' not in line]
            # Estimate table count (rough approximation)
            return len(table_lines) // 3 if table_lines else 0
        except:
            return 0
    
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
