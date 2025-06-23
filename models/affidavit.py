"""
Affidavit Data Model

Represents a generated affidavit document with all its sections and metadata.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field


class AffidavitStatus(Enum):
    """Enumeration of affidavit generation statuses."""
    DRAFT = "draft"
    GENERATED = "generated"
    REVIEWED = "reviewed"
    FINALIZED = "finalized"
    SUBMITTED = "submitted"


class AffidavitType(Enum):
    """Enumeration of affidavit types."""
    REPLY_TO_SCN = "reply_to_scn"
    APPEAL_AFFIDAVIT = "appeal_affidavit"
    WRIT_PETITION = "writ_petition"
    TRIBUNAL_APPEAL = "tribunal_appeal"
    GENERAL = "general"


@dataclass
class AffiantDetails:
    """Details of the person making the affidavit."""
    name: str = ""
    designation: str = ""
    company: str = ""
    address: str = ""
    gstin: str = ""
    contact_details: Dict[str, str] = field(default_factory=dict)


@dataclass
class CourtDetails:
    """Details of the court where affidavit will be filed."""
    court_name: str = ""
    case_number: str = ""
    case_title: str = ""
    filing_date: Optional[datetime] = None
    jurisdiction: str = ""


@dataclass
class AffidavitSection:
    """Individual section of the affidavit."""
    section_number: int
    section_title: str
    content: str
    subsections: List[str] = field(default_factory=list)
    legal_references: List[str] = field(default_factory=list)
    supporting_documents: List[str] = field(default_factory=list)


class Affidavit:
    """
    Represents a complete affidavit document.
    
    This model contains all sections of an affidavit and metadata
    about its generation and current status.
    """
    
    def __init__(self, affidavit_id: str, case_id: str):
        """
        Initialize a new Affidavit instance.
        
        Args:
            affidavit_id (str): Unique identifier for the affidavit
            case_id (str): ID of the case this affidavit belongs to
        """
        # Basic affidavit information
        self.affidavit_id = affidavit_id
        self.case_id = case_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Affidavit metadata
        self.status = AffidavitStatus.DRAFT
        self.affidavit_type = AffidavitType.GENERAL
        self.title = ""
        self.version = 1
        
        # Parties involved
        self.affiant_details: Optional[AffiantDetails] = None
        self.court_details: Optional[CourtDetails] = None
        
        # Affidavit structure (6 main sections)
        self.sections: List[AffidavitSection] = []
        self._initialize_sections()
        
        # Content tracking
        self.word_count = 0
        self.page_count = 0
        self.legal_references_count = 0
        
        # Generation metadata
        self.generation_log: List[Dict[str, Any]] = []
        self.source_documents: List[str] = []
        self.template_used: str = ""
        
        # Quality checks
        self.validation_results: Dict[str, Any] = {}
        self.completeness_score: float = 0.0
        
        # File information
        self.output_file_path: str = ""
        self.file_format: str = "docx"
        
        # Add initial log entry
        self._add_generation_log("Affidavit initialized")
    
    def _initialize_sections(self):
        """Initialize the standard 6 sections of an affidavit."""
        standard_sections = [
            (1, "Header and Affiant Details", ""),
            (2, "Chronology/List of Events", ""),
            (3, "Statement of Facts", ""),
            (4, "Points of Law and Grounds", ""),
            (5, "Relief Claimed", ""),
            (6, "Verification Clause and Notarization", "")
        ]
        
        for num, title, content in standard_sections:
            section = AffidavitSection(
                section_number=num,
                section_title=title,
                content=content
            )
            self.sections.append(section)
    
    def _add_generation_log(self, action: str, details: Optional[Dict] = None):
        """Add an entry to the generation log."""
        entry = {
            'timestamp': datetime.now(),
            'status': self.status.value,
            'action': action,
            'details': details or {}
        }
        self.generation_log.append(entry)
        self.updated_at = datetime.now()
    
    def set_affiant_details(self, affiant: AffiantDetails):
        """
        Set details of the affiant.
        
        Args:
            affiant (AffiantDetails): Affiant details
        """
        self.affiant_details = affiant
        self._add_generation_log("Affiant details set", {
            'name': affiant.name,
            'company': affiant.company,
            'gstin': affiant.gstin
        })
    
    def set_court_details(self, court: CourtDetails):
        """
        Set court details.
        
        Args:
            court (CourtDetails): Court details
        """
        self.court_details = court
        self._add_generation_log("Court details set", {
            'court_name': court.court_name,
            'case_number': court.case_number
        })
    
    def update_section(self, section_number: int, content: str, 
                      subsections: Optional[List[str]] = None,
                      legal_references: Optional[List[str]] = None):
        """
        Update content of a specific section.
        
        Args:
            section_number (int): Section number (1-6)
            content (str): Section content
            subsections (List[str]): Optional subsections
            legal_references (List[str]): Optional legal references
        """
        if 1 <= section_number <= len(self.sections):
            section = self.sections[section_number - 1]
            section.content = content
            if subsections:
                section.subsections = subsections
            if legal_references:
                section.legal_references = legal_references
            
            self._update_statistics()
            self._add_generation_log(f"Section {section_number} updated", {
                'section_title': section.section_title,
                'content_length': len(content),
                'subsections_count': len(section.subsections),
                'references_count': len(section.legal_references)
            })
    
    def add_source_document(self, document_path: str):
        """
        Add a source document reference.
        
        Args:
            document_path (str): Path to source document
        """
        if document_path not in self.source_documents:
            self.source_documents.append(document_path)
            self._add_generation_log("Source document added", {
                'document': document_path,
                'total_sources': len(self.source_documents)
            })
    
    def set_template(self, template_name: str):
        """
        Set the template used for generation.
        
        Args:
            template_name (str): Name of the template
        """
        self.template_used = template_name
        self._add_generation_log("Template set", {'template': template_name})
    
    def _update_statistics(self):
        """Update word count and other statistics."""
        total_words = 0
        total_references = 0
        
        for section in self.sections:
            if section.content:
                total_words += len(section.content.split())
            total_references += len(section.legal_references)
        
        self.word_count = total_words
        self.legal_references_count = total_references
        
        # Estimate page count (assuming ~250 words per page)
        self.page_count = max(1, (total_words + 249) // 250)
    
    def validate_completeness(self) -> Dict[str, Any]:
        """
        Validate completeness of the affidavit.
        
        Returns:
            Dict containing validation results
        """
        validation = {
            'is_complete': True,
            'missing_sections': [],
            'empty_sections': [],
            'missing_details': [],
            'score': 0.0
        }
        
        # Check affiant details
        if not self.affiant_details:
            validation['missing_details'].append('affiant_details')
            validation['is_complete'] = False
        
        # Check court details
        if not self.court_details:
            validation['missing_details'].append('court_details')
            validation['is_complete'] = False
        
        # Check sections
        for section in self.sections:
            if not section.content or section.content.strip() == "":
                validation['empty_sections'].append(section.section_title)
                validation['is_complete'] = False
        
        # Calculate completeness score
        total_checks = 8  # 6 sections + affiant + court details
        passed_checks = total_checks - len(validation['empty_sections']) - len(validation['missing_details'])
        validation['score'] = (passed_checks / total_checks) * 100
        
        self.validation_results = validation
        self.completeness_score = validation['score']
        
        return validation
    
    def mark_as_generated(self, output_path: str):
        """
        Mark affidavit as generated.
        
        Args:
            output_path (str): Path to generated file
        """
        self.status = AffidavitStatus.GENERATED
        self.output_file_path = output_path
        self._update_statistics()
        self._add_generation_log("Affidavit generated", {
            'output_path': output_path,
            'word_count': self.word_count,
            'page_count': self.page_count
        })
    
    def mark_as_reviewed(self, reviewer: str, comments: str = ""):
        """
        Mark affidavit as reviewed.
        
        Args:
            reviewer (str): Name of reviewer
            comments (str): Review comments
        """
        self.status = AffidavitStatus.REVIEWED
        self._add_generation_log("Affidavit reviewed", {
            'reviewer': reviewer,
            'comments': comments
        })
    
    def create_new_version(self) -> 'Affidavit':
        """
        Create a new version of the affidavit.
        
        Returns:
            New Affidavit instance with incremented version
        """
        new_affidavit = Affidavit(f"{self.affidavit_id}_v{self.version + 1}", self.case_id)
        new_affidavit.version = self.version + 1
        new_affidavit.affidavit_type = self.affidavit_type
        new_affidavit.title = self.title
        new_affidavit.affiant_details = self.affiant_details
        new_affidavit.court_details = self.court_details
        new_affidavit.template_used = self.template_used
        new_affidavit.source_documents = self.source_documents.copy()
        
        # Copy sections
        for i, section in enumerate(self.sections):
            new_affidavit.sections[i].content = section.content
            new_affidavit.sections[i].subsections = section.subsections.copy()
            new_affidavit.sections[i].legal_references = section.legal_references.copy()
        
        return new_affidavit
    
    def get_section_by_number(self, section_number: int) -> Optional[AffidavitSection]:
        """
        Get a section by its number.
        
        Args:
            section_number (int): Section number (1-6)
            
        Returns:
            AffidavitSection or None if not found
        """
        if 1 <= section_number <= len(self.sections):
            return self.sections[section_number - 1]
        return None
    
    def get_generation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of affidavit generation.
        
        Returns:
            Dict containing generation summary
        """
        return {
            'affidavit_id': self.affidavit_id,
            'case_id': self.case_id,
            'status': self.status.value,
            'type': self.affidavit_type.value,
            'version': self.version,
            'word_count': self.word_count,
            'page_count': self.page_count,
            'legal_references_count': self.legal_references_count,
            'completeness_score': self.completeness_score,
            'source_documents_count': len(self.source_documents),
            'template_used': self.template_used,
            'output_file': self.output_file_path,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_content_preview(self, max_length: int = 1000) -> str:
        """
        Get a preview of the affidavit content.
        
        Args:
            max_length (int): Maximum length of preview
            
        Returns:
            str: Content preview
        """
        preview_parts = []
        current_length = 0
        
        for section in self.sections:
            if section.content and current_length < max_length:
                section_preview = f"\n{section.section_number}. {section.section_title}\n"
                section_preview += section.content[:min(200, max_length - current_length)]
                
                preview_parts.append(section_preview)
                current_length += len(section_preview)
        
        preview = "".join(preview_parts)
        if len(preview) >= max_length:
            preview += "..."
        
        return preview
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert affidavit to dictionary representation.
        
        Returns:
            Dict representation of the affidavit
        """
        return {
            'affidavit_id': self.affidavit_id,
            'case_id': self.case_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status.value,
            'affidavit_type': self.affidavit_type.value,
            'title': self.title,
            'version': self.version,
            'affiant_details': self.affiant_details.__dict__ if self.affiant_details else None,
            'court_details': self.court_details.__dict__ if self.court_details else None,
            'sections': [
                {
                    'section_number': s.section_number,
                    'section_title': s.section_title,
                    'content': s.content,
                    'subsections': s.subsections,
                    'legal_references': s.legal_references,
                    'supporting_documents': s.supporting_documents
                }
                for s in self.sections
            ],
            'word_count': self.word_count,
            'page_count': self.page_count,
            'legal_references_count': self.legal_references_count,
            'generation_log': self.generation_log,
            'source_documents': self.source_documents,
            'template_used': self.template_used,
            'validation_results': self.validation_results,
            'completeness_score': self.completeness_score,
            'output_file_path': self.output_file_path,
            'file_format': self.file_format
        }
    
    def __str__(self) -> str:
        """String representation of the affidavit."""
        return f"Affidavit({self.affidavit_id}, v{self.version}, {self.status.value}, {self.word_count} words)"
    
    def __repr__(self) -> str:
        """Detailed string representation of the affidavit."""
        return (f"Affidavit(id='{self.affidavit_id}', "
                f"case_id='{self.case_id}', "
                f"status={self.status.value}, "
                f"version={self.version}, "
                f"completeness={self.completeness_score:.1f}%)")
