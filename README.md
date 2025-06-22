# GST Law Co-pilot

A command-line tool to analyze GST-related legal documents and generate draft affidavits for lawyers handling GST dispute cases in India.

## 📋 Project Documentation

For comprehensive project information, please refer to our structured documentation:

**👉 [Project Context & Overview](memory_bank/project-context.md)** - Start here for complete understanding

### Quick Navigation

- **📋 [Project Brief](memory_bank/project-brief.md)** - Executive summary and high-level overview
- **🌍 [Project Context](memory_bank/project-context.md)** - Comprehensive domain and business context  
- **🏗️ [System Architecture](memory_bank/system-architecture.md)** - Technical architecture and design
- **⚡ [Active Context](memory_bank/active-context.md)** - Current development status
- **📚 [Memory Bank Index](memory_bank/README.md)** - Complete documentation guide

## Quick Start

### Prerequisites
- Python 3.8+
- Tesseract OCR
- Poppler (for PDF processing)

### Installation

**macOS:**
```bash
# Install system dependencies
brew install poppler tesseract

# Clone and setup
git clone <repository-url>
cd law_pilot

# Setup virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Test document processing
python tests/test_parser.py

# Process documents (when CLI is complete)
python main.py --documents notice.pdf order.pdf --output affidavit.docx
```

## Current Status

✅ **Document Processing**: Advanced multi-tier extraction with Docling, pdfplumber, PyPDF2, and OCR  
✅ **Entity Extraction**: GSTIN numbers, dates, amounts, legal sections  
✅ **Document Classification**: SCN, Orders, Appeals, Correspondence  
🚧 **Analysis Engine**: Timeline building and facts extraction (in development)  
📋 **Affidavit Generation**: Planned next phase  

## Key Features

### ✅ Implemented
- **Advanced Document Processing**: 4-tier extraction strategy (Docling → pdfplumber → PyPDF2 → OCR)
- **Structured Output**: Markdown format with preserved document formatting
- **Entity Extraction**: Comprehensive GST-specific data extraction
- **Document Classification**: Automatic document type identification
- **Flexible Input**: Handles any combination of GST documents

### 🚧 In Development
- Timeline generation and chronology building
- Legal issues identification
- Facts extraction and analysis
- Affidavit section generation

## Technology Stack

- **Language**: Python 3.8+
- **Document Processing**: Docling, pdfplumber, PyPDF2, Tesseract OCR
- **Text Processing**: spaCy, NLTK
- **Output**: python-docx
- **CLI**: argparse/click

## Testing

Current test results show **100% success rate** on real GST documents:
- **Text Extraction**: 1,738-8,642 characters per document with structured markdown
- **Entity Recognition**: GSTIN, dates, amounts, legal sections accurately identified
- **Classification**: Document types correctly identified with confidence scores

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Legal Context

This tool assists with the GST dispute resolution process in India:
1. **Show Cause Notice** → Company Reply → Personal Hearing
2. **Adjudavit Order** → Appeals (Commissioner → Tribunal → High Court)
3. **Court Proceedings** → Affidavit generation for legal representation

## Documentation

For detailed information about the project, architecture, and development context, please visit our comprehensive [Memory Bank documentation](memory_bank/README.md).

## License

[License information to be added]

---

**For complete project context and detailed information, see: [Project Context](memory_bank/project-context.md)**
