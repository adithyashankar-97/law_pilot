"""
Test complete LightRAG pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_processor.legal_processor import LegalDocumentProcessor

def test_complete_pipeline():
    """Test the complete pipeline"""
    print("🧪 Testing Complete Legal LightRAG Pipeline")
    print("=" * 60)
    
    # Get API key
    GOOGLE_API_KEY = input("Enter your Google AI API key: ").strip()
    
    # Initialize processor
    processor = LegalDocumentProcessor(google_api_key=GOOGLE_API_KEY)
    
    # Run complete pipeline
    results = processor.process_all()
    
    if results["status"] == "success":
        print(f"\n✅ Pipeline completed successfully!")
        print(f"📄 Markdown files: {results['markdown_files_count']}")
        print(f"🧠 LightRAG processing: {results['lightrag_results']['status']}")
        
        # Test entity queries
        print(f"\n🔍 Testing entity extraction...")
        entities = processor.query_entities("What GSTIN numbers were found?")
        print(f"Entities: {entities[:200]}...")
        
        # Test legal analysis
        print(f"\n⚖️  Testing legal analysis...")
        analysis = processor.query_legal_analysis("What legal issues are identified in these documents?")
        print(f"Analysis: {analysis[:200]}...")
        
    else:
        print(f"❌ Pipeline failed: {results.get('message', 'Unknown error')}")

if __name__ == "__main__":
    test_complete_pipeline()