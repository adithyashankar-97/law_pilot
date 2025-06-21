"""
Document Classification Module

Classifies GST legal documents into different types based on content analysis.
"""

import re
from typing import Dict, List, Any
from enum import Enum


class DocumentType(Enum):
    """Enumeration of GST document types."""
    SHOW_CAUSE_NOTICE = "show_cause_notice"
    COMPANY_REPLY = "company_reply"
    HEARING_MINUTES = "hearing_minutes"
    ADJUDICATION_ORDER = "adjudication_order"
    TRIBUNAL_ORDER = "tribunal_order"
    HIGH_COURT_ORDER = "high_court_order"
    APPEAL_ORDER = "appeal_order"
    RECTIFICATION_APPLICATION = "rectification_application"
    CORRESPONDENCE = "correspondence"
    SUPPORTING_EVIDENCE = "supporting_evidence"
    UNKNOWN = "unknown"


class DocumentClassifier:
    """Classify GST legal documents based on content patterns."""
    
    def __init__(self):
        self.classification_patterns = {
            DocumentType.SHOW_CAUSE_NOTICE: [
                r'show\s+cause\s+notice',
                r'DRC-01',
                r'ASMT-14',
                r'notice.*issued.*under.*section',
                r'why.*penalty.*should.*not.*be.*imposed',
                r'opportunity.*being.*heard'
            ],
            DocumentType.COMPANY_REPLY: [
                r'DRC-06',
                r'reply.*to.*show.*cause.*notice',
                r'response.*to.*notice',
                r'submission.*in.*reply',
                r'respectfully.*submitted'
            ],
            DocumentType.HEARING_MINUTES: [
                r'hearing.*minutes',
                r'personal.*hearing',
                r'proceedings.*of.*hearing',
                r'oral.*submission',
                r'hearing.*held.*on'
            ],
            DocumentType.ADJUDICATION_ORDER: [
                r'DRC-07',
                r'order.*in.*original',
                r'adjudication.*order',
                r'adjudicating.*authority',
                r'order.*passed.*under.*section'
            ],
            DocumentType.TRIBUNAL_ORDER: [
                r'appellate.*tribunal',
                r'CESTAT',
                r'tribunal.*order',
                r'appeal.*no',
                r'before.*the.*tribunal'
            ],
            DocumentType.HIGH_COURT_ORDER: [
                r'high.*court',
                r'writ.*petition',
                r'honorable.*court',
                r'court.*order',
                r'judgment.*and.*order'
            ],
            DocumentType.APPEAL_ORDER: [
                r'appeal.*order',
                r'appellate.*order',
                r'commissioner.*appeals',
                r'first.*appeal',
                r'APL-01'
            ],
            DocumentType.RECTIFICATION_APPLICATION: [
                r'rectification.*application',
                r'section.*161',
                r'rectification.*of.*error',
                r'clerical.*error',
                r'arithmetic.*error'
            ],
            DocumentType.CORRESPONDENCE: [
                r'letter.*dated',
                r'communication.*dated',
                r'office.*memorandum',
                r'circular.*no',
                r'notification.*no'
            ]
        }
    
    def classify_document(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify a document based on its text content.
        
        Args:
            text (str): Document text content
            metadata (Dict): Optional metadata about the document
            
        Returns:
            Dict containing classification results
        """
        if not text or not text.strip():
            return {
                'document_type': DocumentType.UNKNOWN,
                'confidence': 0.0,
                'matched_patterns': [],
                'classification_reason': 'Empty or no text content'
            }
        
        text_lower = text.lower()
        classification_scores = {}
        matched_patterns = {}
        
        # Score each document type based on pattern matches
        for doc_type, patterns in self.classification_patterns.items():
            score = 0
            matches = []
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 1
                    matches.append(pattern)
            
            if score > 0:
                classification_scores[doc_type] = score / len(patterns)
                matched_patterns[doc_type] = matches
        
        # Determine best classification
        if not classification_scores:
            return {
                'document_type': DocumentType.UNKNOWN,
                'confidence': 0.0,
                'matched_patterns': [],
                'classification_reason': 'No matching patterns found'
            }
        
        best_type = max(classification_scores.keys(), key=lambda k: classification_scores[k])
        confidence = classification_scores[best_type]
        
        return {
            'document_type': best_type,
            'confidence': confidence,
            'matched_patterns': matched_patterns.get(best_type, []),
            'all_scores': classification_scores,
            'classification_reason': f'Best match with {len(matched_patterns.get(best_type, []))} pattern matches'
        }
    
    def classify_multiple(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classify multiple documents.
        
        Args:
            documents (List[Dict]): List of documents with text and metadata
            
        Returns:
            List of classification results
        """
        results = []
        for doc in documents:
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            
            classification = self.classify_document(text, metadata)
            classification['source_metadata'] = metadata
            
            results.append(classification)
        
        return results
    
    def get_document_summary(self, classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of classified documents.
        
        Args:
            classifications (List[Dict]): List of classification results
            
        Returns:
            Summary statistics
        """
        type_counts = {}
        total_confidence = 0
        high_confidence_count = 0
        
        for classification in classifications:
            doc_type = classification['document_type']
            confidence = classification['confidence']
            
            if doc_type in type_counts:
                type_counts[doc_type] += 1
            else:
                type_counts[doc_type] = 1
            
            total_confidence += confidence
            if confidence > 0.5:
                high_confidence_count += 1
        
        return {
            'total_documents': len(classifications),
            'document_types': {dt.value: count for dt, count in type_counts.items()},
            'average_confidence': total_confidence / len(classifications) if classifications else 0,
            'high_confidence_classifications': high_confidence_count,
            'classification_success_rate': high_confidence_count / len(classifications) if classifications else 0
        }
