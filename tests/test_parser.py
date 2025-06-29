"""
Test Script for Document Parser Components

This script tests the document processing pipeline components individually
to validate their efficacy for PDF text and data extraction.
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from document_processor import DocumentExtractor, DocumentClassifier, EntityParser


def test_document_extractor(file_path):
    """Test the DocumentExtractor component with enhanced docling features."""
    """Test the DocumentExtractor component with enhanced docling features."""
    print(f"\n🔍 TESTING DOCUMENT EXTRACTOR")
    print(f"File: {file_path}")
    print("-" * 50)
    
    try:
        extractor = DocumentExtractor()
        result = extractor.extract_text(file_path)
        
        text = result['text']
        metadata = result['metadata']
        
        print(f"✅ Extraction successful!")
        print(f"📄 Pages: {metadata.get('pages', 'N/A')}")
        print(f"🔧 Method: {metadata.get('extraction_method', 'N/A')}")
        print(f"📝 Text length: {len(text)} characters")
        print(f"📝 Word count: {len(text.split())} words")
        
        # Enhanced docling-specific metrics
        if metadata.get('extraction_method') == 'docling_enhanced':
            print(f"📊 Tables found: {metadata.get('tables_found', 0)}")
            print(f"🖼️  Images extracted: {metadata.get('images_extracted', 0)}")
            
            # Show markdown file info if available
            markdown_file = metadata.get('markdown_saved')
            if markdown_file:
                markdown_path = Path(markdown_file)
                if markdown_path.exists():
                    file_size = markdown_path.stat().st_size
                    print(f"💾 Markdown saved: {markdown_path.name} ({file_size} bytes)")
            
            # Detect markdown features in extracted text
            markdown_features = []
            if '|' in text and '---' in text:
                markdown_features.append("Tables")
            if '![' in text and '](' in text:
                markdown_features.append("Image references")
            if '#' in text:
                markdown_features.append("Headers")
            if '```' in text:
                markdown_features.append("Code blocks")
            
            if markdown_features:
                print(f"🔍 Markdown features: {', '.join(markdown_features)}")
            
            # Check for images directory
            doc_name = Path(file_path).stem
            images_dir = Path("data/extracted_images") / doc_name
            if images_dir.exists():
                image_files = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
                if image_files:
                    print(f"📁 Images directory: {len(image_files)} file(s) in {images_dir}")
        
        # Show extraction issues if any
        extraction_issues = metadata.get('extraction_issues', [])
        if extraction_issues:
            print(f"⚠️  Extraction Issues: {len(extraction_issues)}")
            for issue in extraction_issues[:3]:  # Show first 3 issues
                print(f"   • {issue}")
        
        # Show first 500 characters
        print(f"\n📖 EXTRACTED TEXT PREVIEW:")
        print("-" * 30)
        preview_text = text[:500]
        # Replace multiple newlines with single space for cleaner preview
        preview_text = ' '.join(preview_text.split())
        print(preview_text + "..." if len(text) > 500 else preview_text)
        
        # Show extraction quality assessment
        print(f"\n📈 EXTRACTION QUALITY ASSESSMENT:")
        print("-" * 35)
        
        # Text quality indicators
        quality_score = 0
        quality_indicators = []
        
        if len(text) > 100:
            quality_score += 1
            quality_indicators.append("✅ Sufficient text length")
        else:
            quality_indicators.append("⚠️  Short text extracted")
        
        if metadata.get('extraction_method') == 'docling_enhanced':
            quality_score += 2
            quality_indicators.append("✅ Enhanced docling extraction")
        elif metadata.get('extraction_method') in ['pdfplumber', 'pypdf2']:
            quality_score += 1
            quality_indicators.append("✅ Standard PDF extraction")
        elif metadata.get('extraction_method') == 'ocr':
            quality_indicators.append("⚠️  OCR fallback used")
        
        if metadata.get('tables_found', 0) > 0:
            quality_score += 1
            quality_indicators.append("✅ Tables detected and preserved")
        
        if metadata.get('images_extracted', 0) > 0:
            quality_score += 1
            quality_indicators.append("✅ Images extracted successfully")
        
        if not extraction_issues:
            quality_score += 1
            quality_indicators.append("✅ No extraction issues")
        
        # Display quality assessment
        for indicator in quality_indicators:
            print(f"   {indicator}")
        
        quality_level = "Excellent" if quality_score >= 4 else "Good" if quality_score >= 2 else "Basic"
        print(f"   📊 Overall Quality: {quality_level} ({quality_score}/5)")
        
        return result
        
    except Exception as e:
        print(f"❌ Extraction failed: {str(e)}")
        print(f"🔧 This might be due to:")
        print(f"   • Unsupported file format")
        print(f"   • File corruption or access issues")
        print(f"   • Missing dependencies (docling, OCR libraries)")
        print(f"   • File permission problems")
        return None


def test_document_classifier(extracted_result):
    """Test the DocumentClassifier component."""
    print(f"\n🏷️  TESTING DOCUMENT CLASSIFIER")
    print("-" * 50)
    
    if not extracted_result:
        print("❌ No extracted text to classify")
        return None
    
    try:
        classifier = DocumentClassifier()
        text = extracted_result['text']
        metadata = extracted_result['metadata']
        
        classification = classifier.classify_document(text, metadata)
        
        doc_type = classification['document_type'].value
        confidence = classification['confidence']
        matched_patterns = classification['matched_patterns']
        reason = classification['classification_reason']
        
        print(f"✅ Classification successful!")
        print(f"📋 Document Type: {doc_type}")
        print(f"🎯 Confidence: {confidence:.2f}")
        print(f"🔍 Matched Patterns: {len(matched_patterns)}")
        print(f"💭 Reason: {reason}")
        
        if matched_patterns:
            print(f"\n🎯 MATCHED PATTERNS:")
            for pattern in matched_patterns:
                print(f"   • {pattern}")
        
        return classification
        
    except Exception as e:
        print(f"❌ Classification failed: {str(e)}")
        return None


def test_entity_parser(extracted_result):
    """Test the EntityParser component."""
    print(f"\n🔍 TESTING ENTITY PARSER")
    print("-" * 50)
    
    if not extracted_result:
        print("❌ No extracted text to parse")
        return None
    
    try:
        parser = EntityParser()
        text = extracted_result['text']
        
        entities = parser.parse_entities(text)
        
        print(f"✅ Entity extraction successful!")
        
        # Display summary
        summary = entities.get('summary', {})
        print(f"\n📊 ENTITY SUMMARY:")
        for key, count in summary.items():
            print(f"   {key}: {count}")
        
        # Display specific entities
        print(f"\n📋 EXTRACTED ENTITIES:")
        
        # GSTIN Numbers
        gstin_numbers = entities.get('gstin_numbers', [])
        if gstin_numbers:
            print(f"   🏢 GSTIN Numbers: {gstin_numbers}")
        
        # Dates
        dates = entities.get('dates', [])
        if dates:
            print(f"   📅 Dates found: {len(dates)}")
            for date_info in dates[:3]:  # Show first 3
                print(f"      • {date_info['original']} → {date_info['normalized']}")
        
        # Amounts
        amounts = entities.get('amounts', [])
        if amounts:
            print(f"   💰 Amounts found: {len(amounts)}")
            for amount_info in amounts[:3]:  # Show first 3
                print(f"      • {amount_info['original']} → {amount_info['cleaned']}")
        
        # Legal Sections
        sections = entities.get('legal_sections', [])
        if sections:
            print(f"   ⚖️  Legal Sections: {sections}")
        
        # Form Numbers
        forms = entities.get('form_numbers', [])
        if forms:
            print(f"   📄 Form Numbers: {forms}")
        
        # Case Numbers
        cases = entities.get('case_numbers', [])
        if cases:
            print(f"   📋 Case Numbers: {cases}")
        
        return entities
        
    except Exception as e:
        print(f"❌ Entity parsing failed: {str(e)}")
        return None


def test_case_folder(case_path):
    """Test all documents in a case input folder."""
    input_path = Path(case_path) / "input"
    
    if not input_path.exists():
        print(f"⚠️  Input folder not found: {input_path}")
        return
    
    # Get all PDF and text files in input folder
    input_files = list(input_path.glob("*.pdf")) + list(input_path.glob("*.txt"))
    
    if not input_files:
        print(f"⚠️  No input documents found in: {input_path}")
        return
    
    print(f"\n🧪 TESTING CASE: {case_path}")
    print(f"📁 Input documents: {len(input_files)}")
    print("=" * 60)
    
    for doc_path in input_files:
        print(f"\n📄 Processing: {doc_path.name}")
        print("-" * 40)
        
        # Test 1: Document Extraction
        extracted_result = test_document_extractor(str(doc_path))
        
        # Test 2: Document Classification
        classification_result = test_document_classifier(extracted_result)
        
        # Test 3: Entity Parsing
        entity_result = test_entity_parser(extracted_result)


def main():
    """Main test function."""
    print("🚀 GST Law Co-pilot - Document Parser Testing")
    print("=" * 60)
    
    # Check for organized case structure first
    affidavits_path = Path("data/affidavits")
    if affidavits_path.exists():
        case_folders = [d for d in affidavits_path.iterdir() if d.is_dir()]
        
        if case_folders:
            print(f"📁 Found {len(case_folders)} case folder(s) in data/affidavits/")
            for case_folder in sorted(case_folders):
                test_case_folder(case_folder)
        else:
            print("📁 No case folders found in data/affidavits/")
        
    print(f"\n✅ Testing complete!")
    print(f"💡 Review the results above to assess parser efficacy")
    print(f"📋 To test with organized cases, add folders to data/affidavits/ with input/ subdirectories")


if __name__ == "__main__":
    main()
