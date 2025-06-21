"""
GST Law Co-pilot - Main CLI Entry Point

Command-line tool to analyze GST legal documents and generate draft affidavits.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))

from document_processor import DocumentExtractor, DocumentClassifier, EntityParser
from analyzer import ChronologyBuilder


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
        required=True,
        help='Input document files (PDF, TXT)'
    )
    
    parser.add_argument(
        '--output', 
        required=True,
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
        
        # Step 1: Extract text from documents
        if args.verbose:
            print("\n1. Extracting text from documents...")
        
        extracted_documents = []
        for doc_path in args.documents:
            if args.verbose:
                print(f"   Processing: {doc_path}")
            result = extractor.extract_text(doc_path)
            extracted_documents.append(result)
        
        # Step 2: Classify documents
        if args.verbose:
            print("\n2. Classifying document types...")
        
        classifications = classifier.classify_multiple(extracted_documents)
        
        if args.verbose:
            for i, classification in enumerate(classifications):
                doc_type = classification['document_type'].value
                confidence = classification['confidence']
                print(f"   Document {i+1}: {doc_type} (confidence: {confidence:.2f})")
        
        # Step 3: Extract entities
        if args.verbose:
            print("\n3. Extracting entities...")
        
        all_entities = []
        for doc in extracted_documents:
            entities = parser_entity.parse_entities(doc['text'])
            all_entities.append(entities)
        
        if args.verbose:
            total_dates = sum(len(e.get('dates', [])) for e in all_entities)
            total_amounts = sum(len(e.get('amounts', [])) for e in all_entities)
            total_gstin = sum(len(e.get('gstin_numbers', [])) for e in all_entities)
            print(f"   Found: {total_dates} dates, {total_amounts} amounts, {total_gstin} GSTIN numbers")
        
        # Step 4: Build chronology
        if args.verbose:
            print("\n4. Building chronology...")
        
        chronology = chronology_builder.build_chronology(classifications, all_entities)
        
        if args.verbose:
            print(f"   Created timeline with {chronology['total_events']} events")
            analysis = chronology.get('timeline_analysis', {})
            if analysis.get('procedural_gaps'):
                print(f"   Identified {len(analysis['procedural_gaps'])} procedural gaps")
        
        # Step 5: Generate affidavit (placeholder for now)
        if args.verbose:
            print("\n5. Generating affidavit draft...")
        
        # For now, create a simple text output
        output_content = generate_basic_affidavit(classifications, all_entities, chronology)
        
        # Write output (as text file for now, will be DOCX later)
        output_path = args.output.replace('.docx', '.txt')  # Temporary text output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"\n✅ Analysis complete! Draft affidavit saved to: {output_path}")
        
        # Print summary
        print("\n📊 SUMMARY:")
        print(f"   Documents processed: {len(args.documents)}")
        print(f"   Events in timeline: {chronology['total_events']}")
        
        doc_summary = classifier.get_document_summary(classifications)
        print(f"   Document types found: {len(doc_summary['document_types'])}")
        for doc_type, count in doc_summary['document_types'].items():
            print(f"     - {doc_type}: {count}")
        
        analysis = chronology.get('timeline_analysis', {})
        if analysis.get('procedural_gaps'):
            print(f"   ⚠️  Procedural gaps identified: {len(analysis['procedural_gaps'])}")
            for gap in analysis['procedural_gaps']:
                print(f"     - {gap}")
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


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


def get_primary_gstin(entities_list: List) -> str:
    """Extract primary GSTIN from entities."""
    for entities in entities_list:
        gstin_numbers = entities.get('gstin_numbers', [])
        if gstin_numbers:
            return gstin_numbers[0]
    return "[GSTIN to be specified]"


def generate_facts_section(classifications: List, entities_list: List) -> str:
    """Generate statement of facts section."""
    facts = []
    
    # Collect key facts from documents
    total_amounts = []
    tax_periods = []
    sections = []
    
    for entities in entities_list:
        total_amounts.extend(entities.get('amounts', []))
        tax_periods.extend(entities.get('tax_periods', []))
        sections.extend(entities.get('legal_sections', []))
    
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


def generate_legal_grounds(classifications: List, entities_list: List) -> str:
    """Generate legal grounds section."""
    grounds = []
    
    # Check for common procedural issues
    doc_types = [c['document_type'].value for c in classifications]
    
    if 'show_cause_notice' in doc_types and 'company_reply' not in doc_types:
        grounds.append("1. Violation of principles of natural justice - no opportunity to reply")
    
    if 'adjudication_order' in doc_types:
        grounds.append("2. The impugned order is passed without proper consideration of submissions")
    
    grounds.append("3. [Additional legal grounds to be specified based on case analysis]")
    grounds.append("4. The order is liable to be set aside on grounds of procedural impropriety")
    
    return '\n'.join(grounds)


if __name__ == "__main__":
    main()
