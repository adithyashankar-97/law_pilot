## Brief overview
Guidelines for language-based projects including legal document processing, NLP tasks, and text analysis tools. These rules are specific to projects involving document processing, text extraction, and AI-powered content generation.

## Virtual environment setup
- Always use the Python virtual environment located at `/Users/adithya/Desktop/codes/venvs/lang_stuff/` for language-based tasks
- Activate this environment before installing dependencies or running any Python code
- This applies to legal document processing, NLP projects, and similar language-focused applications

## Project documentation
- Create and maintain a comprehensive memory bank file (`memory_bank.md`) at the project root
- Include project overview, technical requirements, development phases with checkboxes
- Document current status, completed tasks, and next steps
- Update memory bank as tasks are completed to track progress

## Document processing approach
- Design systems to handle flexible input document sets (not fixed document types)
- Build adaptive processing pipelines that work with partial information
- Handle unknown document types gracefully by extracting general content
- Ensure minimum viable functionality with just one input document

## Development workflow
- Start with proof-of-concept command-line tools before building web interfaces
- Break complex systems into modular components (document_processor, analyzer, generator)
- Use clear project structure with separate directories for models, utils, and data
- Implement step-by-step processing pipelines with clear separation of concerns

## Code organization
- Use descriptive module names that reflect functionality (extractor.py, classifier.py, parser.py)
- Create data models for core entities (Document, Case, Affidavit)
- Separate business logic from data processing and output generation
- Include comprehensive constants file for domain-specific information
- Keep all test scripts inside tests directory only.

## Technical stack preferences
- Python 3.8+ for language processing tasks
- PyPDF2/pdfplumber for PDF text extraction
- spaCy/NLTK for text processing and entity extraction
- python-docx for document generation
- argparse or click for CLI interfaces

## File management
- Clean up unused files as per project requirements
- Organize sample documents and templates in dedicated data directories
- Use existing functions from codebase when possible to avoid duplication
