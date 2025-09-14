"""
GST Law Co-pilot - Main CLI Entry Point

Command-line tool to analyze GST legal documents and generate draft affidavits.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List
from datetime import datetime

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))

from document_processor import DocumentExtractor, DocumentClassifier, EntityParser
from models.document import Document, DocumentType, ExtractionMetadata, ClassificationResult, EntityData
from analyzer.chronology import ChronologyBuilder


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="GST Law Co-pilot - Analyze GST legal documents and generate affidavits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --documents notice.pdf order.pdf --output affidavit.docx
  python main.py --documents *.pdf --output my_affidavit.docx
        """
    )
    
    parser.add_argument(
        '--documents', 
        nargs='+', 
        # required=True,
        default=['data/affidavits/affidavit_1/input/p1.pdf', 'data/affidavits/affidavit_1/input/p2.pdf', 'data/affidavits/affidavit_1/input/p3.pdf'],
        # default=['data/affidavits/affidavit_1/input/p1.pdf'],
        help='Input document files (PDF, TXT)'
    )
    
    parser.add_argument(
        '--output', 
        default="test_out.pdf",
        # required=True,
        help='Output affidavit file (DOCX format)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate input files
    for doc_path in args.documents:
        if not os.path.exists(doc_path):
            print(f"Error: File not found: {doc_path}")
            sys.exit(1)
    
    print("GST Law Co-pilot - Document Analysis Started")
    print(f"Processing {len(args.documents)} document(s)...")
    
    try:
        # Initialize processors
        extractor = DocumentExtractor()
        classifier = DocumentClassifier()
        parser_entity = EntityParser()
        chronology_builder = ChronologyBuilder()
        
        # Initialize Document models for each input file
        documents = []
        for doc_path in args.documents:
            doc = Document(doc_path)
            documents.append(doc)
        
        # Step 1: Extract text from documents
        if args.verbose:
            print("\n1. Extracting text from documents...")
        
        for i, doc in enumerate(documents):
            if args.verbose:
                print(f"   Processing: {doc.file_path}")
            
            # Extract text using the extractor
            result = extractor.extract_text(doc.file_path)
            
            # Create extraction metadata
            metadata = ExtractionMetadata(
                file_path=doc.file_path,
                file_type=result.get('file_type', 'pdf'),
                file_size=result.get('file_size'),
                pages=result.get('pages'),
                extraction_method=result.get('extraction_method', 'unknown'),
                extraction_issues=result.get('extraction_issues', []),
                processing_time=result.get('processing_time')
            )
            
            # Update document with extraction data
            doc.set_extraction_data(
                text_md=result.get('text', ''),
                text_plain=result.get('text', ''),
                metadata=metadata
            )
            
            if args.verbose:
                print(f"      ✓ Extracted {len(doc.text_md)} characters using {metadata.extraction_method}")
        
        # Step 2: Classify documents
        if args.verbose:
            print("\n2. Classifying document types...")
        
        # Prepare texts for classification
        texts_for_classification = []
        for doc in documents:
            texts_for_classification.append({'text': doc.text_plain})
        
        # Classify all documents
        classifications = classifier.classify_multiple(texts_for_classification)
        
        # Update each document with classification results
        for i, (doc, classification) in enumerate(zip(documents, classifications)):
            # Create ClassificationResult object
            classification_result = ClassificationResult(
                document_type=classification['document_type'],
                confidence=classification['confidence'],
                matched_patterns=classification.get('matched_patterns', []),
                classification_reason=classification.get('reason', '')
            )
            
            # Set classification in document
            doc.set_classification(classification_result)
            
            if args.verbose:
                doc_type = doc.document_type.value
                confidence = classification_result.confidence
                print(f"   Document {i+1} ({doc.file_name}): {doc_type} (confidence: {confidence:.2f})")
        
        # Step 3: Extract entities
        if args.verbose:
            print("\n3. Extracting entities...")
        
        for doc in documents:
            # Parse entities from document text
            entities = parser_entity.parse_entities(doc.text_plain)
            
            # Create EntityData object
            entity_data = EntityData(
                gstin_numbers=entities.get('gstin_numbers', []),
                dates=entities.get('dates', []),
                amounts=entities.get('amounts', []),
                legal_sections=entities.get('legal_sections', []),
                form_numbers=entities.get('form_numbers', []),
                case_numbers=entities.get('case_numbers', []),
                summary=entities.get('summary', {})
            )
            
            # Set entities in document
            doc.set_entities(entity_data)
            
            if args.verbose:
                print(f"   {doc.file_name}:")
                print(f"      - GSTIN numbers: {len(entity_data.gstin_numbers)}")
                print(f"      - Dates: {len(entity_data.dates)}")
                print(f"      - Amounts: {len(entity_data.amounts)}")
                print(f"      - Legal sections: {len(entity_data.legal_sections)}")
        
        # Calculate totals for summary
        if args.verbose:
            total_dates = sum(len(doc.entities_present.dates) for doc in documents if doc.entities_present)
            total_amounts = sum(len(doc.entities_present.amounts) for doc in documents if doc.entities_present)
            total_gstin = sum(len(doc.entities_present.gstin_numbers) for doc in documents if doc.entities_present)
            print(f"\n   Total entities found: {total_dates} dates, {total_amounts} amounts, {total_gstin} GSTIN numbers")
        
        # Step 4: Display document processing summary
        if args.verbose:
            print("\n4. Document Processing Summary:")
            print("=" * 60)
            for doc in documents:
                summary = doc.get_processing_summary()
                print(f"\n   Document: {summary['file_name']}")
                print(f"   Current Stage: {summary['current_stage']}")
                print(f"   Document Type: {summary['document_type']}")
                print(f"   Has Text: {summary['has_text']}")
                print(f"   Has Entities: {summary['has_entities']}")
                print(f"   Errors: {summary['error_count']}")
                print(f"   Warnings: {summary['warning_count']}")
                
                # Show entity summary if available
                if doc.entities_present:
                    entity_summary = doc.get_entity_summary()
                    if entity_summary.get('gstin_numbers'):
                        print(f"   GSTIN Numbers: {', '.join(entity_summary['gstin_numbers'][:3])}")
                    if entity_summary.get('legal_sections'):
                        print(f"   Legal Sections: {', '.join(entity_summary['legal_sections'][:5])}")
        
        # Step 5: Build chronology using Document objects
        if args.verbose:
            print("\n5. Building chronology...")
        
        # Build chronology from documents
        chronology = chronology_builder.build_chronology(documents)
        
        if args.verbose:
            print(f"   Documents sorted by action date")
            print(f"   Total events: {chronology['total_events']}")
            
            # Display chronology
            chronology_text = chronology_builder.generate_chronology_text(chronology)
            print("\n" + "=" * 60)
            print(chronology_text)
            print("=" * 60)
        
        print(f"\n✅ Analysis complete!")
        print(f"   Documents processed: {len(documents)}")
        print(f"   Chronology built with {chronology['total_events']} events")
        
        # Display final status
        print("\n📊 FINAL STATUS:")
        for doc in documents:
            status_line = f"   - {doc.file_name}: {doc.current_stage.value} | {doc.document_type.value}"
            if doc.doc_action_date and doc.doc_action_date != "unknown":
                status_line += f" | Date: {doc.doc_action_date}"
            print(status_line)
        
        # Return documents and chronology for further processing
        return documents, chronology
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    #     chronology = chronology_builder.build_chronology(classifications, all_entities)
        
    #     if args.verbose:
    #         print(f"   Created timeline with {chronology['total_events']} events")
    #         analysis = chronology.get('timeline_analysis', {})
    #         if analysis.get('procedural_gaps'):
    #             print(f"   Identified {len(analysis['procedural_gaps'])} procedural gaps")
        
    #     # Step 5: Generate affidavit (placeholder for now)
    #     if args.verbose:
    #         print("\n5. Generating affidavit draft...")
        
    #     # For now, create a simple text output
    #     output_content = generate_basic_affidavit(classifications, all_entities, chronology)
        
    #     # Write output (as text file for now, will be DOCX later)
    #     output_path = args.output.replace('.docx', '.txt')  # Temporary text output
    #     with open(output_path, 'w', encoding='utf-8') as f:
    #         f.write(output_content)
        
    #     print(f"\n✅ Analysis complete! Draft affidavit saved to: {output_path}")
        
    #     # Print summary
    #     print("\n📊 SUMMARY:")
    #     print(f"   Documents processed: {len(args.documents)}")
    #     print(f"   Events in timeline: {chronology['total_events']}")
        
    #     doc_summary = classifier.get_document_summary(classifications)
    #     print(f"   Document types found: {len(doc_summary['document_types'])}")
    #     for doc_type, count in doc_summary['document_types'].items():
    #         print(f"     - {doc_type}: {count}")
        
    #     analysis = chronology.get('timeline_analysis', {})
    #     if analysis.get('procedural_gaps'):
    #         print(f"   ⚠️  Procedural gaps identified: {len(analysis['procedural_gaps'])}")
    #         for gap in analysis['procedural_gaps']:
    #             print(f"     - {gap}")
        
    # except Exception as e:
    #     print(f"❌ Error during processing: {str(e)}")
    #     if args.verbose:
    #         import traceback
    #         traceback.print_exc()
        # sys.exit(1)


def generate_basic_affidavit(classifications: List, entities: List, chronology: dict) -> str:
    """Generate a basic affidavit draft (placeholder implementation)."""
    
    content = """AFFIDAVIT DRAFT
===============

Generated by GST Law Co-pilot
Date: {date}

1. HEADER AND AFFIANT DETAILS
-----------------------------
[To be filled with client details]
- Case Title: [To be specified]
- Affiant Name: [To be specified]
- Designation: [To be specified]
- Company GSTIN: {gstin}

2. CHRONOLOGY OF EVENTS
-----------------------
{chronology}

3. STATEMENT OF FACTS
--------------------
{facts}

4. POINTS OF LAW AND GROUNDS
---------------------------
{legal_grounds}

5. RELIEF CLAIMED
----------------
[To be specified based on case requirements]

6. VERIFICATION CLAUSE
---------------------
I, [Name], do hereby solemnly affirm and declare that the contents of the above affidavit are true and correct to the best of my knowledge and belief.

Place: [To be specified]
Date: [To be specified]

                                    [Signature]
                                    [Name]
                                    [Designation]

""".format(
        date=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        gstin=get_primary_gstin(entities),
        chronology=chronology_builder.generate_chronology_text(chronology) if 'chronology_builder' in globals() else "Chronology to be generated",
        facts=generate_facts_section(classifications, entities),
        legal_grounds=generate_legal_grounds(classifications, entities)
    )
    
    return content


def get_primary_gstin(documents: List[Document]) -> str:
    """Extract primary GSTIN from documents."""
    for doc in documents:
        if doc.entities_present and doc.entities_present.gstin_numbers:
            return doc.entities_present.gstin_numbers[0]
    return "[GSTIN to be specified]"


def generate_facts_section(documents: List[Document]) -> str:
    """Generate statement of facts section."""
    facts = []
    
    # Collect key facts from documents
    total_amounts = []
    tax_periods = []
    sections = []
    
    for doc in documents:
        if doc.entities_present:
            total_amounts.extend(doc.entities_present.amounts)
            # Extract tax periods from dates if available
            for date_info in doc.entities_present.dates:
                if isinstance(date_info, dict) and 'context' in date_info:
                    if 'tax period' in date_info['context'].lower():
                        tax_periods.append(date_info['date'])
            sections.extend(doc.entities_present.legal_sections)
    
    facts.append("1. The petitioner is a registered taxpayer under GST.")
    
    if tax_periods:
        unique_periods = list(set(tax_periods))
        facts.append(f"2. The dispute relates to tax period(s): {', '.join(unique_periods[:3])}")
    
    if total_amounts:
        facts.append(f"3. The matter involves disputed amounts as detailed in the documents.")
    
    if sections:
        unique_sections = list(set(sections))
        facts.append(f"4. The proceedings were initiated under Section(s): {', '.join(unique_sections[:3])}")
    
    facts.append("5. [Additional facts to be added based on specific case details]")
    
    return '\n'.join(facts)


def generate_legal_grounds(documents: List[Document]) -> str:
    """Generate legal grounds section."""
    grounds = []
    
    # Check for common procedural issues
    doc_types = [doc.document_type.value for doc in documents]
    
    if 'show_cause_notice' in doc_types and 'company_reply' not in doc_types:
        grounds.append("1. Violation of principles of natural justice - no opportunity to reply")
    
    if 'adjudication_order' in doc_types:
        grounds.append("2. The impugned order is passed without proper consideration of submissions")
    
    grounds.append("3. [Additional legal grounds to be specified based on case analysis]")
    grounds.append("4. The order is liable to be set aside on grounds of procedural impropriety")
    
    return '\n'.join(grounds)


if __name__ == "__main__":
    main()
