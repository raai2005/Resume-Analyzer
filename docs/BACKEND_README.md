# Resume Analyzer Backend

## 🏗️ Architecture Overview

The Resume Analyzer backend is built with **Python FastAPI** and follows a modular microservices architecture for scalable resume analysis and processing.

## 🚀 Tech Stack

### Core Framework

- **FastAPI** - High-performance async web framework
- **Uvicorn** - ASGI server for production deployment
- **Python 3.8+** - Core programming language

### Document Processing

- **PyMuPDF** - High-performance PDF text extraction
- **python-docx** - Microsoft Word document parsing
- **PyPDF2** - Fallback PDF processing

### AI & Analysis

- **Google Gemini AI** - Advanced resume analysis and insights
- **Groq API** - Fast LLM inference for text processing
- **Custom ML Models** - ATS compatibility scoring

### Data Processing

- **JSON** - Structured data exchange
- **Regex** - Pattern matching and text extraction
- **Custom Parsers** - Domain-specific resume parsing

## 📁 Module Structure

```
python_scripts/
├── final_api.py           # 🎯 Main API orchestration
├── document_parser.py     # 📄 Document processing coordinator
├── pdf_parser.py         # 📕 PDF text extraction
├── docx_parser.py        # 📘 Word document parsing
├── section_detector.py   # 🔍 Resume section identification
├── text_normalizer.py    # 🧹 Text cleaning and formatting
├── info_extractor.py     # 📊 Structured data extraction
├── ats_analyzer.py       # 🤖 ATS compatibility analysis
├── quality_scorer.py     # ⭐ Resume quality assessment
├── gemini_analyzer.py    # 🧠 AI-powered insights
└── feedback_report.py    # 📋 Report generation
```

## 🔄 Processing Flow

### 1. **Document Upload & Validation**

```
fastapi_server.py → File validation → Temporary storage
```

### 2. **Document Parsing Pipeline**

```
final_api.py → document_parser.py → [pdf_parser.py | docx_parser.py]
```

### 3. **Text Processing & Normalization**

```
Raw text → text_normalizer.py → Clean, formatted text
```

### 4. **Section Detection & Structure Analysis**

```
Normalized text → section_detector.py → Identified sections
```

### 5. **Information Extraction**

```
Structured sections → info_extractor.py → Contact, Skills, Experience, etc.
```

### 6. **Multi-Layered Analysis**

```
Extracted data → [ats_analyzer.py, quality_scorer.py, gemini_analyzer.py]
```

### 7. **Report Generation**

```
Analysis results → feedback_report.py → Comprehensive JSON response
```

## 🎯 Core Components

### **final_api.py** - API Orchestration

- **Purpose**: Main entry point for resume analysis
- **Features**:
  - Input validation and error handling
  - Coordinates entire analysis pipeline
  - Standardized JSON response formatting
- **Key Functions**:
  - `analyze_resume_api()` - Main analysis endpoint

### **document_parser.py** - Document Processing

- **Purpose**: Orchestrates document parsing and analysis
- **Features**:
  - Multi-format support (PDF, DOCX)
  - Integrated analysis pipeline
  - Error handling and fallbacks
- **Dependencies**: All parsing and analysis modules

### **Text Processing Modules**

#### **pdf_parser.py**

- **Tech**: PyMuPDF, PyPDF2
- **Features**:
  - High-performance PDF text extraction
  - Metadata extraction
  - Scanned document detection

#### **docx_parser.py**

- **Tech**: python-docx
- **Features**:
  - Word document parsing
  - Table and formatting preservation
  - Metadata extraction

#### **text_normalizer.py**

- **Purpose**: Text cleaning and standardization
- **Features**:
  - Unicode normalization
  - Whitespace cleanup
  - Special character handling

### **Analysis Modules**

#### **section_detector.py**

- **Purpose**: Resume section identification
- **Algorithm**: Pattern-based ML detection
- **Sections**: Contact, Summary, Experience, Education, Skills, etc.

