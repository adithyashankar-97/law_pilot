"""
Test script for enhanced parser with LightRAG integration
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_processor.parser import EntityParser, create_parser
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_parser_setup():
    """Test basic parser setup and configuration"""
    print("🧪 Testing Enhanced Parser Setup")
    print("=" * 50)
    
    # Test 1: Regex parser (should always work)
    print("\n1. Testing Regex Parser...")
    try:
        regex_parser = create_parser(method="regex")
        status = regex_parser.get_lightrag_status()
        print("✅ Regex parser created successfully")
        print(f"   Status: {status}")
    except Exception as e:
        print(f"❌ Regex parser failed: {e}")
    
    # Test 2: LightRAG parser (requires API key)
    print("\n2. Testing LightRAG Parser...")
    api_key = input("Enter your Google AI API key (or press Enter to skip): ").strip()
    
    if api_key:
        try:
            lightrag_parser = create_parser(method="lightrag", google_api_key=api_key)
            status = lightrag_parser.get_lightrag_status()
            print("✅ LightRAG parser created successfully")
            print(f"   Status: {status}")
            return lightrag_parser
        except Exception as e:
            print(f"❌ LightRAG parser failed: {e}")
            return None
    else:
        print("⏭️  Skipping LightRAG test (no API key provided)")
        return None


def test_folder_structure():
    """Test and create folder structure"""
    print("\n🧪 Testing Folder Structure")
    print("=" * 30)
    
    # Expected folders
    folders = [
        "./data/source_docs",
        "./data/markdown_files", 
        "./data/lightrag"
    ]
    
    for folder in folders:
        folder_path = Path(folder)
        if folder_path.exists():
            file_count = len(list(folder_path.iterdir()))
            print(f"✅ {folder} exists ({file_count} items)")
        else:
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created {folder}")


def test_document_insertion(parser):
    """Test document insertion into LightRAG"""
    if not parser or parser.method != "lightrag":
        print("⏭️  Skipping document insertion (LightRAG not available)")
        return
    
    print("\n🧪 Testing Document Insertion")
    print("=" * 32)
    
    # Check for markdown files
    markdown_dir = Path("./data/markdown_files")
    markdown_files = list(markdown_dir.glob("*.md"))
    
    if not markdown_files:
        print("📄 No markdown files found in ./data/markdown_files")
        print("💡 To test document insertion:")
        print("   1. Put PDF files in ./data/source_docs")
        print("   2. Run the extractor to convert them to markdown")
        print("   3. Then run this test again")
        return
    
    print(f"📄 Found {len(markdown_files)} markdown files")
    
    # Test insertion
    try:
        success = parser.insert_documents()
        if success:
            print("✅ Documents inserted successfully")
        else:
            print("❌ Document insertion failed")
    except Exception as e:
        print(f"❌ Document insertion error: {e}")


def test_entity_extraction(parser):
    """Test entity extraction"""
    print("\n🧪 Testing Entity Extraction")
    print("=" * 29)
    
    try:
        # Test with sample text first
        sample_text = """
        DRC-07 order dated 30.12.2023 confirming tax demand of ₹9,49,106/- 
        against GSTIN 37ADSPT7675HIZI for VENKATA SIVA AGENCIES for the period 
        July 2017 to March 2018 under Section 73 of CGST Act.
        """
        
        print("📝 Testing with sample legal text...")
        entities = parser.parse_entities(sample_text)
        
        print(f"✅ Extracted entities using {entities.get('extraction_method', 'unknown')} method")
        print(f"   Summary: {entities.get('summary', {})}")
        
        # Print some key entities
        if entities.get('gstin_numbers'):
            print(f"   GSTIN: {entities['gstin_numbers']}")
        if entities.get('amounts'):
            print(f"   Amounts: {[amt.get('original', amt) for amt in entities['amounts'][:3]]}")
        if entities.get('form_numbers'):
            print(f"   Forms: {entities['form_numbers']}")
        
        return entities
        
    except Exception as e:
        print(f"❌ Entity extraction failed: {e}")
        return None


def test_comparison(regex_parser, lightrag_parser):
    """Compare regex vs LightRAG extraction"""
    if not lightrag_parser:
        print("⏭️  Skipping comparison (LightRAG not available)")
        return
    
    print("\n🧪 Comparing Regex vs LightRAG")
    print("=" * 33)
    
    sample_text = """
    Show Cause Notice DRC-01 dated 24.08.2023 issued to M/s VENKATA SIVA AGENCIES 
    (GSTIN: 37ADSPT7675HIZI) for non-payment of tax amounting to ₹8,76,128/- 
    under Section 73 of CGST Act for the period July 2017-March 2018.
    
    Adjudication Order DRC-07 dated 30.12.2023 confirmed total demand of ₹9,49,106/- 
    including penalty and interest. Appeal filed under Section 107 with pre-deposit 
    of ₹1,57,500/- representing 10% of confirmed demand.
    """
    
    # Extract with both methods
    print("🔄 Extracting with Regex...")
    regex_entities = regex_parser.parse_entities(sample_text)
    
    print("🔄 Extracting with LightRAG...")
    lightrag_entities = lightrag_parser.parse_entities(sample_text)
    
    # Compare results
    print("\n📊 Comparison Results:")
    print("-" * 20)
    
    for entity_type in ['gstin_numbers', 'amounts', 'form_numbers', 'legal_sections']:
        regex_count = len(regex_entities.get(entity_type, []))
        lightrag_count = len(lightrag_entities.get(entity_type, []))
        
        print(f"{entity_type:15}: Regex={regex_count:2d}, LightRAG={lightrag_count:2d}")
    
    print(f"\nTotal entities   : Regex={regex_entities['summary']['total_entities']:2d}, "
          f"LightRAG={lightrag_entities['summary']['total_entities']:2d}")


def main():
    """Main test function"""
    print("🚀 Enhanced Parser Testing Suite")
    print("=" * 40)
    
    # Test 1: Setup
    lightrag_parser = test_parser_setup()
    regex_parser = create_parser(method="regex")
    
    # Test 2: Folder structure
    test_folder_structure()
    
    # Test 3: Document insertion (if LightRAG available)
    test_document_insertion(lightrag_parser)
    
    # Test 4: Entity extraction
    print("\n" + "=" * 50)
    print("Testing Regex Parser:")
    test_entity_extraction(regex_parser)
    
    if lightrag_parser:
        print("\n" + "=" * 50)
        print("Testing LightRAG Parser:")
        test_entity_extraction(lightrag_parser)
        
        # Test 5: Comparison
        test_comparison(regex_parser, lightrag_parser)
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print("\n💡 Next steps:")
    print("   1. Put PDF files in ./data/source_docs")
    print("   2. Run extractor.py to convert to markdown")
    print("   3. Use enhanced parser for entity extraction")


if __name__ == "__main__":
    main()