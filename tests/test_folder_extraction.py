"""
Test folder-based document extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_processor.extractor import DocumentExtractor
from pathlib import Path
import shutil

def setup_test_documents():
    """Copy your existing test docs to source folder"""
    source_dir = Path("./data/source_docs")
    source_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy from your existing test data
    existing_docs = Path("./data/affidavits")
    if existing_docs.exists():
        print("📁 Copying test documents...")
        copied = 0
        for case_dir in existing_docs.iterdir():
            if case_dir.is_dir():
                input_dir = case_dir / "input"
                if input_dir.exists():
                    for doc in input_dir.glob("*.pdf"):
                        dest_path = source_dir / f"{case_dir.name}_{doc.name}"
                        if not dest_path.exists():
                            shutil.copy2(doc, dest_path)
                            copied += 1
        print(f"✅ Copied {copied} documents to {source_dir}")
    else:
        print("💡 Add some PDF files to ./data/source_docs/ for testing")

def test_folder_extraction():
    """Test folder-based extraction"""
    print("🧪 Testing Folder-Based Document Extraction")
    print("=" * 50)
    
    # Setup test documents
    setup_test_documents()
    
    # Initialize extractor with folder paths
    extractor = DocumentExtractor(
        source_dir="./data/source_docs",
        markdown_dir="./data/markdown_files"
    )
    
    # Test folder extraction
    results = extractor.extract_folder(skip_existing=True)
    
    # Test markdown files retrieval
    markdown_files = extractor.get_markdown_files()
    
    print(f"\n📝 Markdown files ready for LightRAG:")
    for md_file in markdown_files[:3]:  # Show first 3
        print(f"   - {md_file['file_name']} ({md_file['size']} bytes)")
    
    print(f"\n🎉 Folder extraction test completed!")
    print(f"📂 Markdown files: {len(markdown_files)}")
    
    return markdown_files

if __name__ == "__main__":
    test_folder_extraction()