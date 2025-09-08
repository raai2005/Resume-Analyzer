# Resume Analyzer

A comprehensive resume analysis tool with AI-powered insights, ATS compatibility scoring, and detailed feedback reporting.

## Features

- **PDF & DOCX Support**: Parse resumes in multiple formats
- **ATS Compatibility**: Analyze resume compatibility with Applicant Tracking Systems
- **AI-Powered Analysis**: Leverage Google Gemini AI for intelligent insights
- **Quality Scoring**: Multi-dimensional quality assessment across 30+ categories
- **Skills Analysis**: Match skills against job requirements and identify gaps
- **Detailed Reporting**: Comprehensive feedback with actionable recommendations

## Architecture

- **Frontend**: Next.js 15 with React 19 and TypeScript
- **Backend**: FastAPI Python server
- **AI Integration**: Google Gemini API for advanced analysis

## Project Structure

```
resume_analyzer/
├── src/                    # Next.js frontend
│   ├── app/               # App router pages
│   └── components/        # React components
├── python_scripts/        # Core Python modules
│   ├── final_api.py      # Main API endpoint
│   ├── document_parser.py # Document parsing orchestration
│   ├── ats_analyzer.py   # ATS compatibility analysis
│   ├── quality_scorer.py # Quality assessment
│   └── ...               # Other analysis modules
├── fastapi_server.py      # FastAPI server entry point
├── requirements.txt       # Python dependencies
└── package.json          # Node.js dependencies
```

## Setup

### Prerequisites

- Node.js 18+
- Python 3.8+
- Google Gemini API key (optional, for AI features)

### Installation

1. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies:**

   ```bash
   npm install
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   CORS_ORIGINS=http://localhost:3000
   ```

## Running the Application

1. **Start the Python backend:**

   ```bash
   python fastapi_server.py
   ```

   The API server will run on `http://localhost:8000`

2. **Start the Next.js frontend:**
   ```bash
   npm run dev
   ```
   The web application will be available at `http://localhost:3000`

## Usage

1. Open the application in your browser
2. Upload a resume (PDF or DOCX format)
3. Optionally provide job details for targeted analysis
4. View comprehensive analysis results including:
   - Contact information extraction
   - Skills analysis and matching
   - ATS compatibility score
   - Quality assessment
   - AI-powered insights and recommendations

## API Documentation

The API provides a comprehensive analysis endpoint at `/analyze-resume` with detailed response structure documented in `API_DOCUMENTATION.md`.

## Build for Production

```bash
npm run build
npm start
```

For the Python backend, use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn fastapi_server:app -w 4 -k uvicorn.workers.UvicornWorker
```
