# GST Law Co-pilot - System Architecture

## Architecture Overview

The GST Law Co-pilot follows a modular, pipeline-based architecture designed for scalability, maintainability, and extensibility. The system processes legal documents through a series of specialized components, each responsible for specific aspects of document analysis and affidavit generation.

## High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "Input Layer"
        A[PDF Documents] --> B[Document Ingestion]
        C[Text Files] --> B
        D[Scanned Images] --> B
    end
    
    subgraph "Processing Pipeline"
        B --> E[Document Extractor]
        E --> F[Document Classifier]
        F --> G[Entity Parser]
        G --> H[Chronology Builder]
        H --> I[Facts Extractor]
        I --> J[Legal Issues Identifier]
    end
    
    subgraph "Analysis Engine"
        H --> K[Timeline Analysis]
        I --> L[Facts Analysis]
        J --> M[Legal Analysis]
        K --> N[Affidavit Generator]
        L --> N
        M --> N
    end
    
    subgraph "Output Layer"
        N --> O[Template Engine]
        O --> P[DOCX Generator]
        P --> Q[Final Affidavit]
    end
    
    subgraph "Support Systems"
        R[Configuration Manager]
        S[Logging System]
        T[Error Handler]
        U[Validation Engine]
    end
    
    subgraph "Legal Knowledge Base"
        V[GST Act Sections]
        W[Legal Precedents]
        X[Procedural Rules]
        Y[Form Templates]
        Z[Case Law Database]
    end
    
    E -.-> R
    F -.-> R
    G -.-> R
    N -.-> U
    B -.-> S
    E -.-> T
    J -.-> V
    J -.-> W
    J -.-> X
    M -.-> V
    M -.-> W
    N -.-> Y
    N -.-> Z
```

## Component Architecture

### 1. Document Processing Layer

#### Document Extractor
```mermaid
graph LR
    A[Input Document] --> B{File Type?}
    B -->|PDF| C[PDF Processor]
    B -->|TXT| D[Text Processor]
    C --> E[Docling Primary]
    E --> F{Success?}
    F -->|Yes| G[Structured Markdown]
    F -->|No| H[pdfplumber Fallback]
    H --> I{Success?}
    I -->|Yes| G
    I -->|No| J[PyPDF2 Fallback]
    J --> K{Success?}
    K -->|Yes| G
    K -->|No| L[OCR Engine]
    L --> M[Tesseract]
    M --> G
    D --> G
    G --> N[Metadata Generation]
    N --> O[Output: Markdown + Metadata]
```

**Key Features**:
- 4-tier extraction strategy with Docling primary
- Structured markdown output with preserved formatting
- OCR fallback for image-based PDFs
- Metadata preservation and extraction method tracking
- Enhanced error handling and logging

#### Document Classifier
```mermaid
graph TD
    A[Extracted Text] --> B[Pattern Matching Engine]
    B --> C{Document Type Detection}
    C -->|Match Found| D[Classification Result]
    C -->|No Match| E[Unknown Document]
    
    subgraph "Pattern Library"
        F[SCN Patterns]
        G[Order Patterns]
        H[Appeal Patterns]
        I[Correspondence Patterns]
    end
    
    B --> F
    B --> G
    B --> H
    B --> I
    
    D --> J[Confidence Score]
    E --> J
    J --> K[Output: Type + Confidence]
```

**Classification Categories**:
- Show Cause Notice (SCN)
- Adjudication Order
- Appeal Order
- Tribunal Order
- Correspondence
- Unknown

#### Entity Parser
```mermaid
graph TB
    A[Classified Text] --> B[Regex Engine]
    B --> C[GSTIN Extractor]
    B --> D[Date Extractor]
    B --> E[Amount Extractor]
    B --> F[Section Extractor]
    B --> G[Form Number Extractor]
    B --> H[Case Number Extractor]
    
    C --> I[GSTIN Validation]
    D --> J[Date Normalization]
    E --> K[Amount Cleaning]
    F --> L[Section Validation]
    G --> M[Form Validation]
    H --> N[Case Validation]
    
    I --> O[Structured Entities]
    J --> O
    K --> O
    L --> O
    M --> O
    N --> O
    
    O --> P[Entity Summary]
