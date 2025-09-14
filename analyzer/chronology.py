"""
Chronology Builder Module

Builds chronological timeline of events from GST legal documents.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from models.document import Document, DocumentType


class ChronologyBuilder:
    """Build chronological timeline from classified documents and extracted entities."""
    
    def __init__(self):
        self.event_priority = {
            DocumentType.SHOW_CAUSE_NOTICE: 1,
            DocumentType.ADJUDICATION_ORDER: 2,
            DocumentType.APPEAL_ORDER: 3,
            DocumentType.TRIBUNAL_ORDER: 4,
            DocumentType.CORRESPONDENCE: 5,
            DocumentType.UNKNOWN: 6
        }
    
    def build_chronology(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Build chronological timeline from Document objects.
        
        Args:
            documents: List of Document objects after entity parsing
            
        Returns:
            Dict containing chronological timeline and analysis
        """
        # Sort documents by doc_action_date
        sorted_documents = self._sort_documents_by_date(documents)
        
        # Create events from sorted documents
        events = []
        for i, doc in enumerate(sorted_documents):
            event = self._create_event_from_document(doc, i)
            events.append(event)
        
        # Analyze timeline for gaps and issues
        timeline_analysis = self._analyze_timeline_from_documents(sorted_documents)
        
        return {
            'sorted_documents': sorted_documents,
            'events': events,
            'timeline_analysis': timeline_analysis,
            'total_events': len(events),
            'date_range': self._get_date_range_from_documents(sorted_documents),
            'document_sequence': self._get_document_sequence_from_documents(sorted_documents)
        }
    
    def _sort_documents_by_date(self, documents: List[Document]) -> List[Document]:
        """
        Sort documents by doc_action_date.
        
        Args:
            documents: List of Document objects
            
        Returns:
            Sorted list of Document objects
        """
        # Separate documents with valid dates and unknown dates
        dated_docs = []
        undated_docs = []
        
        for doc in documents:
            if doc.doc_action_date and doc.doc_action_date.lower() != "unknown":
                dated_docs.append(doc)
            else:
                undated_docs.append(doc)
        
        # Sort dated documents by action_date
        # Parse dates in DD-MM-YYYY format for sorting
        def parse_date(date_str):
            try:
                parts = date_str.split('-')
                if len(parts) == 3:
                    day, month, year = parts
                    return datetime(int(year), int(month), int(day))
            except:
                pass
            return datetime.min
        
        dated_docs.sort(key=lambda x: parse_date(x.doc_action_date))
        
        # Sort undated documents by document type priority
        undated_docs.sort(key=lambda x: self.event_priority.get(x.document_type, 99))
        
        # Return dated documents first, then undated
        return dated_docs + undated_docs
    
    def _create_event_from_document(self, doc: Document, index: int) -> Dict[str, Any]:
        """
        Create an event dictionary from a Document object.
        
        Args:
            doc: Document object
            index: Index in the sorted list
            
        Returns:
            Event dictionary
        """
        return {
            'date': doc.doc_action_date if doc.doc_action_date else "Unknown",
            'event_summary': doc.doc_event_summary if doc.doc_event_summary else "No summary available",
            'document_type': doc.document_type.value,
            'file_name': doc.file_name,
            'event_type': self._get_event_type(doc.document_type),
            'index': index + 1,
            'has_date': doc.doc_action_date and doc.doc_action_date.lower() != "unknown",
            'entities_summary': doc.get_entity_summary() if doc.entities_present else {}
        }
    
    def _analyze_timeline_from_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Analyze timeline for gaps and procedural issues using Document objects.
        
        Args:
            documents: Sorted list of Document objects
            
        Returns:
            Analysis dictionary
        """
        analysis = {
            'total_documents': len(documents),
            'dated_documents': len([d for d in documents if d.doc_action_date and d.doc_action_date.lower() != "unknown"]),
            'undated_documents': len([d for d in documents if not d.doc_action_date or d.doc_action_date.lower() == "unknown"]),
            'procedural_gaps': [],
            'timeline_issues': [],
            'document_types_present': [],
            'missing_document_types': []
        }
        
        # Identify document types present
        present_types = set(doc.document_type for doc in documents)
        analysis['document_types_present'] = [dt.value for dt in present_types if dt != DocumentType.UNKNOWN]
        
        # Check for common procedural gaps
        doc_types = [doc.document_type for doc in documents]
        
        if DocumentType.SHOW_CAUSE_NOTICE in present_types:
            # Check if there's a reply after SCN
            scn_index = next((i for i, dt in enumerate(doc_types) if dt == DocumentType.SHOW_CAUSE_NOTICE), -1)
            has_reply_after = any(dt == DocumentType.CORRESPONDENCE for dt in doc_types[scn_index+1:]) if scn_index >= 0 else False
            
            if not has_reply_after:
                analysis['procedural_gaps'].append("No reply found after Show Cause Notice")
        
        if DocumentType.ADJUDICATION_ORDER in present_types:
            # Check if there was a notice before the order
            order_index = next((i for i, dt in enumerate(doc_types) if dt == DocumentType.ADJUDICATION_ORDER), -1)
            has_notice_before = any(dt == DocumentType.SHOW_CAUSE_NOTICE for dt in doc_types[:order_index]) if order_index >= 0 else False
            
            if not has_notice_before:
                analysis['timeline_issues'].append("Adjudication Order without prior Show Cause Notice")
        
        return analysis
    
    def _get_date_range_from_documents(self, documents: List[Document]) -> Dict[str, Optional[str]]:
        """
        Get the date range from Document objects.
        
        Args:
            documents: List of Document objects
            
        Returns:
            Date range dictionary
        """
        dated_docs = [doc for doc in documents if doc.doc_action_date and doc.doc_action_date.lower() != "unknown"]
        
        if not dated_docs:
            return {'start_date': None, 'end_date': None}
        
        return {
            'start_date': dated_docs[0].doc_action_date,  # First in sorted list
            'end_date': dated_docs[-1].doc_action_date    # Last in sorted list
        }
    
    def _get_document_sequence_from_documents(self, documents: List[Document]) -> List[str]:
        """
        Get sequence of document types from Document objects.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of document type values
        """
        return [doc.document_type.value for doc in documents]
    
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
            DocumentType.ADJUDICATION_ORDER: "Order Passed",
            DocumentType.APPEAL_ORDER: "Appeal Filed",
            DocumentType.TRIBUNAL_ORDER: "Tribunal Decision",
            DocumentType.CORRESPONDENCE: "Communication",
            DocumentType.UNKNOWN: "Document Received"
        }
        return event_mapping.get(doc_type, "Unknown Event")
    
    def _generate_event_description(self, doc_type: DocumentType, entities: Dict[str, Any]) -> str:
        """Generate descriptive text for the event."""
        base_descriptions = {
            DocumentType.SHOW_CAUSE_NOTICE: "Show Cause Notice issued",
            DocumentType.ADJUDICATION_ORDER: "Adjudication order passed",
            DocumentType.APPEAL_ORDER: "Appeal filed",
            DocumentType.TRIBUNAL_ORDER: "Tribunal order issued",
            DocumentType.CORRESPONDENCE: "Official correspondence",
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
            DocumentType.ADJUDICATION_ORDER
        }
        missing_types = expected_types - present_types
        analysis['missing_document_types'] = [dt.value for dt in missing_types]
        
        # Check for procedural gaps
        if DocumentType.SHOW_CAUSE_NOTICE in present_types:
            # Check if there's correspondence (which could be a reply) after SCN
            has_correspondence = DocumentType.CORRESPONDENCE in present_types
            if not has_correspondence:
                analysis['procedural_gaps'].append("No reply/correspondence found for Show Cause Notice")
        
        if DocumentType.CORRESPONDENCE in present_types and DocumentType.ADJUDICATION_ORDER not in present_types:
            analysis['procedural_gaps'].append("No adjudication order found after correspondence")
        
        # Check timeline issues for dated events
        dated_events = [e for e in events if e.get('normalized_date')]
        if len(dated_events) > 1:
            for i in range(1, len(dated_events)):
                prev_event = dated_events[i-1]
                curr_event = dated_events[i]
                
                # Check if order came before notice (timeline issue)
                if (prev_event['document_type'] == DocumentType.ADJUDICATION_ORDER and 
                    curr_event['document_type'] == DocumentType.SHOW_CAUSE_NOTICE):
                    analysis['timeline_issues'].append("Order appears to precede Show Cause Notice")
        
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
        
        chronology_text = "CHRONOLOGY OF EVENTS:\n"
        chronology_text += "=" * 60 + "\n\n"
        
        # Display events sorted by date with event summaries
        for event in events:
            date_str = event.get('date', 'Date not specified')
            event_summary = event.get('event_summary', 'No summary available')
            file_name = event.get('file_name', 'Unknown file')
            doc_type = event.get('document_type', 'unknown')
            
            chronology_text += f"{event['index']}. Date: {date_str}\n"
            chronology_text += f"   Document: {file_name} ({doc_type})\n"
            chronology_text += f"   Summary: {event_summary}\n"
            
            # Add entity details if available
            entities = event.get('entities_summary', {})
            if entities:
                if entities.get('gstin_numbers'):
                    chronology_text += f"   GSTIN: {', '.join(entities['gstin_numbers'][:2])}\n"
                if entities.get('legal_sections'):
                    chronology_text += f"   Sections: {', '.join(entities['legal_sections'][:3])}\n"
            
            chronology_text += "\n"
        
        # Add date range
        date_range = chronology.get('date_range', {})
        if date_range.get('start_date') and date_range.get('end_date'):
            chronology_text += f"Timeline Period: {date_range['start_date']} to {date_range['end_date']}\n\n"
        
        # Add analysis summary
        analysis = chronology.get('timeline_analysis', {})
        if analysis:
            chronology_text += "TIMELINE ANALYSIS:\n"
            chronology_text += "-" * 40 + "\n"
            chronology_text += f"Total Documents: {analysis.get('total_documents', 0)}\n"
            chronology_text += f"Documents with Dates: {analysis.get('dated_documents', 0)}\n"
            chronology_text += f"Documents without Dates: {analysis.get('undated_documents', 0)}\n"
            
            if analysis.get('procedural_gaps'):
                chronology_text += "\nProcedural Gaps Identified:\n"
                for gap in analysis['procedural_gaps']:
                    chronology_text += f"• {gap}\n"
            
            if analysis.get('timeline_issues'):
                chronology_text += "\nTimeline Issues:\n"
                for issue in analysis['timeline_issues']:
                    chronology_text += f"• {issue}\n"
        
        return chronology_text
