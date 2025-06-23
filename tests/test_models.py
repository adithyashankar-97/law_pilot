"""
Test script for data models integration

Demonstrates how the Document, Case, and Affidavit models work together
throughout the processing pipeline.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.document import Document, DocumentType, ExtractionMetadata, ClassificationResult, EntityData
from models.case import Case, CaseType, CaseAnalysis, Timeline
from models.affidavit import Affidavit, AffiantDetails, CourtDetails
from datetime import datetime


def test_document_pipeline():
    """Test Document model through the processing pipeline."""
    print("🧪 TESTING DOCUMENT MODEL PIPELINE")
    print("=" * 60)
    
    # 1. Initialize document
    doc = Document("data/affidavits/affidavit 1/input/p1.pdf")
    print(f"📄 Document initialized: {doc}")
    print(f"   Stage: {doc.current_stage.value}")
    print(f"   Processing history: {len(doc.processing_history)} entries")
    
    # 2. Simulate text extraction
    extraction_metadata = ExtractionMetadata(
        file_path=doc.file_path,
        file_type="pdf",
        pages=1,
        extraction_method="docling",
        processing_time=2.5
    )
    
    markdown_text = """## FORM GST DRC - 07
[See rule 100(1), 100(2), 100(3) & 142(5)]

## Summary of the order
Reference No: ZD3712230232850
GSTIN/ID: 37ADSPT7675HIZI
Name: VENKATA SIVARAMA KRISHNA TANGA

