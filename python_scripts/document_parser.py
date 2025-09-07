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


def parse_document(file_path: str) -> Dict[str, Any]:
    """
    Parse a resume document and extract structured information
    
    Args:
        file_path: Path to the document file
        
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
        
        # Step 2: Detect sections if text extraction was successful
        if extracted_text.strip():
            detector = SectionDetector()
            section_result = detector.detect_sections(extracted_text)
            result["section_detection"] = section_result
        else:
            result["section_detection"]["error"] = "No text available for section detection"
        
        # Step 3: Generate summary
        summary = {
            "total_characters": len(extracted_text),
            "total_words": len(extracted_text.split()),
            "total_lines": len(extracted_text.split('\n')),
            "sections_detected": len(result["section_detection"].get("sections", [])),
            "parsing_method": text_result.get("parsing_method", "unknown"),
            "is_scanned": text_result.get("is_scanned", False),
            "structure_quality": result["section_detection"].get("structure_analysis", {}).get("structure_quality", "unknown")
        }
        result["summary"] = summary
        
        # Step 4: Generate recommendations
        recommendations = []
        
        # Text extraction recommendations
        if text_result.get("is_scanned"):
            recommendations.append("Document appears to be scanned - consider using OCR for better text extraction")
        
        # Section detection recommendations
        if result["section_detection"].get("success"):
            structure_recs = result["section_detection"]["structure_analysis"].get("recommendations", [])
            recommendations.extend(structure_recs)
        
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
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python document_parser.py <file_path>"
        }))
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = parse_document(file_path)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
