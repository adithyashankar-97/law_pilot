"""
Document Data Model

Represents a legal document in the GST Law Co-pilot processing pipeline.
This model gets populated progressively as the document moves through
different stages of processing.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field


class DocumentType(Enum):
    """Enumeration of supported document types."""
    SHOW_CAUSE_NOTICE = "show_cause_notice"
    ADJUDICATION_ORDER = "adjudication_order"
    APPEAL_ORDER = "appeal_order"
    TRIBUNAL_ORDER = "tribunal_order"
    CORRESPONDENCE = "correspondence"
    UNKNOWN = "unknown"


class ProcessingStage(Enum):
    """Enumeration of processing stages."""
    UPLOADED = "uploaded"
    TEXT_EXTRACTED = "text_extracted"
    CLASSIFIED = "classified"
    ENTITIES_PARSED = "entities_parsed"
    ANALYZED = "analyzed"
    COMPLETED = "completed"


@dataclass
class ExtractionMetadata:
    """Metadata from text extraction process."""
    file_path: str
    file_type: str
    file_size: Optional[int] = None
    pages: Optional[int] = None
    extraction_method: str = ""
    extraction_issues: List[str] = field(default_factory=list)
    processing_time: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ClassificationResult:
    """Result from document classification."""
    document_type: DocumentType = DocumentType.UNKNOWN
    confidence: float = 0.0
    matched_patterns: List[str] = field(default_factory=list)
    classification_reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EntityData:
    """Structured entity data extracted from document."""
    gstin_numbers: List[str] = field(default_factory=list)
    dates: List[Dict[str, Any]] = field(default_factory=list)
    amounts: List[Dict[str, Any]] = field(default_factory=list)
    legal_sections: List[str] = field(default_factory=list)
    form_numbers: List[str] = field(default_factory=list)
    case_numbers: List[str] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AnalysisResult:
    """Results from document analysis."""
    facts: List[Dict[str, Any]] = field(default_factory=list)
    legal_issues: List[Dict[str, Any]] = field(default_factory=list)
    timeline_events: List[Dict[str, Any]] = field(default_factory=list)
    procedural_violations: List[str] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class Document:
    """
    Comprehensive document model that gets populated throughout the processing pipeline.
    
    This model serves as the central data structure that carries information
    about a document through all stages of processing - from initial upload
    to final analysis.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize a new Document instance.
        
        Args:
            file_path (str): Path to the document file
        """
        # Basic document information
        self.file_path = file_path
        self.file_name = file_path.split('/')[-1] if '/' in file_path else file_path
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Processing stage tracking
        self.current_stage = ProcessingStage.UPLOADED
        self.processing_history: List[Dict[str, Any]] = []
        
        # Core content (populated by extractor)
        self.text_md = ""  # Markdown formatted text from docling
        self.text_plain = ""  # Plain text fallback
        self.extraction_metadata: Optional[ExtractionMetadata] = None
        
        # Classification results (populated by classifier)
        self.document_type = DocumentType.UNKNOWN
        self.classification_result: Optional[ClassificationResult] = None
        
        # Entity data (populated by parser)
        self.entities_present: Optional[EntityData] = None
        
        # Analysis results (populated by analyzer)
        self.analysis_result: Optional[AnalysisResult] = None
        
        # Processing errors and warnings
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Additional metadata
        self.tags: List[str] = []
        self.notes: str = ""
        
        # Add initial processing entry
        self._add_processing_entry("Document initialized")
    
    def _add_processing_entry(self, action: str, details: Optional[Dict] = None):
        """Add an entry to processing history."""
        entry = {
            'timestamp': datetime.now(),
            'stage': self.current_stage.value,
            'action': action,
            'details': details or {}
        }
        self.processing_history.append(entry)
        self.updated_at = datetime.now()
    
    def set_extraction_data(self, text_md: str, text_plain: str = "", metadata: Optional[ExtractionMetadata] = None):
        """
        Set text extraction data.
        
        Args:
            text_md (str): Markdown formatted text
            text_plain (str): Plain text fallback
            metadata (ExtractionMetadata): Extraction metadata
        """
        self.text_md = text_md
        self.text_plain = text_plain or text_md
        self.extraction_metadata = metadata
        self.current_stage = ProcessingStage.TEXT_EXTRACTED
        self._add_processing_entry("Text extracted", {
            'method': metadata.extraction_method if metadata else 'unknown',
            'text_length': len(text_md),
            'pages': metadata.pages if metadata else None
        })
    
    def set_classification(self, classification: ClassificationResult):
        """
        Set document classification result.
        
        Args:
            classification (ClassificationResult): Classification result
        """
        self.document_type = classification.document_type
        self.classification_result = classification
        self.current_stage = ProcessingStage.CLASSIFIED
        self._add_processing_entry("Document classified", {
            'type': classification.document_type.value,
            'confidence': classification.confidence,
            'patterns_matched': len(classification.matched_patterns)
        })
    
    def set_entities(self, entities: EntityData):
        """
        Set extracted entity data.
        
        Args:
            entities (EntityData): Extracted entity data
        """
        self.entities_present = entities
        self.current_stage = ProcessingStage.ENTITIES_PARSED
        self._add_processing_entry("Entities extracted", {
            'gstin_count': len(entities.gstin_numbers),
            'dates_count': len(entities.dates),
            'amounts_count': len(entities.amounts),
            'sections_count': len(entities.legal_sections)
        })
    
    def set_analysis(self, analysis: AnalysisResult):
        """
        Set document analysis results.
        
        Args:
            analysis (AnalysisResult): Analysis results
        """
        self.analysis_result = analysis
        self.current_stage = ProcessingStage.ANALYZED
        self._add_processing_entry("Document analyzed", {
            'facts_count': len(analysis.facts),
            'issues_count': len(analysis.legal_issues),
            'timeline_events': len(analysis.timeline_events),
            'violations_count': len(analysis.procedural_violations)
        })
    
    def add_error(self, error: str, stage: Optional[ProcessingStage] = None):
        """
        Add an error to the document.
        
        Args:
            error (str): Error message
            stage (ProcessingStage): Stage where error occurred
        """
        self.errors.append(error)
        self._add_processing_entry("Error occurred", {
            'error': error,
            'stage': stage.value if stage else self.current_stage.value
        })
    
    def add_warning(self, warning: str):
        """
        Add a warning to the document.
        
        Args:
            warning (str): Warning message
        """
        self.warnings.append(warning)
        self._add_processing_entry("Warning issued", {'warning': warning})
    
    def add_tag(self, tag: str):
        """Add a tag to the document."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of document processing.
        
        Returns:
            Dict containing processing summary
        """
        return {
            'file_name': self.file_name,
            'current_stage': self.current_stage.value,
            'document_type': self.document_type.value,
            'has_text': bool(self.text_md),
            'has_entities': self.entities_present is not None,
            'has_analysis': self.analysis_result is not None,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'processing_steps': len(self.processing_history),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_entity_summary(self) -> Dict[str, Any]:
        """
        Get a summary of extracted entities.
        
        Returns:
            Dict containing entity summary
        """
        if not self.entities_present:
            return {}
        
        return {
            'gstin_numbers': self.entities_present.gstin_numbers,
            'total_dates': len(self.entities_present.dates),
            'total_amounts': len(self.entities_present.amounts),
            'legal_sections': self.entities_present.legal_sections,
            'form_numbers': self.entities_present.form_numbers,
            'case_numbers': self.entities_present.case_numbers,
            'summary': self.entities_present.summary
        }
    
    def is_processed(self) -> bool:
        """Check if document has been fully processed."""
        return self.current_stage in [ProcessingStage.ANALYZED, ProcessingStage.COMPLETED]
    
    def has_errors(self) -> bool:
        """Check if document has any errors."""
        return len(self.errors) > 0
    
    def get_text_preview(self, max_length: int = 500) -> str:
        """
        Get a preview of the document text.
        
        Args:
            max_length (int): Maximum length of preview
            
        Returns:
            str: Text preview
        """
        text = self.text_md or self.text_plain
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert document to dictionary representation.
        
        Returns:
            Dict representation of the document
        """
        return {
            'file_path': self.file_path,
            'file_name': self.file_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'current_stage': self.current_stage.value,
            'document_type': self.document_type.value,
            'text_md': self.text_md,
            'text_plain': self.text_plain,
            'extraction_metadata': self.extraction_metadata.__dict__ if self.extraction_metadata else None,
            'classification_result': self.classification_result.__dict__ if self.classification_result else None,
            'entities_present': self.entities_present.__dict__ if self.entities_present else None,
            'analysis_result': self.analysis_result.__dict__ if self.analysis_result else None,
            'errors': self.errors,
            'warnings': self.warnings,
            'tags': self.tags,
            'notes': self.notes,
            'processing_history': self.processing_history
        }
    
    def __str__(self) -> str:
        """String representation of the document."""
        return f"Document({self.file_name}, {self.document_type.value}, {self.current_stage.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the document."""
        return (f"Document(file_path='{self.file_path}', "
                f"type={self.document_type.value}, "
                f"stage={self.current_stage.value}, "
                f"errors={len(self.errors)}, "
                f"warnings={len(self.warnings)})")