```

### 2. Analysis Engine

#### Chronology Builder
```mermaid
graph TD
    A[Parsed Entities] --> B[Date Extraction]
    B --> C[Event Association]
    C --> D[Timeline Construction]
    D --> E[Chronological Sorting]
    E --> F[Gap Analysis]
    F --> G[Timeline Validation]
    G --> H[Formatted Timeline]
    
    subgraph "Event Types"
        I[Notice Dates]
        J[Response Dates]
        K[Hearing Dates]
        L[Order Dates]
        M[Appeal Dates]
    end
    
    C --> I
    C --> J
    C --> K
    C --> L
    C --> M
```

#### Facts Extractor
```mermaid
graph LR
    A[Document Content] --> B[Fact Identification]
    B --> C[Tax Period Facts]
    B --> D[Amount Facts]
    B --> E[Procedural Facts]
    B --> F[Legal Facts]
    
    C --> G[Fact Validation]
    D --> G
    E --> G
    F --> G
    
    G --> H[Structured Facts]
    H --> I[Fact Categorization]
    I --> J[Output: Categorized Facts]
```

#### Legal Issues Identifier
```mermaid
graph TB
    A[Facts + Timeline] --> B[Issue Detection Engine]
    B --> C[Procedural Issues]
    B --> D[Substantive Issues]
    B --> E[Limitation Issues]
    
    C --> F[Natural Justice Violations]
    C --> G[Process Violations]
    D --> H[Tax Calculation Errors]
    D --> I[Classification Issues]
    E --> J[Time Limit Violations]
    
    F --> K[Issue Prioritization]
    G --> K
    H --> K
    I --> K
    J --> K
    
    K --> L[Legal Grounds]
    L --> M[Output: Identified Issues]
```

### 3. Legal Knowledge Base

#### Knowledge Base Architecture
```mermaid
graph TB
    A[Legal Knowledge Base] --> B[GST Act Repository]
    A --> C[Procedural Rules Database]
    A --> D[Case Law Database]
    A --> E[Form Templates Repository]
    A --> F[Legal Precedents Database]
    
    B --> G[Section 73 - Tax Determination]
    B --> H[Section 74 - Fraud Cases]
    B --> I[Section 161 - Rectification]
    B --> J[Section 107 - Appeals]
    
    C --> K[Rule 100 - Adjudication]
    C --> L[Rule 142 - Appeal Procedures]
    C --> M[Rule 88 - SCN Requirements]
    
    D --> N[High Court Judgments]
    D --> O[Tribunal Orders]
    D --> P[Supreme Court Cases]
    
    E --> Q[DRC Forms]
    E --> R[Appeal Forms]
    E --> S[Affidavit Templates]
    
    F --> T[Natural Justice Cases]
    F --> U[Limitation Period Cases]
    F --> V[Procedural Violation Cases]
```

#### Legal Knowledge Integration
```mermaid
graph LR
    A[Legal Issues Identifier] --> B[Knowledge Base Query]
    B --> C[Section Lookup]
    B --> D[Precedent Search]
    B --> E[Rule Validation]
    
    C --> F[Relevant Sections]
    D --> G[Supporting Cases]
    E --> H[Procedural Requirements]
    
    F --> I[Legal Grounds Generator]
    G --> I
    H --> I
    
    I --> J[Affidavit Content]
```

#### Knowledge Base Components
```mermaid
graph TD
    subgraph "GST Act Sections"
        A1[Section 73 - Determination]
        A2[Section 74 - Fraud]
        A3[Section 161 - Rectification]
        A4[Section 107 - Appeals]
        A5[Section 112 - Tribunal Appeals]
    end
    
    subgraph "Procedural Rules"
        B1[Rule 100 - Adjudication Process]
        B2[Rule 142 - Appeal Procedures]
        B3[Rule 88 - SCN Requirements]
        B4[Time Limitations]
        B5[Pre-deposit Requirements]
    end
    
    subgraph "Legal Precedents"
        C1[Natural Justice Violations]
        C2[Limitation Period Issues]
        C3[Procedural Compliance]
        C4[Tax Calculation Disputes]
        C5[Classification Issues]
    end
    
    subgraph "Form Templates"
        D1[DRC-01 - Show Cause Notice]
        D2[DRC-06 - Reply Format]
        D3[DRC-07 - Adjudication Order]
        D4[APL-01 - Appeal Form]
        D5[Affidavit Templates]
    end
