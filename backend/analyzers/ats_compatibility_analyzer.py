"""
ATS Compatibility Analyzer for Resume Documents
Provides comprehensive analysis of resume compatibility with Applicant Tracking Systems
"""

import os
import re
import fitz  # PyMuPDF
from docx import Document
from typing import Dict, Any, List, Tuple
import statistics
from collections import Counter


class ATSAnalyzer:
    """Analyzes resume documents for ATS compatibility using simple heuristics"""
    
    def __init__(self):
        self.preferred_extensions = ['.pdf', '.docx', '.doc']
        self.section_keywords = {
            'experience': ['experience', 'work', 'employment', 'professional', 'career', 'history'],
            'education': ['education', 'academic', 'university', 'college', 'degree', 'school'],
            'skills': ['skills', 'technical', 'technologies', 'tools', 'programming', 'competencies'],
            'contact': ['contact', 'phone', 'email', 'address', 'linkedin', 'github']
        }
        self.problematic_symbols = ['★', '☆', '●', '◆', '▲', '▼', '♦', '♠', '♥', '♣', '✓', '✗', '→', '←', '↑', '↓']
        
    def analyze_ats_compatibility(self, file_path: str, extracted_text: str = None, 
                                 extracted_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive ATS compatibility analysis
        
        Args:
            file_path: Path to the resume file
            extracted_text: Already extracted text content (optional)
            extracted_data: Already extracted structured data (optional)
            
        Returns:
            Comprehensive ATS compatibility analysis with score and recommendations
        """
        
        # Get file information
        file_info = self._get_file_info(file_path)
        
        # File type and format checks
        file_checks = self._check_file_format(file_path, file_info)
        
        # Layout analysis (requires extracted text)
        layout_analysis = {}
        if extracted_text:
            layout_analysis = self._analyze_layout(extracted_text, file_path)
        
        # Content validation
        content_analysis = {}
        if extracted_text and extracted_data:
            content_analysis = self._validate_content(extracted_text, extracted_data)
        
        # Length recommendations
        length_analysis = {}
        if extracted_text and extracted_data:
            length_analysis = self._analyze_length(extracted_text, extracted_data)
        
        # Calculate overall ATS score
        overall_score = self._calculate_ats_score(file_checks, layout_analysis, content_analysis, length_analysis)
        
        # Generate recommendations
        recommendations = self._generate_ats_recommendations(file_checks, layout_analysis, content_analysis, length_analysis)
        
        return {
            "file_info": file_info,
            "file_format_analysis": file_checks,
            "layout_analysis": layout_analysis,
            "content_analysis": content_analysis,
            "length_analysis": length_analysis,
            "ats_score": overall_score,
            "recommendations": recommendations,
            "compatibility_level": self._get_compatibility_level(overall_score["total_score"]),
            "priority_issues": self._get_priority_issues(file_checks, layout_analysis, content_analysis, length_analysis)
        }
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Extract basic file information"""
        try:
            stat = os.stat(file_path)
            size_bytes = stat.st_size
            size_mb = round(size_bytes / (1024 * 1024), 2)
            
            return {
                "filename": os.path.basename(file_path),
                "extension": os.path.splitext(file_path)[1].lower(),
                "size_bytes": size_bytes,
                "size_mb": size_mb,
                "exists": True
            }
        except (OSError, FileNotFoundError):
            return {
                "filename": os.path.basename(file_path) if file_path else "unknown",
                "extension": "",
                "size_bytes": 0,
                "size_mb": 0,
                "exists": False
            }
    
    def _check_file_format(self, file_path: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check file format compatibility with ATS systems"""
        results = {
            "format_score": 0,
            "is_preferred_format": False,
            "is_scanned_pdf": False,
            "format_warnings": [],
            "format_recommendations": []
        }
        
        extension = file_info.get("extension", "").lower()
        
        # Check preferred formats
        if extension in ['.pdf', '.docx']:
            results["is_preferred_format"] = True
            results["format_score"] += 25
        elif extension == '.doc':
            results["is_preferred_format"] = True
            results["format_score"] += 20
            results["format_warnings"].append("DOC format is older - DOCX is preferred")
            results["format_recommendations"].append("Convert to DOCX format for better compatibility")
        else:
            results["format_warnings"].append(f"Format {extension} is not ATS-friendly")
            results["format_recommendations"].append("Convert to PDF or DOCX format")
        
        # Check for scanned PDF
        if extension == '.pdf':
            is_scanned = self._check_scanned_pdf(file_path)
            results["is_scanned_pdf"] = is_scanned
            
            if is_scanned:
                results["format_score"] = 0  # Override score for scanned PDFs
                results["format_warnings"].append("CRITICAL: Scanned PDF detected - no searchable text")
                results["format_recommendations"].append("Convert scanned PDF to text-based PDF or DOCX")
            else:
                results["format_score"] += 25  # Bonus for text-based PDF
        
        return results
    
    def _check_scanned_pdf(self, file_path: str) -> bool:
        """Check if PDF is scanned (image-based) with no searchable text"""
        try:
            doc = fitz.open(file_path)
            
            # Check first few pages for text content
            pages_to_check = min(3, len(doc))
            total_text_length = 0
            
            for page_num in range(pages_to_check):
                page = doc[page_num]
                text = page.get_text()
                total_text_length += len(text.strip())
            
            doc.close()
            
            # If very little text found across pages, likely scanned
            # Heuristic: less than 100 characters per page suggests scanned content
            avg_text_per_page = total_text_length / pages_to_check if pages_to_check > 0 else 0
            return avg_text_per_page < 100
            
        except Exception:
            return False  # If we can't analyze, assume it's okay
    
    def _analyze_layout(self, text: str, file_path: str) -> Dict[str, Any]:
        """Analyze document layout for ATS compatibility issues"""
        results = {
            "layout_score": 0,
            "has_multi_column": False,
            "excessive_tables": False,
            "excessive_images": False,
            "excessive_textboxes": False,
            "layout_warnings": [],
            "layout_recommendations": []
        }
        
        # Multi-column detection using line length variance
        multi_column_detected = self._detect_multi_column_layout(text)
        results["has_multi_column"] = multi_column_detected
        
        if multi_column_detected:
            results["layout_warnings"].append("Multi-column layout detected - may cause reading issues")
            results["layout_recommendations"].append("Consider single-column layout for better ATS parsing")
        else:
            results["layout_score"] += 20
        
        # Check for excessive elements (PDF-specific)
        if file_path.lower().endswith('.pdf'):
            element_counts = self._count_pdf_elements(file_path)
            
            # Tables check
            if element_counts.get("tables", 0) > 3:
                results["excessive_tables"] = True
                results["layout_warnings"].append(f"Many tables detected ({element_counts['tables']}) - may confuse ATS")
                results["layout_recommendations"].append("Reduce table usage, use simple formatting instead")
            else:
                results["layout_score"] += 15
            
            # Images check
            if element_counts.get("images", 0) > 2:
                results["excessive_images"] = True
                results["layout_warnings"].append(f"Multiple images detected ({element_counts['images']}) - ATS cannot read images")
                results["layout_recommendations"].append("Remove non-essential images, keep only professional photo if needed")
            else:
                results["layout_score"] += 15
        
        # DOCX-specific checks
        elif file_path.lower().endswith('.docx'):
            element_counts = self._count_docx_elements(file_path)
            
            if element_counts.get("textboxes", 0) > 2:
                results["excessive_textboxes"] = True
                results["layout_warnings"].append(f"Text boxes detected ({element_counts['textboxes']}) - ATS may skip content")
                results["layout_recommendations"].append("Replace text boxes with regular paragraph text")
            else:
                results["layout_score"] += 20
        
        return results
    
    def _detect_multi_column_layout(self, text: str) -> bool:
        """Detect multi-column layout using line length variance and margin patterns"""
        lines = text.split('\n')
        
        # Filter out empty lines and very short lines (likely headers/footers)
        content_lines = [line for line in lines if len(line.strip()) > 10]
        
        if len(content_lines) < 10:
            return False
        
        # Calculate line lengths
        line_lengths = [len(line.strip()) for line in content_lines]
        
        # Check for bimodal distribution (two distinct column widths)
        if len(line_lengths) > 20:
            # Calculate variance in line lengths
            variance = statistics.variance(line_lengths)
            mean_length = statistics.mean(line_lengths)
            
            # High variance relative to mean suggests columns
            coefficient_of_variation = (variance ** 0.5) / mean_length if mean_length > 0 else 0
            
            # Check for repeating patterns of short and long lines
            length_pattern = []
            for length in line_lengths[:50]:  # Check first 50 lines
                if length < mean_length * 0.7:
                    length_pattern.append('short')
                else:
                    length_pattern.append('long')
            
            # Count transitions between short and long
            transitions = sum(1 for i in range(1, len(length_pattern)) 
                            if length_pattern[i] != length_pattern[i-1])
            
            # High coefficient of variation + many transitions suggests multi-column
            return coefficient_of_variation > 0.5 and transitions > len(length_pattern) * 0.3
        
        return False
    
    def _count_pdf_elements(self, file_path: str) -> Dict[str, int]:
        """Count problematic elements in PDF documents"""
        try:
            doc = fitz.open(file_path)
            counts = {"tables": 0, "images": 0, "drawings": 0}
            
            for page in doc:
                # Count tables (heuristic: look for table-like structures)
                blocks = page.get_text("dict")["blocks"]
                table_indicators = 0
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            text = ""
                            for span in line["spans"]:
                                text += span["text"]
                            # Simple heuristic: lines with multiple tab-separated values
                            if text.count('\t') > 2 or text.count('  ') > 4:
                                table_indicators += 1
                
                if table_indicators > 5:  # If many table-like lines, count as table
                    counts["tables"] += 1
                
                # Count images
                image_list = page.get_images()
                counts["images"] += len(image_list)
                
                # Count drawings/vector graphics
                drawings = page.get_drawings()
                counts["drawings"] += len(drawings)
            
            doc.close()
            return counts
            
        except Exception:
            return {"tables": 0, "images": 0, "drawings": 0}
    
    def _count_docx_elements(self, file_path: str) -> Dict[str, int]:
        """Count problematic elements in DOCX documents"""
        try:
            doc = Document(file_path)
            counts = {"tables": 0, "images": 0, "textboxes": 0}
            
            # Count tables
            counts["tables"] = len(doc.tables)
            
            # Count images and textboxes (requires checking document relationships)
            try:
                # Access document relationships to count images and textboxes
                rels = doc.part.rels
                for rel in rels.values():
                    if 'image' in rel.target_ref:
                        counts["images"] += 1
                    elif 'textbox' in rel.target_ref or 'shape' in rel.target_ref:
                        counts["textboxes"] += 1
            except:
                # Fallback: scan document XML for image/textbox elements
                doc_xml = str(doc._element.xml)
                counts["images"] = doc_xml.count('<pic:pic')
                counts["textboxes"] = doc_xml.count('<v:textbox') + doc_xml.count('<w:txbxContent')
            
            return counts
            
        except Exception:
            return {"tables": 0, "images": 0, "textboxes": 0}
    
    def _validate_content(self, text: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content for ATS compatibility"""
        results = {
            "content_score": 0,
            "has_required_sections": {},
            "contact_info_complete": False,
            "excessive_symbols": False,
            "content_warnings": [],
            "content_recommendations": []
        }
        
        # Check for required sections
        section_analysis = self._analyze_section_headings(text)
        results["has_required_sections"] = section_analysis
        
        # Score based on section presence
        required_sections = ['experience', 'education', 'skills']
        found_sections = sum(1 for section in required_sections if section_analysis.get(section, False))
        results["content_score"] += (found_sections / len(required_sections)) * 30
        
        # Missing section warnings
        for section in required_sections:
            if not section_analysis.get(section, False):
                results["content_warnings"].append(f"Missing {section.title()} section heading")
                results["content_recommendations"].append(f"Add clear '{section.title()}' section heading")
        
        # Contact info validation
        contact_complete = self._validate_contact_info(extracted_data)
        results["contact_info_complete"] = contact_complete
        
        if contact_complete:
            results["content_score"] += 25
        else:
            results["content_warnings"].append("Incomplete contact information")
            results["content_recommendations"].append("Ensure name, email, and phone number are clearly visible")
        
        # Symbol and formatting checks
        symbol_issues = self._check_problematic_symbols(text)
        results["excessive_symbols"] = symbol_issues["has_issues"]
        
        if symbol_issues["has_issues"]:
            results["content_warnings"].extend(symbol_issues["warnings"])
            results["content_recommendations"].extend(symbol_issues["recommendations"])
        else:
            results["content_score"] += 15
        
        return results
    
    def _analyze_section_headings(self, text: str) -> Dict[str, bool]:
        """Check for presence of standard resume section headings"""
        text_lower = text.lower()
        lines = text.split('\n')
        
        results = {}
        
        for section, keywords in self.section_keywords.items():
            found = False
            
            # Look for section headings (short lines with keywords)
            for line in lines:
                line_clean = line.strip().lower()
                
                # Skip very long lines (likely not headings)
                if len(line_clean) > 50:
                    continue
                
                # Check if line contains section keywords
                if any(keyword in line_clean for keyword in keywords):
                    # Additional validation: line should be relatively standalone
                    if len(line_clean) < 30 and any(keyword == line_clean or 
                                                   line_clean.startswith(keyword) for keyword in keywords):
                        found = True
                        break
            
            results[section] = found
        
        return results
    
    def _validate_contact_info(self, extracted_data: Dict[str, Any]) -> bool:
        """Validate completeness of contact information"""
        if not extracted_data:
            return False
        
        contact_info = extracted_data.get("contact_info", {})
        
        # Check for essential contact elements
        has_name = bool(contact_info.get("name"))
        has_email = bool(contact_info.get("email"))
        has_phone = bool(contact_info.get("phone"))
        
        # At minimum, need name and either email or phone
        return has_name and (has_email or has_phone)
    
    def _check_problematic_symbols(self, text: str) -> Dict[str, Any]:
        """Check for symbols that may cause ATS parsing issues"""
        results = {
            "has_issues": False,
            "symbol_count": 0,
            "problematic_symbols_found": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Count problematic symbols
        symbol_counts = Counter()
        for symbol in self.problematic_symbols:
            count = text.count(symbol)
            if count > 0:
                symbol_counts[symbol] = count
                results["symbol_count"] += count
        
        results["problematic_symbols_found"] = list(symbol_counts.keys())
        
        # Determine if there are issues
        if results["symbol_count"] > 5:  # More than 5 problematic symbols
            results["has_issues"] = True
            results["warnings"].append(f"Excessive special symbols found ({results['symbol_count']} instances)")
            results["recommendations"].append("Replace special symbols with standard text formatting")
        elif results["symbol_count"] > 0:
            results["warnings"].append(f"Some special symbols detected ({results['symbol_count']} instances)")
            results["recommendations"].append("Consider replacing special symbols with bullet points (•) or dashes (-)")
        
        return results
    
    def _analyze_length(self, text: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document length and provide recommendations based on experience"""
        results = {
            "length_score": 0,
            "word_count": 0,
            "estimated_pages": 0,
            "experience_years": 0,
            "recommended_pages": 0,
            "length_appropriate": False,
            "length_warnings": [],
            "length_recommendations": []
        }
        
        # Count words
        words = re.findall(r'\b\w+\b', text)
        results["word_count"] = len(words)
        
        # Estimate pages (approximately 250-300 words per page for resumes)
        results["estimated_pages"] = round(results["word_count"] / 275, 1)
        
        # Get experience years
        experience_data = extracted_data.get("experience", {}) if extracted_data else {}
        results["experience_years"] = experience_data.get("total_years", 0)
        
        # Determine recommended pages based on experience
        if results["experience_years"] <= 3:
            results["recommended_pages"] = 1
        elif results["experience_years"] <= 7:
            results["recommended_pages"] = 2  # 1-2 pages acceptable
        else:
            results["recommended_pages"] = 2  # Max 2 pages
        
        # Check length appropriateness
        if results["experience_years"] <= 3:
            # 0-3 years: should be 1 page
            if results["estimated_pages"] <= 1.2:
                results["length_appropriate"] = True
                results["length_score"] = 30
            else:
                results["length_warnings"].append(f"Resume is too long ({results['estimated_pages']} pages) for {results['experience_years']} years experience")
                results["length_recommendations"].append("Reduce to 1 page by focusing on most relevant experience")
        
        elif results["experience_years"] <= 7:
            # 3-7 years: 1-2 pages acceptable
            if 0.8 <= results["estimated_pages"] <= 2.2:
                results["length_appropriate"] = True
                results["length_score"] = 30
            elif results["estimated_pages"] < 0.8:
                results["length_warnings"].append("Resume may be too short - consider adding more details")
                results["length_recommendations"].append("Add more details about achievements and responsibilities")
            else:
                results["length_warnings"].append(f"Resume is too long ({results['estimated_pages']} pages)")
                results["length_recommendations"].append("Reduce to 2 pages maximum")
        
        else:
            # 7+ years: maximum 2 pages
            if 1.5 <= results["estimated_pages"] <= 2.2:
                results["length_appropriate"] = True
                results["length_score"] = 30
            elif results["estimated_pages"] < 1.5:
                results["length_warnings"].append("Resume may be too short for senior experience level")
                results["length_recommendations"].append("Include more leadership and strategic accomplishments")
            else:
                results["length_warnings"].append(f"Resume is too long ({results['estimated_pages']} pages)")
                results["length_recommendations"].append("Focus on most recent and relevant 10-15 years of experience")
        
        return results
    
    def _calculate_ats_score(self, file_checks: Dict[str, Any], layout_analysis: Dict[str, Any], 
                           content_analysis: Dict[str, Any], length_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall ATS compatibility score"""
        
        # Weighted scoring
        file_score = file_checks.get("format_score", 0)  # Max 50 points
        layout_score = layout_analysis.get("layout_score", 0)  # Max 50 points
        content_score = content_analysis.get("content_score", 0)  # Max 70 points
        length_score = length_analysis.get("length_score", 0)  # Max 30 points
        
        # Critical issues that significantly impact score
        critical_penalty = 0
        if file_checks.get("is_scanned_pdf", False):
            critical_penalty += 50  # Major penalty for scanned PDFs
        
        total_score = max(0, file_score + layout_score + content_score + length_score - critical_penalty)
        max_possible = 200
        
        percentage_score = min(100, (total_score / max_possible) * 100)
        
        return {
            "total_score": round(percentage_score, 1),
            "breakdown": {
                "file_format": round((file_score / 50) * 100, 1),
                "layout": round((layout_score / 50) * 100, 1),
                "content": round((content_score / 70) * 100, 1),
                "length": round((length_score / 30) * 100, 1)
            },
            "critical_penalty": critical_penalty > 0,
            "max_possible_score": 100
        }
    
    def _get_compatibility_level(self, score: float) -> str:
        """Get compatibility level description based on score"""
        if score >= 85:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 55:
            return "fair"
        elif score >= 40:
            return "poor"
        else:
            return "critical_issues"
    
    def _generate_ats_recommendations(self, file_checks: Dict[str, Any], layout_analysis: Dict[str, Any], 
                                    content_analysis: Dict[str, Any], length_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate prioritized ATS recommendations"""
        
        recommendations = {
            "critical": [],
            "high_priority": [],
            "medium_priority": [],
            "low_priority": []
        }
        
        # Critical issues (must fix)
        if file_checks.get("is_scanned_pdf", False):
            recommendations["critical"].append("Convert scanned PDF to searchable text format immediately")
        
        if not file_checks.get("is_preferred_format", False):
            recommendations["critical"].append("Convert document to PDF or DOCX format")
        
        if not content_analysis.get("contact_info_complete", False):
            recommendations["critical"].append("Add complete contact information (name, email, phone)")
        
        # High priority issues
        required_sections = ['experience', 'education', 'skills']
        missing_sections = [section for section in required_sections 
                          if not content_analysis.get("has_required_sections", {}).get(section, False)]
        
        for section in missing_sections:
            recommendations["high_priority"].append(f"Add clear '{section.title()}' section heading")
        
        if layout_analysis.get("has_multi_column", False):
            recommendations["high_priority"].append("Convert to single-column layout for better ATS parsing")
        
        if not length_analysis.get("length_appropriate", False):
            recommendations["high_priority"].extend(length_analysis.get("length_recommendations", []))
        
        # Medium priority issues
        if layout_analysis.get("excessive_tables", False):
            recommendations["medium_priority"].append("Reduce table usage, use simple formatting instead")
        
        if layout_analysis.get("excessive_textboxes", False):
            recommendations["medium_priority"].append("Replace text boxes with regular paragraph text")
        
        if content_analysis.get("excessive_symbols", False):
            recommendations["medium_priority"].append("Replace special symbols with standard formatting")
        
        # Low priority improvements
        if layout_analysis.get("excessive_images", False):
            recommendations["low_priority"].append("Remove non-essential images")
        
        recommendations["low_priority"].append("Use standard fonts (Arial, Calibri, Times New Roman)")
        recommendations["low_priority"].append("Ensure consistent formatting throughout document")
        recommendations["low_priority"].append("Use bullet points for lists instead of special characters")
        
        return recommendations
    
    def _get_priority_issues(self, file_checks: Dict[str, Any], layout_analysis: Dict[str, Any], 
                           content_analysis: Dict[str, Any], length_analysis: Dict[str, Any]) -> List[str]:
        """Get list of priority issues that need immediate attention"""
        
        priority_issues = []
        
        # Critical file format issues
        if file_checks.get("is_scanned_pdf", False):
            priority_issues.append("Scanned PDF detected - no searchable text")
        
        if not file_checks.get("is_preferred_format", False):
            priority_issues.append("Non-standard file format")
        
        # Critical content issues
        if not content_analysis.get("contact_info_complete", False):
            priority_issues.append("Incomplete contact information")
        
        # Missing essential sections
        required_sections = ['experience', 'education', 'skills']
        missing_sections = [section for section in required_sections 
                          if not content_analysis.get("has_required_sections", {}).get(section, False)]
        
        if missing_sections:
            priority_issues.append(f"Missing sections: {', '.join(missing_sections)}")
        
        # Layout issues
        if layout_analysis.get("has_multi_column", False):
            priority_issues.append("Multi-column layout detected")
        
        # Length issues
        if not length_analysis.get("length_appropriate", False):
            priority_issues.append("Inappropriate document length")
        
        return priority_issues


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python ats_analyzer.py '<file_path>' [extracted_text] [extracted_data_json]"
        }))
        sys.exit(1)
    
    try:
        file_path = sys.argv[1]
        extracted_text = sys.argv[2] if len(sys.argv) > 2 else None
        extracted_data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
        
        analyzer = ATSAnalyzer()
        result = analyzer.analyze_ats_compatibility(file_path, extracted_text, extracted_data)
        
        print(json.dumps(result, indent=2))
        
    except json.JSONDecodeError:
        print(json.dumps({
            "success": False,
            "error": "Invalid JSON in extracted_data parameter"
        }))
        sys.exit(1)
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"ATS analysis failed: {str(e)}"
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
