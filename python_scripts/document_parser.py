"""
Main document parser that orchestrates PDF/DOCX extraction and section detection
"""

import json
import sys
import os
from typing import Dict, Any
from pdf_parser import extract_pdf_text
from docx_parser import extract_docx_text
from section_detector import SectionDetector
from text_normalizer import TextNormalizer
from info_extractor import InformationExtractor
from gemini_analyzer import GeminiAnalyzer
from ats_analyzer import ATSAnalyzer
from quality_scorer import ResumeQualityScorer


def parse_document(file_path: str, job_description: str = None, job_title: str = None, 
                  company: str = None, required_skills: list = None, 
                  preferred_skills: list = None) -> Dict[str, Any]:
    """
    Parse a resume document and extract structured information
    
    Args:
        file_path: Path to the document file
        job_description: Optional job description for targeted analysis
        job_title: Optional job title for context
        company: Optional company name for context
        required_skills: Optional list of required skills
        preferred_skills: Optional list of preferred skills
        
    Returns:
        Complete parsing results including text extraction and section detection
    """
    
    # Initialize result structure
    result = {
        "success": False,
        "file_info": {
            "filename": os.path.basename(file_path),
            "extension": os.path.splitext(file_path)[1].lower(),
            "size_bytes": 0,
            "size_mb": 0
        },
        "text_extraction": {
            "success": False,
            "text": "",
            "metadata": {},
            "error": None
        },
        "section_detection": {
            "success": False,
            "sections": [],
            "contact_info": {},
            "structure_analysis": {},
            "error": None
        },
        "summary": {
            "total_characters": 0,
            "total_words": 0,
            "total_lines": 0,
            "sections_detected": 0,
            "is_scanned": False,
            "structure_quality": "unknown"
        },
        "recommendations": [],
        "error": None
    }
    
    try:
        # Validate file exists
        if not os.path.exists(file_path):
            result["error"] = f"File not found: {file_path}"
            return result
        
        # Get file info
        file_size = os.path.getsize(file_path)
        result["file_info"].update({
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2)
        })
        
        extension = result["file_info"]["extension"]
        
        # Step 1: Extract text based on file type
        if extension == ".pdf":
            text_result = extract_pdf_text(file_path)
        elif extension in [".docx", ".doc"]:
            text_result = extract_docx_text(file_path)
        else:
            result["error"] = f"Unsupported file type: {extension}"
            return result
        
        result["text_extraction"] = text_result
        
        if not text_result["success"]:
            result["error"] = f"Text extraction failed: {text_result.get('error', 'Unknown error')}"
            return result
        
        extracted_text = text_result["text"]
        
        # Step 2: Normalize and clean text if extraction was successful
        text_normalization = {}
        if extracted_text.strip():
            normalizer = TextNormalizer()
            text_normalization = normalizer.normalize_text(extracted_text)
            # Use normalized text for further processing
            normalized_text = text_normalization["normalized"]
        else:
            normalized_text = extracted_text
            text_normalization = {
                "success": False,
                "error": "No text available for normalization"
            }
        
        result["text_normalization"] = text_normalization
        
        # Step 3: Extract structured information
        information_extraction = {}
        if normalized_text.strip():
            extractor = InformationExtractor()
            information_extraction = extractor.extract_all_information(extracted_text, normalized_text)
        else:
            information_extraction = {
                "success": False,
                "error": "No text available for information extraction"
            }
        
        result["information_extraction"] = information_extraction
        
        # Step 4: AI-powered analysis using Gemini
        ai_analysis = {}
        if information_extraction.get("success"):
            analyzer = GeminiAnalyzer()
            ai_analysis = analyzer.analyze_resume(
                information_extraction, 
                extracted_text,
                job_description=job_description,
                job_title=job_title,
                company=company,
                required_skills=required_skills,
                preferred_skills=preferred_skills
            )
            # Format for display
            ai_analysis = analyzer.format_analysis_for_display(ai_analysis)
        else:
            ai_analysis = {
                "success": False,
                "error": "Cannot perform AI analysis without extracted information"
            }
        
        result["ai_analysis"] = ai_analysis
        
        # Step 6: Comprehensive ATS compatibility analysis
        ats_analysis = {}
        if extracted_text.strip():
            ats_analyzer = ATSAnalyzer()
            ats_analysis = ats_analyzer.analyze_ats_compatibility(
                file_path, 
                extracted_text, 
                information_extraction
            )
        else:
            ats_analysis = {
                "success": False,
                "error": "No text available for ATS analysis"
            }
        
        result["ats_analysis"] = ats_analysis
        
        # Step 7: Comprehensive quality scoring
        quality_analysis = {}
        if extracted_text.strip() and information_extraction.get("success"):
            # Determine target experience years from job context
            target_experience_years = None
            if job_title:
                # Simple heuristic based on job title
                title_lower = job_title.lower()
                if any(term in title_lower for term in ["senior", "lead", "principal"]):
                    target_experience_years = 5
                elif any(term in title_lower for term in ["junior", "associate", "entry"]):
                    target_experience_years = 2
                else:
                    target_experience_years = 3  # Default mid-level
            
            # Combine required and preferred skills for quality analysis
            target_skills_combined = []
            if required_skills:
                target_skills_combined.extend(required_skills)
            if preferred_skills:
                target_skills_combined.extend(preferred_skills)
            
            quality_scorer = ResumeQualityScorer()
            quality_analysis = quality_scorer.score_resume_quality(
                extracted_text,
                information_extraction,
                target_skills_combined if target_skills_combined else None,
                target_experience_years,
                ats_analysis
            )
        else:
            quality_analysis = {
                "success": False,
                "error": "No text or extracted data available for quality analysis"
            }
        
        result["quality_analysis"] = quality_analysis
        
        # Step 8: Detect sections using normalized text (legacy support)
        if normalized_text.strip():
            detector = SectionDetector()
            section_result = detector.detect_sections(normalized_text)
            result["section_detection"] = section_result
        else:
            result["section_detection"]["error"] = "No text available for section detection"
        
        # Step 9: Generate enhanced summary with extracted information
        summary = {
            "total_characters": len(extracted_text),
            "total_words": len(extracted_text.split()),
            "total_lines": len(extracted_text.split('\n')),
            "sections_detected": len(result["section_detection"].get("sections", [])),
            "parsing_method": text_result.get("parsing_method", "unknown"),
            "is_scanned": text_result.get("is_scanned", False),
            "structure_quality": result["section_detection"].get("structure_analysis", {}).get("structure_quality", "unknown"),
            # Text normalization statistics
            "normalized_characters": text_normalization.get("statistics", {}).get("normalized_length", 0),
            "normalized_words": text_normalization.get("statistics", {}).get("normalized_words", 0),
            "bullet_points_found": text_normalization.get("statistics", {}).get("bullet_points_found", 0),
            "sections_by_headings": text_normalization.get("statistics", {}).get("sections_found", 0),
            "compression_ratio": text_normalization.get("statistics", {}).get("compression_ratio", 1.0),
            # Information extraction statistics
            "total_experience_years": information_extraction.get("summary_stats", {}).get("total_experience_years", 0),
            "total_skills_found": information_extraction.get("summary_stats", {}).get("total_skills", 0),
            "total_projects": information_extraction.get("summary_stats", {}).get("total_projects", 0),
            "total_certifications": information_extraction.get("summary_stats", {}).get("total_certifications", 0),
            "education_level": information_extraction.get("summary_stats", {}).get("education_level", "unknown"),
            "career_level": information_extraction.get("summary_stats", {}).get("career_level", "entry"),
            "primary_role": information_extraction.get("summary_stats", {}).get("primary_role", "unknown"),
            # AI analysis scores
            "ai_overall_score": ai_analysis.get("formatted_analysis", {}).get("summary", {}).get("overall_score", 0),
            "ats_compatibility": ai_analysis.get("formatted_analysis", {}).get("summary", {}).get("ats_compatibility", "unknown"),
            "contact_completeness": ai_analysis.get("formatted_analysis", {}).get("contact_completeness", 0),
            "ai_powered": ai_analysis.get("ai_powered", False),
            # ATS analysis scores
            "ats_score": ats_analysis.get("ats_score", {}).get("total_score", 0),
            "ats_compatibility_level": ats_analysis.get("compatibility_level", "unknown"),
            "ats_priority_issues": len(ats_analysis.get("priority_issues", [])),
            "ats_word_count": ats_analysis.get("length_analysis", {}).get("word_count", 0),
            "ats_estimated_pages": ats_analysis.get("length_analysis", {}).get("estimated_pages", 0),
            # Quality analysis scores
            "quality_score": quality_analysis.get("overall_score", 0),
            "quality_level": quality_analysis.get("quality_level", "unknown"),
            "content_fit_score": quality_analysis.get("score_breakdown", {}).get("content_fit", {}).get("score", 0),
            "clarity_score": quality_analysis.get("score_breakdown", {}).get("clarity_quantification", {}).get("score", 0),
            "structure_score": quality_analysis.get("score_breakdown", {}).get("structure_readability", {}).get("score", 0)
        }
        result["summary"] = summary
        
        # Step 10: Generate comprehensive recommendations
        recommendations = []
        
        # Text extraction recommendations
        if text_result.get("is_scanned"):
            recommendations.append("Document appears to be scanned - consider using OCR for better text extraction")
        
        # Text normalization recommendations
        if text_normalization.get("statistics", {}).get("compression_ratio", 1.0) < 0.9:
            recommendations.append("Text contained formatting issues that were cleaned up")
        
        bullet_count = text_normalization.get("statistics", {}).get("bullet_points_found", 0)
        if bullet_count == 0:
            recommendations.append("Consider using bullet points to improve readability")
        elif bullet_count > 20:
            recommendations.append("Consider consolidating bullet points for better focus")
        
        # AI-powered recommendations
        if ai_analysis.get("success") and ai_analysis.get("formatted_analysis"):
            ai_recommendations = ai_analysis["formatted_analysis"].get("recommendations", {})
            if ai_recommendations.get("immediate_actions"):
                recommendations.extend(ai_recommendations["immediate_actions"][:3])  # Top 3 immediate actions
        
        # ATS compatibility recommendations
        if ats_analysis.get("recommendations"):
            ats_recs = ats_analysis["recommendations"]
            # Add critical and high priority ATS recommendations
            if ats_recs.get("critical"):
                recommendations.extend(ats_recs["critical"][:2])  # Top 2 critical issues
            if ats_recs.get("high_priority"):
                recommendations.extend(ats_recs["high_priority"][:3])  # Top 3 high priority issues
        
        # Quality-based recommendations
        if quality_analysis.get("recommendations"):
            quality_recs = quality_analysis["recommendations"]
            # Add critical and high priority quality recommendations
            if quality_recs.get("critical"):
                recommendations.extend(quality_recs["critical"][:2])  # Top 2 critical issues
            if quality_recs.get("high_priority"):
                recommendations.extend(quality_recs["high_priority"][:2])  # Top 2 high priority issues
        
        # Information extraction recommendations
        contact_info = information_extraction.get("contact_info", {})
        if not contact_info.get("email"):
            recommendations.append("Add email address for better contact accessibility")
        if not contact_info.get("phone"):
            recommendations.append("Include phone number in contact information")
        
        skills_count = information_extraction.get("skills", {}).get("total_skills_found", 0)
        if skills_count < 5:
            recommendations.append("Add more technical skills to improve keyword matching")
        
        # Section detection recommendations (legacy)
        if result["section_detection"].get("success"):
            structure_recs = result["section_detection"]["structure_analysis"].get("recommendations", [])
            recommendations.extend(structure_recs[:2])  # Limit to 2 recommendations
        
        # General recommendations
        if summary["total_characters"] < 500:
            recommendations.append("Resume appears to be very short - consider adding more detail")
        elif summary["total_characters"] > 5000:
            recommendations.append("Resume is quite long - consider condensing for better readability")
        
        if summary["sections_detected"] < 3:
            recommendations.append("Consider organizing content into more distinct sections")
        
        result["recommendations"] = recommendations
        
        # Overall success
        result["success"] = text_result["success"]
        
    except Exception as e:
        result["error"] = f"Document parsing error: {str(e)}"
    
    return result


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python document_parser.py <file_path> [job_description] [job_title] [company] [required_skills] [preferred_skills]"
        }))
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Parse optional job context parameters
    job_description = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != 'None' else None
    job_title = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != 'None' else None
    company = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != 'None' else None
    
    # Parse skills arrays from JSON strings
    required_skills = None
    preferred_skills = None
    
    if len(sys.argv) > 5 and sys.argv[5] != 'None':
        try:
            required_skills = json.loads(sys.argv[5])
        except json.JSONDecodeError:
            pass  # Continue without required skills
    
    if len(sys.argv) > 6 and sys.argv[6] != 'None':
        try:
            preferred_skills = json.loads(sys.argv[6])
        except json.JSONDecodeError:
            pass  # Continue without preferred skills
    
    result = parse_document(
        file_path, 
        job_description=job_description,
        job_title=job_title,
        company=company,
        required_skills=required_skills,
        preferred_skills=preferred_skills
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