```

### 4. Generation Engine

#### Affidavit Generator
```mermaid
graph TD
    A[Analysis Results] --> B[Section Generator]
    B --> C[Header Generator]
    B --> D[Chronology Generator]
    B --> E[Facts Generator]
    B --> F[Legal Grounds Generator]
    B --> G[Relief Generator]
    B --> H[Verification Generator]
    
    C --> I[Template Engine]
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I
    
    I --> J[Content Assembly]
    J --> K[Format Validation]
    K --> L[DOCX Generation]
    L --> M[Final Affidavit]
    
    subgraph "Knowledge Base Integration"
        N[Legal Knowledge Base]
        N --> F
        N --> G
    end
```

## Data Flow Architecture

### Primary Data Flow
```mermaid
sequenceDiagram
    participant U as User
    participant CLI as CLI Interface
    participant DP as Document Processor
    participant AE as Analysis Engine
    participant AG as Affidavit Generator
    participant FS as File System
    
    U->>CLI: Input documents
    CLI->>DP: Process documents
    DP->>DP: Extract text (OCR if needed)
    DP->>DP: Classify documents
    DP->>DP: Parse entities
    DP->>AE: Send processed data
    AE->>AE: Build chronology
    AE->>AE: Extract facts
    AE->>AE: Identify legal issues
    AE->>AG: Send analysis results
    AG->>AG: Generate affidavit sections
    AG->>FS: Create DOCX file
    AG->>CLI: Return success status
    CLI->>U: Display results
```

### Error Handling Flow
```mermaid
graph TD
    A[Processing Step] --> B{Error Occurred?}
    B -->|No| C[Continue Pipeline]
    B -->|Yes| D[Error Handler]
    D --> E{Error Type?}
    E -->|Recoverable| F[Apply Fallback]
    E -->|Critical| G[Log Error]
    F --> H[Retry Operation]
    G --> I[Graceful Failure]
    H --> J{Success?}
    J -->|Yes| C
    J -->|No| G
    I --> K[User Notification]
```

## Technology Stack Architecture

### Core Technologies
```mermaid
graph TB
    subgraph "Application Layer"
        A[Python 3.8+]
        B[Click CLI Framework]
        C[argparse]
    end
    
    subgraph "Document Processing"
        D[pdfplumber]
        E[PyPDF2]
        F[Tesseract OCR]
        G[pdf2image]
        H[Pillow]
    end
    
    subgraph "Text Processing"
        I[spaCy NLP]
        J[NLTK]
        K[Regular Expressions]
        L[python-dateutil]
    end
    
    subgraph "Output Generation"
        M[python-docx]
        N[Jinja2 Templates]
        O[JSON/YAML Config]
    end
    
    subgraph "Development Tools"
        P[pytest]
        Q[Git]
        R[Virtual Environment]
    end
    
    A --> B
    A --> D
    A --> I
    A --> M
    D --> F
    I --> K
```

## Module Dependencies

### Dependency Graph
```mermaid
graph TD
    A[main.py] --> B[document_processor]
    A --> C[analyzer]
    A --> D[generator]
    A --> E[utils]
    
    B --> F[extractor.py]
    B --> G[classifier.py]
    B --> H[parser.py]
    
    C --> I[chronology.py]
    C --> J[facts.py]
    C --> K[legal_issues.py]
    
    D --> L[affidavit.py]
    D --> M[sections.py]
    D --> N[templates.py]
    
    E --> O[constants.py]
    E --> P[helpers.py]
    
    F --> Q[models/document.py]
    G --> Q
    H --> Q
    I --> R[models/case.py]
    L --> S[models/affidavit.py]