#### **info_extractor.py**

- **Purpose**: Structured data extraction
- **Features**:
  - Contact information parsing
  - Experience timeline analysis
  - Skills categorization
  - Education details extraction

#### **ats_analyzer.py**

- **Purpose**: ATS (Applicant Tracking System) compatibility
- **Analysis**:
  - Keyword optimization
  - Format compatibility
  - Parsing friendliness scoring
  - Industry standards compliance

#### **quality_scorer.py**

- **Purpose**: Comprehensive quality assessment
- **Scoring Categories**:
  - Content completeness (25%)
  - Professional presentation (25%)
  - Skills relevance (25%)
  - Experience quality (25%)

#### **gemini_analyzer.py**

- **Tech**: Google Gemini AI API
- **Purpose**: AI-powered insights and recommendations
- **Features**:
  - Intelligent content analysis
  - Personalized recommendations
  - Industry-specific insights
  - Career progression analysis

#### **feedback_report.py**

- **Purpose**: Comprehensive report generation
- **Output**: Structured JSON with 30+ analysis categories

## 🔌 API Endpoints

### **FastAPI Server** (`../fastapi_server.py`)

#### `GET /`

- **Purpose**: Health check and API information
- **Response**: Service status and feature list

#### `GET /health`

- **Purpose**: Deployment monitoring
- **Response**: Health status

#### `POST /analyze-resume`

- **Purpose**: Complete resume analysis
- **Parameters**:
  - `file` (required) - Resume file (PDF/DOCX)
  - `job_title` (optional) - Target job title
  - `job_description` (optional) - Job posting text
  - `target_skills` (optional) - Required skills list
- **Response**: Comprehensive analysis JSON

## 📊 Response Structure

```json
{
  "status": "success|error",
  "status_code": 200|400|500,
  "message": "Description",
  "data": {
    "contact_info": {...},
    "education": [...],
    "experience": [...],
    "skills": {...},
    "ats_analysis": {...},
    "quality_analysis": {...},
    "ai_insights": {...},
    "recommendations": [...],
    // ... 30+ analysis categories
  }
}
```

## 🚀 Deployment

### **Local Development**

```bash
# Install dependencies
pip install -r ../requirements.txt

# Start FastAPI server
uvicorn fastapi_server:app --reload --host 0.0.0.0 --port 8000
```

### **Production**

```bash
# With Uvicorn (recommended)
uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn
gunicorn fastapi_server:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Environment Variables**

```env
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

## 🔧 Configuration

### **CORS Settings**

- Configurable origins for frontend integration
- Supports multiple domains for deployment flexibility

### **File Processing Limits**

- Max file size: 10MB
- Supported formats: PDF, DOCX, DOC
- Timeout: 30 seconds per analysis

### **AI Integration**

- Gemini AI for advanced analysis
- Groq for fast text processing
- Fallback mechanisms for API failures

## 🛡️ Security & Performance

### **Security Features**

- File type validation
- Size limits and timeouts
- CORS protection
- Input sanitization

### **Performance Optimizations**

- Async processing with FastAPI
- Efficient PDF parsing with PyMuPDF
- Modular architecture for scalability
- Response caching potential

### **Error Handling**

- Comprehensive error responses
- Graceful fallbacks for AI services
- Detailed logging for debugging

## 🔄 Future Enhancements

### **Planned Features**

- Batch processing support
- Real-time analysis updates
- Enhanced AI model integration
- Performance metrics and monitoring

### **Scalability Considerations**

- Microservices architecture ready
- Database integration capability
- Queue-based processing potential
- Docker containerization support

---

## 📞 Support

For backend-specific issues:

1. Check logs in FastAPI console
2. Verify Python dependencies
3. Confirm API key configurations
4. Test individual modules independently

**Backend Entry Point**: `../fastapi_server.py`  
**Main API Logic**: `final_api.py`  
**Module Documentation**: Each module contains detailed docstrings
