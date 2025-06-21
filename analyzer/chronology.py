"""
Chronology Builder Module

Builds chronological timeline of events from GST legal documents.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from document_processor.classifier import DocumentType


class ChronologyBuilder:
    """Build chronological timeline from classified documents and extracted entities."""
    
    def __init__(self):
        self.event_priority = {
            DocumentType.SHOW_CAUSE_NOTICE: 1,
            DocumentType.COMPANY_REPLY: 2,
            DocumentType.HEARING_MINUTES: 3,
            DocumentType.ADJUDICATION_ORDER: 4,
            DocumentType.APPEAL_ORDER: 5,
            DocumentType.TRIBUNAL_ORDER: 6,
            DocumentType.HIGH_COURT_ORDER: 7,
            DocumentType.RECTIFICATION_APPLICATION: 8,
            DocumentType.CORRESPONDENCE: 9,
            DocumentType.SUPPORTING_EVIDENCE: 10,
            DocumentType.UNKNOWN: 11
        }
    
    def build_chronology(self, classified_documents: List[Dict[str, Any]], 
                        extracted_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build chronological timeline from documents and entities.
        
        Args:
            classified_documents: List of classified document results
            extracted_entities: List of extracted entity results
            
        Returns:
            Dict containing chronological timeline and analysis
        """
        events = []
        
        # Process each document to create events
        for i, (classification, entities) in enumerate(zip(classified_documents, extracted_entities)):
            doc_events = self._extract_events_from_document(classification, entities, i)
            events.extend(doc_events)
        
        # Sort events chronologically
        sorted_events = self._sort_events(events)
        
        # Identify gaps and issues
        timeline_analysis = self._analyze_timeline(sorted_events)
        
        return {
            'events': sorted_events,
            'timeline_analysis': timeline_analysis,
            'total_events': len(sorted_events),
            'date_range': self._get_date_range(sorted_events),
            'document_sequence': self._get_document_sequence(sorted_events)
        }
    
    def _extract_events_from_document(self, classification: Dict[str, Any], 
                                    entities: Dict[str, Any], doc_index: int) -> List[Dict[str, Any]]:
        """Extract events from a single document."""
        events = []
        doc_type = classification.get('document_type')
        source_metadata = classification.get('source_metadata', {})
        
        # Get dates from entities
        dates = entities.get('dates', [])
        
        if not dates:
            # Create event without specific date
            events.append({
                'date': None,
                'normalized_date': None,
                'event_type': self._get_event_type(doc_type),
                'document_type': doc_type,
                'description': self._generate_event_description(doc_type, entities),
                'document_index': doc_index,
                'source_file': source_metadata.get('file_path', f'Document_{doc_index}'),
                'entities': entities,
                'priority': self.event_priority.get(doc_type, 99)
            })
        else:
            # Create events for each date found
            for date_info in dates:
                events.append({
                    'date': date_info.get('original'),
                    'normalized_date': date_info.get('normalized'),
                    'event_type': self._get_event_type(doc_type),
                    'document_type': doc_type,
                    'description': self._generate_event_description(doc_type, entities),
                    'document_index': doc_index,
                    'source_file': source_metadata.get('file_path', f'Document_{doc_index}'),
                    'entities': entities,
                    'priority': self.event_priority.get(doc_type, 99)
                })
        
        return events
    
    def _get_event_type(self, doc_type: DocumentType) -> str:
        """Map document type to event type."""
        event_mapping = {
            DocumentType.SHOW_CAUSE_NOTICE: "Notice Issued",
            DocumentType.COMPANY_REPLY: "Reply Submitted",
            DocumentType.HEARING_MINUTES: "Hearing Conducted",
            DocumentType.ADJUDICATION_ORDER: "Order Passed",
            DocumentType.APPEAL_ORDER: "Appeal Filed",
            DocumentType.TRIBUNAL_ORDER: "Tribunal Decision",
            DocumentType.HIGH_COURT_ORDER: "Court Order",
            DocumentType.RECTIFICATION_APPLICATION: "Rectification Applied",
            DocumentType.CORRESPONDENCE: "Communication",
            DocumentType.SUPPORTING_EVIDENCE: "Evidence Submitted",
            DocumentType.UNKNOWN: "Document Received"
        }
        return event_mapping.get(doc_type, "Unknown Event")
    
    def _generate_event_description(self, doc_type: DocumentType, entities: Dict[str, Any]) -> str:
        """Generate descriptive text for the event."""
        base_descriptions = {
            DocumentType.SHOW_CAUSE_NOTICE: "Show Cause Notice issued",
            DocumentType.COMPANY_REPLY: "Reply submitted to authorities",
            DocumentType.HEARING_MINUTES: "Personal hearing conducted",
            DocumentType.ADJUDICATION_ORDER: "Adjudication order passed",
            DocumentType.APPEAL_ORDER: "Appeal filed",
            DocumentType.TRIBUNAL_ORDER: "Tribunal order issued",
            DocumentType.HIGH_COURT_ORDER: "High Court order passed",
            DocumentType.RECTIFICATION_APPLICATION: "Rectification application filed",
            DocumentType.CORRESPONDENCE: "Official correspondence",
            DocumentType.SUPPORTING_EVIDENCE: "Supporting evidence provided",
            DocumentType.UNKNOWN: "Document processed"
        }
        
        description = base_descriptions.get(doc_type, "Event occurred")
        
        # Add relevant details from entities
        form_numbers = entities.get('form_numbers', [])
        amounts = entities.get('amounts', [])
        sections = entities.get('legal_sections', [])
        
        if form_numbers:
            description += f" (Form: {', '.join(form_numbers)})"
        
        if amounts and len(amounts) > 0:
            amount_values = [amt.get('original', '') for amt in amounts[:2]]  # Show first 2 amounts
            description += f" involving amounts: {', '.join(amount_values)}"
        
        if sections:
            description += f" under Section(s): {', '.join(sections[:3])}"  # Show first 3 sections
        
        return description
    
    def _sort_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort events chronologically."""
        # Separate events with and without dates
        dated_events = [e for e in events if e.get('normalized_date')]
        undated_events = [e for e in events if not e.get('normalized_date')]
        
        # Sort dated events by date
        dated_events.sort(key=lambda x: x['normalized_date'])
        
        # Sort undated events by priority and document index
        undated_events.sort(key=lambda x: (x['priority'], x['document_index']))
        
        # Combine: dated events first, then undated events
        return dated_events + undated_events
    
    def _analyze_timeline(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze timeline for gaps and procedural issues."""
        analysis = {
            'total_events': len(events),
            'dated_events': len([e for e in events if e.get('normalized_date')]),
            'undated_events': len([e for e in events if not e.get('normalized_date')]),
            'procedural_gaps': [],
            'timeline_issues': [],
            'document_types_present': [],
            'missing_document_types': []
        }
        
        # Identify document types present
        present_types = set(e['document_type'] for e in events)
        analysis['document_types_present'] = [dt.value for dt in present_types if dt != DocumentType.UNKNOWN]
        
        # Identify common missing document types
        expected_types = {
            DocumentType.SHOW_CAUSE_NOTICE,
            DocumentType.COMPANY_REPLY,
            DocumentType.ADJUDICATION_ORDER
        }
        missing_types = expected_types - present_types
        analysis['missing_document_types'] = [dt.value for dt in missing_types]
        
        # Check for procedural gaps
        if DocumentType.SHOW_CAUSE_NOTICE in present_types and DocumentType.COMPANY_REPLY not in present_types:
            analysis['procedural_gaps'].append("No reply found for Show Cause Notice")
        
        if DocumentType.COMPANY_REPLY in present_types and DocumentType.ADJUDICATION_ORDER not in present_types:
            analysis['procedural_gaps'].append("No adjudication order found after reply")
        
        # Check timeline issues for dated events
        dated_events = [e for e in events if e.get('normalized_date')]
        if len(dated_events) > 1:
            for i in range(1, len(dated_events)):
                prev_event = dated_events[i-1]
                curr_event = dated_events[i]
                
                # Check if reply came before notice (timeline issue)
                if (prev_event['document_type'] == DocumentType.COMPANY_REPLY and 
                    curr_event['document_type'] == DocumentType.SHOW_CAUSE_NOTICE):
                    analysis['timeline_issues'].append("Reply appears to precede Show Cause Notice")
        
        return analysis
    
    def _get_date_range(self, events: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
        """Get the date range of events."""
        dated_events = [e for e in events if e.get('normalized_date')]
        
        if not dated_events:
            return {'start_date': None, 'end_date': None}
        
        dates = [e['normalized_date'] for e in dated_events]
        return {
            'start_date': min(dates),
            'end_date': max(dates)
        }
    
    def _get_document_sequence(self, events: List[Dict[str, Any]]) -> List[str]:
        """Get sequence of document types in chronological order."""
        return [e['document_type'].value for e in events]
    
    def generate_chronology_text(self, chronology: Dict[str, Any]) -> str:
        """Generate formatted chronology text for affidavit."""
        events = chronology.get('events', [])
        
        if not events:
            return "No chronological events could be determined from the available documents."
        
        chronology_text = "CHRONOLOGY OF EVENTS:\n\n"
        
        for i, event in enumerate(events, 1):
            date_str = event.get('date', 'Date not specified')
            event_type = event.get('event_type', 'Event')
            description = event.get('description', 'No description available')
            
            chronology_text += f"{i}. {date_str}: {event_type}\n"
            chronology_text += f"   {description}\n\n"
        
        # Add analysis summary
        analysis = chronology.get('timeline_analysis', {})
        if analysis.get('procedural_gaps'):
            chronology_text += "PROCEDURAL GAPS IDENTIFIED:\n"
            for gap in analysis['procedural_gaps']:
                chronology_text += f"• {gap}\n"
            chronology_text += "\n"
        
        return chronology_text
