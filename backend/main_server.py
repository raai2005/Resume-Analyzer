#!/usr/bin/env python3
"""
FastAPI server for comprehensive resume analysis
Serves the enhanced JSON analysis with all implemented features
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
import sys
import traceback
from typing import Optional
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current backend directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from api.resume_analysis_api import analyze_resume_api
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {current_dir}")
    raise

app = FastAPI(title="Resume Analyzer API", description="Comprehensive resume analysis with ATS compatibility, quality scoring, and AI insights")

# Get CORS origins from environment variable
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001").split(",")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "Resume Analyzer API is running",
        "version": "2.0.0",
        "features": [
            "Comprehensive analysis with 30+ categories",
            "ATS compatibility scoring",
            "AI-powered insights and recommendations",
            "Skills analysis and matching",
            "Quality scoring across multiple dimensions"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "resume-analyzer-api"}

@app.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    job_title: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    target_skills: Optional[str] = Form(None)
):
    """
    Comprehensive resume analysis endpoint
    
    Returns structured JSON with:
    - Contact information analysis
    - Skills matching and gap analysis
    - ATS compatibility scoring
    - Quality metrics and scoring
    - AI-powered insights and recommendations
    - Industry and competitive analysis
    - 30+ additional analysis categories
    """
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.doc']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_ext}. Supported types: {', '.join(allowed_extensions)}"
        )
    
    # Create temporary file
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Prepare analysis parameters
        analysis_params = {
            'job_title': job_title,
            'job_description': job_description,
            'target_skills': target_skills.split(',') if target_skills else None
        }
        
        # Perform comprehensive analysis
        try:
            result = analyze_resume_api(
                temp_file_path,
                job_title=job_title,
                job_description=job_description,
                target_skills=target_skills.split(',') if target_skills else None
            )
            
            # Ensure we have the expected structure
            if not isinstance(result, dict) or 'status' not in result:
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "status_code": 500,
                        "message": "Invalid response format from analysis engine",
                        "data": None
                    }
                )
            
            return JSONResponse(
                status_code=200,
                content=result
            )
            
        except Exception as analysis_error:
            print(f"Analysis error: {str(analysis_error)}")
            print(f"Traceback: {traceback.format_exc()}")
            
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "status_code": 500,
                    "message": f"Analysis failed: {str(analysis_error)}",
                    "data": None
                }
            )
    
    except Exception as e:
        print(f"Server error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "status_code": 500,
                "message": f"Server error: {str(e)}",
                "data": None
            }
        )
    
    finally:
        # Cleanup temporary files
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except:
            pass

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