## Details of order
- (a) Order no: AD370823002450G
- (b) Order date: 30/12/2023
- (c) Financial year: 2017-2018
- (d) Tax period: Jul 2017 - Mar 2018
"""
    
    doc.set_extraction_data(markdown_text, markdown_text, extraction_metadata)
    print(f"✅ Text extracted: {len(doc.text_md)} characters")
    print(f"   Stage: {doc.current_stage.value}")
    print(f"   Method: {doc.extraction_metadata.extraction_method}")
    
    # 3. Simulate classification
    classification = ClassificationResult(
        document_type=DocumentType.ADJUDICATION_ORDER,
        confidence=0.85,
        matched_patterns=["DRC-07", "order.*date", "financial.*year"],
        classification_reason="Strong match with adjudication order patterns"
    )
    
    doc.set_classification(classification)
    print(f"✅ Document classified: {doc.document_type.value}")
    print(f"   Confidence: {doc.classification_result.confidence}")
    print(f"   Stage: {doc.current_stage.value}")
    
    # 4. Simulate entity extraction
    entities = EntityData(
        gstin_numbers=["37ADSPT7675HIZI"],
        dates=[
            {"original": "30/12/2023", "normalized": "2023-12-30", "type": "order_date"},
            {"original": "Jul 2017", "normalized": "2017-07-01", "type": "tax_period_start"}
        ],
        amounts=[],
        legal_sections=["100(1)", "100(2)", "100(3)", "142(5)"],
        form_numbers=["DRC-07"],
        case_numbers=["AD370823002450G"],
        summary={
            "total_gstin_numbers": 1,
            "total_dates": 2,
            "total_amounts": 0,
            "total_sections": 4,
            "total_forms": 1,
            "total_cases": 1
        }
    )
    
    doc.set_entities(entities)
    print(f"✅ Entities extracted: {doc.current_stage.value}")
    print(f"   GSTIN: {entities.gstin_numbers}")
    print(f"   Dates: {len(entities.dates)}")
    print(f"   Legal sections: {entities.legal_sections}")
    
    # 5. Get document summary
    summary = doc.get_processing_summary()
    print(f"\n📊 DOCUMENT SUMMARY:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    return doc


def test_case_pipeline():
    """Test Case model with multiple documents."""
    print("\n🧪 TESTING CASE MODEL PIPELINE")
    print("=" * 60)
    
    # 1. Initialize case
    case = Case("CASE_001", "VENKATA SIVA AGENCIES GST DISPUTE")
    print(f"📁 Case created: {case}")
    
    # 2. Add documents (simulate multiple documents)
    doc1 = test_document_pipeline()  # Use the document from previous test
    case.add_document(doc1)
    
    # Add a second document (simulated)
    doc2 = Document("data/affidavits/affidavit 1/input/p2.pdf")
    doc2.set_extraction_data("Show Cause Notice content...", "Show Cause Notice content...")
    
    classification2 = ClassificationResult(
        document_type=DocumentType.SHOW_CAUSE_NOTICE,
        confidence=0.75,
        matched_patterns=["show.*cause", "DRC-01"],
        classification_reason="Identified as Show Cause Notice"
    )
    doc2.set_classification(classification2)
    
    entities2 = EntityData(
        gstin_numbers=["37ADSPT7675HIZI"],
        dates=[{"original": "24-08-2023", "normalized": "2023-08-24", "type": "notice_date"}],
        legal_sections=["73", "73(1)"],
        form_numbers=["DRC-01"]
    )
    doc2.set_entities(entities2)
    
    case.add_document(doc2)
    print(f"✅ Added documents: {case.document_count}")
    
    # 3. Add case analysis
    timeline = Timeline(
        events=[
            {"date": "2023-08-24", "event": "Show Cause Notice issued", "document": "p2.pdf"},
            {"date": "2023-12-30", "event": "Adjudication Order passed", "document": "p1.pdf"}
        ],
        start_date=datetime(2023, 8, 24),
        end_date=datetime(2023, 12, 30),
        duration_days=128
    )
    
    analysis = CaseAnalysis(
        case_type=CaseType.ITC_MISMATCH,
        key_facts=[
            "ITC mismatch identified for tax period Jul 2017 - Mar 2018",
            "Show Cause Notice issued on 24-08-2023",
            "Adjudication Order passed on 30-12-2023"
        ],
        legal_issues=[
            {"issue": "Natural Justice", "severity": "high", "description": "Proper hearing not conducted"},
            {"issue": "Limitation Period", "severity": "medium", "description": "Notice issued beyond 3-year limit"}
        ],
        procedural_violations=["Inadequate hearing opportunity"],
        timeline=timeline,
        recommendations=["File appeal challenging natural justice violation"],
        strength_assessment="Strong case due to procedural violations"
    )
    
    case.set_analysis(analysis)
    print(f"✅ Case analyzed: {case.case_type.value}")
    print(f"   Legal issues: {len(analysis.legal_issues)}")
    print(f"   Timeline events: {len(timeline.events)}")
    
    # 4. Get case summary
    summary = case.get_processing_summary()
    print(f"\n📊 CASE SUMMARY:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # 5. Get aggregated entities
    all_entities = case.get_all_entities()
    print(f"\n🔍 AGGREGATED ENTITIES:")
    for key, value in all_entities.items():
        print(f"   {key}: {value}")
    
    return case


def test_affidavit_pipeline():
    """Test Affidavit model generation."""
    print("\n🧪 TESTING AFFIDAVIT MODEL PIPELINE")
    print("=" * 60)
    
    # 1. Initialize affidavit
    affidavit = Affidavit("AFF_001", "CASE_001")
    print(f"📝 Affidavit created: {affidavit}")
    
    # 2. Set affiant details
    affiant = AffiantDetails(
        name="VENKATA SIVARAMA KRISHNA TANGA",
        designation="Authorized Representative",
        company="VENKATA SIVA AGENCIES",
        address="Andhra Pradesh, 522101",
        gstin="37ADSPT7675HIZI",
        contact_details={"phone": "+91-XXXXXXXXXX", "email": "contact@example.com"}
    )
    affidavit.set_affiant_details(affiant)
    print(f"✅ Affiant details set: {affiant.name}")
    
    # 3. Set court details
    court = CourtDetails(
        court_name="High Court of Andhra Pradesh",
        case_number="WP 5146 OF 2025",
        case_title="VENKATA SIVA AGENCIES vs. GST DEPARTMENT",
        filing_date=datetime.now(),
        jurisdiction="Andhra Pradesh"
    )
    affidavit.set_court_details(court)
    print(f"✅ Court details set: {court.court_name}")
    
    # 4. Update sections with content
    sections_content = [
        "I, VENKATA SIVARAMA KRISHNA TANGA, aged about XX years, son of...",
        "The chronology of events in this case is as follows:\n1. Show Cause Notice dated 24-08-2023\n2. Adjudication Order dated 30-12-2023",
        "The facts of the case are that the petitioner is engaged in...",
        "The legal grounds for this petition are:\n1. Violation of natural justice\n2. Limitation period exceeded",
        "The petitioner prays for the following relief:\n1. Quash the impugned order\n2. Grant any other relief",
        "I solemnly affirm that the contents of this affidavit are true..."
    ]
    
    for i, content in enumerate(sections_content, 1):
        affidavit.update_section(i, content)
    
    print(f"✅ All sections updated")
    
    # 5. Add source documents
    affidavit.add_source_document("data/affidavits/affidavit 1/input/p1.pdf")
    affidavit.add_source_document("data/affidavits/affidavit 1/input/p2.pdf")
    affidavit.set_template("standard_gst_affidavit_template")
    
    # 6. Validate completeness
    validation = affidavit.validate_completeness()
    print(f"✅ Validation complete: {validation['score']:.1f}% complete")
    print(f"   Is complete: {validation['is_complete']}")
    if validation['empty_sections']:
        print(f"   Empty sections: {validation['empty_sections']}")
    
    # 7. Mark as generated
    affidavit.mark_as_generated("output/affidavit_001.docx")
    print(f"✅ Affidavit generated: {affidavit.status.value}")
    print(f"   Word count: {affidavit.word_count}")
    print(f"   Page count: {affidavit.page_count}")
    
    # 8. Get generation summary
    summary = affidavit.get_generation_summary()
    print(f"\n📊 AFFIDAVIT SUMMARY:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # 9. Get content preview
    preview = affidavit.get_content_preview(300)
    print(f"\n📖 CONTENT PREVIEW:")
    print(preview)
    
    return affidavit


def test_complete_pipeline():
    """Test the complete pipeline integration."""
    print("\n🧪 TESTING COMPLETE PIPELINE INTEGRATION")
    print("=" * 60)
    
    # Create case with documents
    case = test_case_pipeline()
    
    # Generate affidavit from case
    affidavit = test_affidavit_pipeline()
    
    # Show integration
    print(f"\n🔗 PIPELINE INTEGRATION:")
    print(f"   Case: {case.case_id} with {case.document_count} documents")
    print(f"   Affidavit: {affidavit.affidavit_id} for case {affidavit.case_id}")
    print(f"   Source documents: {len(affidavit.source_documents)}")
    
    # Show processing stages
    print(f"\n📈 PROCESSING STAGES:")
    for doc in case.documents:
        print(f"   {doc.file_name}: {doc.current_stage.value}")
    print(f"   Case: {case.status.value}")
    print(f"   Affidavit: {affidavit.status.value}")
    
    return case, affidavit


if __name__ == "__main__":
    print("🚀 GST Law Co-pilot - Data Models Testing")
    print("=" * 60)
    
    try:
        # Test individual models
        doc = test_document_pipeline()
        case = test_case_pipeline()
        affidavit = test_affidavit_pipeline()
        
        # Test complete integration
        final_case, final_affidavit = test_complete_pipeline()
        
        print(f"\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print(f"   Documents processed: {len(final_case.documents)}")
        print(f"   Case status: {final_case.status.value}")
        print(f"   Affidavit completeness: {final_affidavit.completeness_score:.1f}%")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
