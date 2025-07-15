"""
Enhanced Entity Parsing Module with LightRAG Integration

Extracts key entities from GST legal documents using either LightRAG (LLM-based)
or regex patterns (fallback). Uses built-in API key configuration.
"""

import re
import os
import asyncio
import nest_asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
import json

# Apply nest_asyncio to handle event loops
nest_asyncio.apply()

# LightRAG imports
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.kg.shared_storage import initialize_pipeline_status
    from document_processor.lightrag_config import setup_legal_lightrag
    LIGHTRAG_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LightRAG not available: {e}")
    LIGHTRAG_AVAILABLE = False

logger = logging.getLogger(__name__)


class EntityParser:
    """Parse and extract entities from GST legal document text using LightRAG or regex."""
    
    def __init__(self, method="regex"):
        """
        Initialize the parser with specified method.
        
        Args:
            method (str): "lightrag" or "regex"
        """
        self.method = method
        
        # Folder structure following your requirements
        self.source_dir = Path("./data/source_docs")
        self.markdown_dir = Path("./data/markdown_files") 
        self.lightrag_dir = Path("./data/lightrag")
        
        # Initialize LightRAG if requested
        self.rag = None
        if method == "lightrag" and LIGHTRAG_AVAILABLE:
            try:
                # Use async initialization in a separate method
                logger.info("🔄 Initializing LightRAG...")
                # LightRAG will be initialized on first use
            except Exception as e:
                logger.error(f"❌ LightRAG initialization failed: {e}")
                logger.info("🔄 Falling back to regex method")
                self.method = "regex"
        elif method == "lightrag" and not LIGHTRAG_AVAILABLE:
            logger.warning("LightRAG not available, falling back to regex")
            self.method = "regex"
        
        # Regex patterns for fallback
        self.patterns = {
            'gstin': r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b',
            'pan': r'\b[A-Z]{5}\d{4}[A-Z]{1}\b',
            'dates': [
                r'\b\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}\b',
                r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b',
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}\b'
            ],
            'amounts': [
                r'₹\s*[\d,]+(?:\.\d{2})?',
                r'Rs\.?\s*[\d,]+(?:\.\d{2})?',
                r'INR\s*[\d,]+(?:\.\d{2})?',
                r'\b[\d,]+(?:\.\d{2})?\s*(?:rupees?|lakhs?|crores?)\b'
            ],
            'sections': r'(?:section|sec\.?)\s*(\d+[A-Z]*(?:\(\d+\))?)',
            'form_numbers': r'(?:DRC|ASMT|APL|GSTR)-\d+[A-Z]*',
            'case_numbers': r'(?:WP|Appeal|Case)\s*(?:No\.?)?\s*(\d+(?:/\d+)?)',
            'tax_periods': r'(?:FY|AY|tax\s+period)\s*(\d{4}-\d{2,4}|\d{4})',
            'notice_numbers': r'(?:notice|order)\s*(?:no\.?)?\s*([A-Z0-9/-]+)',
            'court_names': r'(?:high\s+court|supreme\s+court|tribunal|CESTAT)(?:\s+of\s+[A-Za-z\s]+)?'
        }
    
    async def _initialize_lightrag(self):
        """Initialize LightRAG with proper async configuration."""
        # Create lightrag directory
        self.lightrag_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup LightRAG with working configuration
        from document_processor.lightrag_config import setup_legal_lightrag
        self.rag = await setup_legal_lightrag(str(self.lightrag_dir))
        logger.info("✅ LightRAG initialized successfully")
    
    def insert_documents(self, force_reinsert=False):
        """
        Insert all markdown documents into LightRAG knowledge base.
        
        Args:
            force_reinsert (bool): If True, clear existing data and reinsert
        """
        if self.method != "lightrag":
            logger.warning("LightRAG not requested, skipping document insertion")
            return False
            
        try:
            # Initialize LightRAG if not already done
            if not self.rag:
                asyncio.run(self._initialize_lightrag())
            
            # Find all markdown files
            markdown_files = list(self.markdown_dir.glob("*.md"))
            
            if not markdown_files:
                logger.warning(f"No markdown files found in {self.markdown_dir}")
                return False
            
            logger.info(f"📄 Found {len(markdown_files)} markdown files to insert")
            
            # Prepare documents for insertion
            contents = []
            doc_ids = []
            file_paths = []
            
            for md_file in markdown_files:
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if content.strip():  # Only insert non-empty files
                        contents.append(content)
                        doc_ids.append(md_file.stem)  # filename without extension
                        file_paths.append(str(md_file))
                        logger.info(f"✅ Prepared {md_file.name}")
                    else:
                        logger.warning(f"⚠️  Skipping empty file: {md_file.name}")
                        
                except Exception as e:
                    logger.error(f"❌ Error reading {md_file.name}: {e}")
            
            if not contents:
                logger.warning("No valid content to insert")
                return False
            
            # Insert into LightRAG (simple insertion like the working test)
            logger.info(f"🚀 Inserting {len(contents)} documents into LightRAG...")
            
            for i, content in enumerate(contents):
                self.rag.insert(content)
                logger.info(f"✅ Inserted {doc_ids[i]}")
            
            logger.info(f"✅ Successfully inserted {len(contents)} documents into LightRAG")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inserting documents: {e}")
            return False
    
    def parse_entities(self, text_or_folder=None) -> Dict[str, Any]:
        """
        Extract entities using LightRAG or regex fallback.
        
        Args:
            text_or_folder: For compatibility. If None, uses inserted documents.
            
        Returns:
            Dict containing extracted entities
        """
        if self.method == "lightrag":
            try:
                return self._parse_with_lightrag()
            except Exception as e:
                logger.warning(f"LightRAG parsing failed: {e}, falling back to regex")
                if text_or_folder and isinstance(text_or_folder, str):
                    return self._parse_with_regex(text_or_folder)
                else:
                    # If no text provided and LightRAG failed, try to read from markdown files
                    combined_text = self._read_all_markdown_files()
                    return self._parse_with_regex(combined_text)
        else:
            if text_or_folder and isinstance(text_or_folder, str):
                return self._parse_with_regex(text_or_folder)
            else:
                combined_text = self._read_all_markdown_files()
                return self._parse_with_regex(combined_text)
    
    def _parse_with_lightrag(self) -> Dict[str, Any]:
        """Extract entities using LightRAG with mix mode."""
        try:
            # Initialize LightRAG if not already done
            if not self.rag:
                asyncio.run(self._initialize_lightrag())
            
            # Query for entities using mix mode
            entity_query = """
            Extract all legal entities and their relationships from the GST legal documents.
            Focus on:
            - Taxpayer names and GSTIN numbers
            - Tax authorities and officers
            - Legal proceedings and case references  
            - Tax amounts, penalties, and demands
            - Legal sections and form numbers
            - Important dates and tax periods
            - Procedural steps and relief sought
            
            Format the response as structured information with entity types and relationships.
            """
            
            from lightrag import QueryParam
            result = self.rag.query(
                entity_query,
                param=QueryParam(mode="mix", top_k=10)
            )
            
            # Parse LightRAG response into compatible format
            return self._parse_lightrag_response(result)
            
        except Exception as e:
            logger.error(f"LightRAG parsing error: {e}")
            raise
    
    def _parse_lightrag_response(self, lightrag_response: str) -> Dict[str, Any]:
        """
        Parse LightRAG response into format compatible with existing code.
        
        Args:
            lightrag_response: Raw response from LightRAG
            
        Returns:
            Dict in format similar to regex parser
        """
        # Initialize empty entities structure
        entities = {
            'gstin_numbers': [],
            'pan_numbers': [],
            'dates': [],
            'amounts': [],
            'legal_sections': [],
            'form_numbers': [],
            'case_numbers': [],
            'tax_periods': [],
            'notice_numbers': [],
            'court_names': [],
            'taxpayers': [],  # Additional entities from LightRAG
            'tax_authorities': [],
            'legal_proceedings': [],
            'relationships': []  # New: relationship information
        }
        
        # Extract entities from LightRAG response using regex as backup
        # (This is a simplified parser - LightRAG response parsing can be more sophisticated)
        response_text = str(lightrag_response)
        
        # Extract common patterns from the response
        entities['gstin_numbers'] = self._extract_gstin(response_text)
        entities['amounts'] = self._extract_amounts(response_text)
        entities['legal_sections'] = self._extract_sections(response_text)
        entities['form_numbers'] = self._extract_form_numbers(response_text)
        entities['dates'] = self._extract_dates(response_text)
        
        # Add LightRAG-specific extractions
        entities['lightrag_response'] = response_text
        entities['extraction_method'] = 'lightrag'
        
        # Generate summary
        entities['summary'] = self._generate_summary(entities)
        
        return entities
    
    def _parse_with_regex(self, text: str) -> Dict[str, Any]:
        """Extract entities using regex patterns (fallback method)."""
        entities = {
            'gstin_numbers': self._extract_gstin(text),
            'pan_numbers': self._extract_pan(text),
            'dates': self._extract_dates(text),
            'amounts': self._extract_amounts(text),
            'legal_sections': self._extract_sections(text),
            'form_numbers': self._extract_form_numbers(text),
            'case_numbers': self._extract_case_numbers(text),
            'tax_periods': self._extract_tax_periods(text),
            'notice_numbers': self._extract_notice_numbers(text),
            'court_names': self._extract_court_names(text),
            'extraction_method': 'regex'
        }
        
        # Add summary statistics
        entities['summary'] = self._generate_summary(entities)
        
        return entities
    
    def _read_all_markdown_files(self) -> str:
        """Read and combine all markdown files for regex processing."""
        combined_text = ""
        
        for md_file in self.markdown_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    combined_text += f"\n\n--- {md_file.name} ---\n\n"
                    combined_text += f.read()
            except Exception as e:
                logger.error(f"Error reading {md_file}: {e}")
        
        return combined_text
    
    # Original regex extraction methods (preserved for fallback)
    def _extract_gstin(self, text: str) -> List[str]:
        """Extract GSTIN numbers."""
        matches = re.findall(self.patterns['gstin'], text, re.IGNORECASE)
        return list(set(matches))
    
    def _extract_pan(self, text: str) -> List[str]:
        """Extract PAN numbers."""
        matches = re.findall(self.patterns['pan'], text, re.IGNORECASE)
        return list(set(matches))
    
    def _extract_dates(self, text: str) -> List[Dict[str, str]]:
        """Extract and normalize dates."""
        all_dates = []
        
        for pattern in self.patterns['dates']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                normalized_date = self._normalize_date(match)
                if normalized_date:
                    all_dates.append({
                        'original': match,
                        'normalized': normalized_date,
                        'format': self._detect_date_format(match)
                    })
        
        # Remove duplicates based on normalized date
        seen = set()
        unique_dates = []
        for date_info in all_dates:
            if date_info['normalized'] not in seen:
                seen.add(date_info['normalized'])
                unique_dates.append(date_info)
        
        return unique_dates
    
    def _extract_amounts(self, text: str) -> List[Dict[str, str]]:
        """Extract monetary amounts."""
        amounts = []
        
        for pattern in self.patterns['amounts']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cleaned_amount = self._clean_amount(match)
                if cleaned_amount:
                    amounts.append({
                        'original': match,
                        'cleaned': cleaned_amount,
                        'numeric_value': self._extract_numeric_value(cleaned_amount)
                    })
        
        return amounts
    
    def _extract_sections(self, text: str) -> List[str]:
        """Extract legal section references."""
        matches = re.findall(self.patterns['sections'], text, re.IGNORECASE)
        return list(set(matches))
    
    def _extract_form_numbers(self, text: str) -> List[str]:
        """Extract GST form numbers."""
        matches = re.findall(self.patterns['form_numbers'], text, re.IGNORECASE)
        return list(set(matches))
    
    def _extract_case_numbers(self, text: str) -> List[str]:
        """Extract case/petition numbers."""
        matches = re.findall(self.patterns['case_numbers'], text, re.IGNORECASE)
        return list(set(matches))
    
    def _extract_tax_periods(self, text: str) -> List[str]:
        """Extract tax periods/financial years."""
        matches = re.findall(self.patterns['tax_periods'], text, re.IGNORECASE)
        return list(set(matches))
    
    def _extract_notice_numbers(self, text: str) -> List[str]:
        """Extract notice/order numbers."""
        matches = re.findall(self.patterns['notice_numbers'], text, re.IGNORECASE)
        return list(set(matches))
    
    def _extract_court_names(self, text: str) -> List[str]:
        """Extract court/tribunal names."""
        matches = re.findall(self.patterns['court_names'], text, re.IGNORECASE)
        return list(set(matches))
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to YYYY-MM-DD format."""
        # Implementation of date normalization logic
        # This is a simplified version - you may want to enhance it
        try:
            # Basic date parsing logic here
            return date_str  # Placeholder
        except:
            return None
    
    def _detect_date_format(self, date_str: str) -> str:
        """Detect the format of the date string."""
        if '/' in date_str:
            return 'DD/MM/YYYY'
        elif '-' in date_str:
            return 'DD-MM-YYYY'
        else:
            return 'DD MMM YYYY'
    
    def _clean_amount(self, amount_str: str) -> str:
        """Clean and standardize amount string."""
        # Remove currency symbols and clean
        cleaned = re.sub(r'[₹Rs\.INR\s]', '', amount_str)
        return cleaned.strip()
    
    def _extract_numeric_value(self, amount_str: str) -> float:
        """Extract numeric value from amount string."""
        try:
            # Remove commas and convert to float
            numeric = re.sub(r'[,\s]', '', amount_str)
            return float(numeric)
        except:
            return 0.0
    
    def _generate_summary(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for extracted entities."""
        summary = {
            'extraction_method': entities.get('extraction_method', 'unknown'),
            'total_entities': 0,
            'entity_counts': {}
        }
        
        # Count entities by type
        for key, value in entities.items():
            if key not in ['summary', 'extraction_method', 'lightrag_response', 'relationships']:
                if isinstance(value, list):
                    count = len(value)
                    summary['entity_counts'][key] = count
                    summary['total_entities'] += count
        
        return summary
    
    def get_lightrag_status(self) -> Dict[str, Any]:
        """Get status information about LightRAG integration."""
        status = {
            'lightrag_available': LIGHTRAG_AVAILABLE,
            'current_method': self.method,
            'rag_initialized': self.rag is not None,
            'working_directory': str(self.lightrag_dir),
            'markdown_files_count': len(list(self.markdown_dir.glob("*.md"))),
        }
        
        if self.rag:
            # Add LightRAG-specific status
            status['lightrag_working_dir'] = self.rag.working_dir
        
        return status


# Convenience function for easy usage
def create_parser(method="regex") -> EntityParser:
    """
    Create an EntityParser instance with specified method.
    
    Args:
        method (str): "lightrag" or "regex" 
        
    Returns:
        EntityParser instance
    """
    return EntityParser(method=method)


# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced parser
    parser = EntityParser(method="lightrag")
    
    # Insert documents from markdown_files folder
    success = parser.insert_documents()
    
    if success:
        # Extract entities using LightRAG
        entities = parser.parse_entities()
        print("Extracted entities:", entities)
    
    # Get status
    status = parser.get_lightrag_status()
    print("Parser status:", status)