"""
Case Data Model

Represents a GST legal case containing multiple documents and analysis results.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from .document import Document, DocumentType


class CaseStatus(Enum):
    """Enumeration of case processing statuses."""
    CREATED = "created"
    DOCUMENTS_UPLOADED = "documents_uploaded"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    AFFIDAVIT_GENERATED = "affidavit_generated"
    COMPLETED = "completed"
    ERROR = "error"


class CaseType(Enum):
    """Enumeration of GST case types."""
    ITC_MISMATCH = "itc_mismatch"
    CLASSIFICATION_DISPUTE = "classification_dispute"
    PROCEDURAL_VIOLATION = "procedural_violation"
    VALUATION_ISSUE = "valuation_issue"
    PENALTY_DISPUTE = "penalty_dispute"
    APPEAL_CASE = "appeal_case"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class Timeline:
    """Timeline of events in the case."""
    events: List[Dict[str, Any]] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_days: Optional[int] = None
    gaps_identified: List[str] = field(default_factory=list)


@dataclass
class CaseAnalysis:
    """Comprehensive case analysis results."""
    case_type: CaseType = CaseType.UNKNOWN
    key_facts: List[str] = field(default_factory=list)
    legal_issues: List[Dict[str, Any]] = field(default_factory=list)
    procedural_violations: List[str] = field(default_factory=list)
    timeline: Optional[Timeline] = None
    recommendations: List[str] = field(default_factory=list)
    strength_assessment: str = ""
    risk_factors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class Case:
    """
    Represents a complete GST legal case with multiple documents.
    
    This model aggregates information from multiple documents and provides
    case-level analysis and insights.
    """
    
    def __init__(self, case_id: str, case_name: str = ""):
        """
        Initialize a new Case instance.
        
        Args:
            case_id (str): Unique identifier for the case
            case_name (str): Human-readable case name
        """
        # Basic case information
        self.case_id = case_id
        self.case_name = case_name or f"Case_{case_id}"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Case status and type
        self.status = CaseStatus.CREATED
        self.case_type = CaseType.UNKNOWN
        
        # Documents in the case
        self.documents: List[Document] = []
        self.document_count = 0
        
        # Case analysis
        self.analysis: Optional[CaseAnalysis] = None
        
        # Case metadata
        self.client_info: Dict[str, Any] = {}
        self.case_details: Dict[str, Any] = {}
        self.tags: List[str] = []
        self.notes: str = ""
        
        # Processing tracking
        self.processing_log: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Add initial log entry
        self._add_log_entry("Case created")
    
    def _add_log_entry(self, action: str, details: Optional[Dict] = None):
        """Add an entry to the processing log."""
        entry = {
            'timestamp': datetime.now(),
            'status': self.status.value,
            'action': action,
            'details': details or {}
        }
        self.processing_log.append(entry)
        self.updated_at = datetime.now()
    
    def add_document(self, document: Document):
        """
        Add a document to the case.
        
        Args:
            document (Document): Document to add
        """
        self.documents.append(document)
        self.document_count = len(self.documents)
        self.status = CaseStatus.DOCUMENTS_UPLOADED
        self._add_log_entry("Document added", {
            'document_name': document.file_name,
            'document_type': document.document_type.value,
            'total_documents': self.document_count
        })
    
    def remove_document(self, document_path: str) -> bool:
        """
        Remove a document from the case.
        
        Args:
            document_path (str): Path of document to remove
            
        Returns:
            bool: True if document was removed, False if not found
        """
        for i, doc in enumerate(self.documents):
            if doc.file_path == document_path:
                removed_doc = self.documents.pop(i)
                self.document_count = len(self.documents)
                self._add_log_entry("Document removed", {
                    'document_name': removed_doc.file_name,
                    'remaining_documents': self.document_count
                })
                return True
        return False
    
    def get_document_by_path(self, file_path: str) -> Optional[Document]:
        """
        Get a document by its file path.
        
        Args:
            file_path (str): Path of the document
            
        Returns:
            Document or None if not found
        """
        for doc in self.documents:
            if doc.file_path == file_path:
                return doc
        return None
    
    def get_documents_by_type(self, doc_type: DocumentType) -> List[Document]:
        """
        Get all documents of a specific type.
        
        Args:
            doc_type (DocumentType): Type of documents to retrieve
            
        Returns:
            List of documents of the specified type
        """
        return [doc for doc in self.documents if doc.document_type == doc_type]
    
    def set_analysis(self, analysis: CaseAnalysis):
        """
        Set case analysis results.
        
        Args:
            analysis (CaseAnalysis): Case analysis results
        """
        self.analysis = analysis
        self.case_type = analysis.case_type
        self.status = CaseStatus.ANALYZED
        self._add_log_entry("Case analyzed", {
            'case_type': analysis.case_type.value,
            'facts_count': len(analysis.key_facts),
            'issues_count': len(analysis.legal_issues),
            'violations_count': len(analysis.procedural_violations)
        })
    
    def add_client_info(self, info: Dict[str, Any]):
        """
        Add client information to the case.
        
        Args:
            info (Dict): Client information
        """
        self.client_info.update(info)
        self._add_log_entry("Client info updated")
    
    def add_case_details(self, details: Dict[str, Any]):
        """
        Add case details.
        
        Args:
            details (Dict): Case details
        """
        self.case_details.update(details)
        self._add_log_entry("Case details updated")
    
    def add_error(self, error: str):
        """
        Add an error to the case.
        
        Args:
            error (str): Error message
        """
        self.errors.append(error)
        self.status = CaseStatus.ERROR
        self._add_log_entry("Error occurred", {'error': error})
    
    def add_warning(self, warning: str):
        """
        Add a warning to the case.
        
        Args:
            warning (str): Warning message
        """
        self.warnings.append(warning)
        self._add_log_entry("Warning issued", {'warning': warning})
    
    def add_tag(self, tag: str):
        """Add a tag to the case."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of case processing.
        
        Returns:
            Dict containing processing summary
        """
        document_types = {}
        processed_docs = 0
        docs_with_errors = 0
        
        for doc in self.documents:
            doc_type = doc.document_type.value
            document_types[doc_type] = document_types.get(doc_type, 0) + 1
            if doc.is_processed():
                processed_docs += 1
            if doc.has_errors():
                docs_with_errors += 1
        
        return {
            'case_id': self.case_id,
            'case_name': self.case_name,
            'status': self.status.value,
            'case_type': self.case_type.value,
            'total_documents': self.document_count,
            'processed_documents': processed_docs,
            'documents_with_errors': docs_with_errors,
            'document_types': document_types,
            'has_analysis': self.analysis is not None,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_document_summary(self) -> List[Dict[str, Any]]:
        """
        Get a summary of all documents in the case.
        
        Returns:
            List of document summaries
        """
        return [doc.get_processing_summary() for doc in self.documents]
    
    def get_timeline_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the case timeline.
        
        Returns:
            Dict containing timeline summary
        """
        if not self.analysis or not self.analysis.timeline:
            return {}
        
        timeline = self.analysis.timeline
        return {
            'total_events': len(timeline.events),
            'start_date': timeline.start_date.isoformat() if timeline.start_date else None,
            'end_date': timeline.end_date.isoformat() if timeline.end_date else None,
            'duration_days': timeline.duration_days,
            'gaps_identified': len(timeline.gaps_identified),
            'events': timeline.events
        }
    
    def get_legal_issues_summary(self) -> List[Dict[str, Any]]:
        """
        Get a summary of legal issues identified.
        
        Returns:
            List of legal issues
        """
        if not self.analysis:
            return []
        return self.analysis.legal_issues
    
    def is_complete(self) -> bool:
        """Check if case processing is complete."""
        return self.status in [CaseStatus.COMPLETED, CaseStatus.AFFIDAVIT_GENERATED]
    
    def has_errors(self) -> bool:
        """Check if case has any errors."""
        return len(self.errors) > 0 or any(doc.has_errors() for doc in self.documents)
    
    def get_all_entities(self) -> Dict[str, List[Any]]:
        """
        Get all entities from all documents in the case.
        
        Returns:
            Dict containing aggregated entities
        """
        all_entities = {
            'gstin_numbers': set(),
            'dates': [],
            'amounts': [],
            'legal_sections': set(),
            'form_numbers': set(),
            'case_numbers': set()
        }
        
        for doc in self.documents:
            if doc.entities_present:
                entities = doc.entities_present
                all_entities['gstin_numbers'].update(entities.gstin_numbers)
                all_entities['dates'].extend(entities.dates)
                all_entities['amounts'].extend(entities.amounts)
                all_entities['legal_sections'].update(entities.legal_sections)
                all_entities['form_numbers'].update(entities.form_numbers)
                all_entities['case_numbers'].update(entities.case_numbers)
        
        # Convert sets to lists for JSON serialization
        return {
            'gstin_numbers': list(all_entities['gstin_numbers']),
            'dates': all_entities['dates'],
            'amounts': all_entities['amounts'],
            'legal_sections': list(all_entities['legal_sections']),
            'form_numbers': list(all_entities['form_numbers']),
            'case_numbers': list(all_entities['case_numbers'])
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert case to dictionary representation.
        
        Returns:
            Dict representation of the case
        """
        return {
            'case_id': self.case_id,
            'case_name': self.case_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status.value,
            'case_type': self.case_type.value,
            'document_count': self.document_count,
            'documents': [doc.to_dict() for doc in self.documents],
            'analysis': self.analysis.__dict__ if self.analysis else None,
            'client_info': self.client_info,
            'case_details': self.case_details,
            'tags': self.tags,
            'notes': self.notes,
            'processing_log': self.processing_log,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def __str__(self) -> str:
        """String representation of the case."""
        return f"Case({self.case_id}, {self.case_name}, {self.document_count} docs, {self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the case."""
        return (f"Case(case_id='{self.case_id}', "
                f"name='{self.case_name}', "
                f"status={self.status.value}, "
                f"documents={self.document_count}, "
                f"errors={len(self.errors)})")