```

## Configuration Architecture

### Configuration Management
```mermaid
graph LR
    A[Configuration Files] --> B[Config Manager]
    B --> C[Document Processing Config]
    B --> D[OCR Config]
    B --> E[Classification Config]
    B --> F[Template Config]
    
    C --> G[File Type Settings]
    C --> H[Extraction Parameters]
    D --> I[Tesseract Settings]
    D --> J[Image Processing]
    E --> K[Pattern Definitions]
    E --> L[Confidence Thresholds]
    F --> M[Affidavit Templates]
    F --> N[Section Templates]
```

## Security Architecture

### Security Layers
```mermaid
graph TB
    subgraph "Input Security"
        A[File Validation]
        B[Size Limits]
        C[Type Checking]
    end
    
    subgraph "Processing Security"
        D[Sandboxed Execution]
        E[Memory Management]
        F[Timeout Controls]
    end
    
    subgraph "Data Security"
        G[Local Processing]
        H[No Cloud Storage]
        I[Temporary File Cleanup]
    end
    
    subgraph "Output Security"
        J[Content Validation]
        K[Format Verification]
        L[Access Controls]
    end
    
    A --> D
    B --> E
    C --> F
    D --> G
    E --> H
    F --> I
    G --> J
    H --> K
    I --> L
```

## Performance Architecture

### Performance Optimization
```mermaid
graph TD
    A[Performance Requirements] --> B[Processing Optimization]
    A --> C[Memory Optimization]
    A --> D[I/O Optimization]
    
    B --> E[Parallel Processing]
    B --> F[Caching Strategies]
    B --> G[Algorithm Optimization]
    
    C --> H[Memory Pooling]
    C --> I[Garbage Collection]
    C --> J[Resource Cleanup]
    
    D --> K[Batch Processing]
    D --> L[Stream Processing]
    D --> M[File Handling]
```

### Scalability Considerations
- **Horizontal Scaling**: Multiple document processing in parallel
- **Vertical Scaling**: Optimized for single-machine performance
- **Resource Management**: Efficient memory and CPU utilization
- **Caching**: Template and configuration caching for performance

## Deployment Architecture

### Local Deployment
```mermaid
graph LR
    A[User Machine] --> B[Python Environment]
    B --> C[Virtual Environment]
    C --> D[Application Code]
    C --> E[Dependencies]
    C --> F[System Libraries]
    
    D --> G[CLI Interface]
    E --> H[Python Packages]
    F --> I[Tesseract OCR]
    F --> J[Poppler Utils]
```

### Installation Flow
```mermaid
sequenceDiagram
    participant U as User
    participant S as System
    participant P as Package Manager
    participant A as Application
    
    U->>S: Install system dependencies
    S->>S: Install Tesseract, Poppler
    U->>P: Create virtual environment
    P->>P: Setup Python environment
    U->>P: Install Python packages
    P->>P: Install requirements.txt
    U->>A: Initialize application
    A->>A: Verify dependencies
    A->>U: Ready for use
```

## Monitoring and Logging

### Logging Architecture
```mermaid
graph TD
    A[Application Events] --> B[Logging System]
    B --> C[Debug Logs]
    B --> D[Info Logs]
    B --> E[Warning Logs]
    B --> F[Error Logs]
    
    C --> G[Development]
    D --> H[Production]
    E --> I[Monitoring]
    F --> J[Error Tracking]
    
    G --> K[Console Output]
    H --> L[File Logging]
    I --> M[Alert System]
    J --> N[Error Reports]
```

## Future Architecture Considerations

### Extensibility Points
1. **Plugin Architecture**: Support for custom document processors
2. **Template System**: Customizable affidavit templates
3. **API Layer**: RESTful API for web integration
4. **Database Layer**: Persistent storage for case management
5. **ML Pipeline**: Machine learning model integration

### Migration Path
```mermaid
graph LR
    A[Current CLI] --> B[Enhanced CLI]
    B --> C[Web Interface]
    C --> D[API Service]
    D --> E[Cloud Platform]
    
    A1[Local Processing] --> B1[Hybrid Processing]
    B1 --> C1[Cloud Processing]
    
    A2[File-based] --> B2[Database Integration]
    B2 --> C2[Full Case Management]
```

This architecture provides a solid foundation for the current CLI implementation while maintaining flexibility for future enhancements and scaling requirements.
