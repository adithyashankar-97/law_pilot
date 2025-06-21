"""
Entity Parsing Module

Extracts key entities from GST legal documents including dates, amounts, 
GSTIN numbers, and legal references.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import calendar


class EntityParser:
    """Parse and extract entities from GST legal document text."""
    
    def __init__(self):
        # Regex patterns for entity extraction
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
    
    def parse_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract all entities from document text.
        
        Args:
            text (str): Document text content
            
        Returns:
            Dict containing extracted entities
        """
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
            'court_names': self._extract_court_names(text)
        }
        
        # Add summary statistics
        entities['summary'] = self._generate_summary(entities)
        
        return entities
    
    def _extract_gstin(self, text: str) -> List[str]:
        """Extract GSTIN numbers."""
        matches = re.findall(self.patterns['gstin'], text, re.IGNORECASE)
        return list(set(matches))  # Remove duplicates
    
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
        try:
            # Handle different date formats
            date_str = date_str.strip()
            
            # DD/MM/YYYY or DD-MM-YYYY
            if re.match(r'\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}', date_str):
                parts = re.split(r'[-/\.]', date_str)
                day, month, year = parts[0], parts[1], parts[2]
                if len(year) == 2:
                    year = '20' + year if int(year) < 50 else '19' + year
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Month DD, YYYY or DD Month YYYY
            month_names = {
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
            }
            
            for month_name, month_num in month_names.items():
                if month_name in date_str.lower():
                    parts = re.split(r'[\s,]+', date_str)
                    day = None
                    year = None
                    
                    for part in parts:
                        if part.isdigit():
                            if len(part) == 4:
                                year = part
                            elif 1 <= int(part) <= 31:
                                day = part
                    
                    if day and year:
                        return f"{year}-{month_num}-{day.zfill(2)}"
            
        except Exception:
            pass
        
        return None
    
    def _detect_date_format(self, date_str: str) -> str:
        """Detect the format of the date string."""
        if re.match(r'\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}', date_str):
            return 'DD/MM/YYYY'
        elif re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', date_str, re.IGNORECASE):
            return 'Month DD, YYYY'
        return 'Unknown'
    
    def _clean_amount(self, amount_str: str) -> str:
        """Clean and standardize amount string."""
        # Remove currency symbols and extra spaces
        cleaned = re.sub(r'[₹Rs\.INR\s]', '', amount_str)
        return cleaned.strip()
    
    def _extract_numeric_value(self, amount_str: str) -> Optional[float]:
        """Extract numeric value from amount string."""
        try:
            # Remove commas and convert to float
            numeric_str = re.sub(r'[,]', '', amount_str)
            
            # Handle lakhs and crores
            if 'lakh' in amount_str.lower():
                return float(numeric_str) * 100000
            elif 'crore' in amount_str.lower():
                return float(numeric_str) * 10000000
            else:
                return float(numeric_str)
        except (ValueError, TypeError):
            return None
    
    def _generate_summary(self, entities: Dict[str, Any]) -> Dict[str, int]:
        """Generate summary statistics of extracted entities."""
        return {
            'total_gstin_numbers': len(entities['gstin_numbers']),
            'total_dates': len(entities['dates']),
            'total_amounts': len(entities['amounts']),
            'total_sections': len(entities['legal_sections']),
            'total_forms': len(entities['form_numbers']),
            'total_cases': len(entities['case_numbers'])
        }
