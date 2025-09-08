"""
PDF text extraction for resume parsing
Uses PyPDF2 for PDF text extraction
"""

import PyPDF2
import json
import sys
import os
from typing import Dict, Any, Optional, Tuple


def extract_pdf_text(file_path: str) -> Dict[str, Any]:
    """
    Extract text from PDF using PyPDF2
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary containing extraction results
    """
    result = {
        "success": False,
        "text": "",
        "metadata": {},
        "parsing_method": "PyPDF2",
        "is_scanned": False,
        "char_count": 0,
        "error": None
    }
    
    try:
        if not os.path.exists(file_path):
            result["error"] = f"File not found: {file_path}"
            return result
            
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract metadata
            metadata = {}
            if pdf_reader.metadata:
                metadata = {
                    "title": pdf_reader.metadata.get('/Title', ''),
                    "author": pdf_reader.metadata.get('/Author', ''),
                    "subject": pdf_reader.metadata.get('/Subject', ''),
                    "creator": pdf_reader.metadata.get('/Creator', ''),
                    "producer": pdf_reader.metadata.get('/Producer', ''),
                    "creation_date": str(pdf_reader.metadata.get('/CreationDate', '')),
                    "modification_date": str(pdf_reader.metadata.get('/ModDate', ''))
                }
            
            # Extract text from all pages
            text_parts = []
            page_count = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_parts.append(page_text)
                except Exception as e:
                    print(f"Warning: Failed to extract text from page {page_num + 1}: {e}")
                    continue
            
            full_text = "\n".join(text_parts)
            
            # Check if document might be scanned (very little extractable text)
            is_scanned = len(full_text.strip()) < 100 and page_count > 0
            
            result.update({
                "success": True,
                "text": full_text,
                "metadata": {
                    "page_count": page_count,
                    "pdf_metadata": metadata,
                    "file_size": os.path.getsize(file_path)
                },
                "is_scanned": is_scanned,
                "char_count": len(full_text)
            })
            
            if is_scanned:
                result["error"] = "Document appears to be scanned - OCR may be needed"
                
    except Exception as e:
        result["error"] = f"PDF parsing error: {str(e)}"
        
    return result


def main():
    """Main function for command line usage"""
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python pdf_parser.py <pdf_file_path>"
        }))
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = extract_pdf_text(file_path)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
