"""
Resume section detection and analysis
Identifies common resume sections using pattern matching
"""

import re
import json
import sys
from typing import Dict, List, Any, Tuple


class SectionDetector:
    """Detects and analyzes resume sections"""
    
    def __init__(self):
        # Define section patterns (case-insensitive)
        self.section_patterns = {
            "contact": [
                r"contact\s+information",
                r"personal\s+details",
                r"contact\s+details",
                r"personal\s+information"
            ],
            "summary": [
                r"professional\s+summary",
                r"career\s+summary",
                r"summary\s+of\s+qualifications",
                r"executive\s+summary",
                r"profile",
                r"objective",
                r"career\s+objective"
            ],
            "experience": [
                r"work\s+experience",
                r"professional\s+experience",
                r"employment\s+history",
                r"career\s+history",
                r"work\s+history",
                r"experience",
                r"employment"
            ],
            "education": [
                r"education",
                r"academic\s+background",
                r"educational\s+background",
                r"qualifications",
                r"academic\s+qualifications"
            ],
            "skills": [
                r"technical\s+skills",
                r"core\s+competencies",
                r"skills\s+and\s+abilities",
                r"key\s+skills",
                r"competencies",
                r"skills"
            ],
            "projects": [
                r"projects",
                r"key\s+projects",
                r"notable\s+projects",
                r"project\s+experience"
            ],
            "certifications": [
                r"certifications",
                r"certificates",
                r"professional\s+certifications",
                r"licenses\s+and\s+certifications"
            ],
            "awards": [
                r"awards",
                r"honors",
                r"achievements",
                r"recognitions",
                r"awards\s+and\s+honors"
            ],
            "languages": [
                r"languages",
                r"language\s+skills",
                r"foreign\s+languages"
            ],
            "references": [
                r"references",
                r"professional\s+references",
                r"references\s+available"
            ]
        }
        
        # Contact information patterns
        self.contact_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
            "linkedin": r"(?:linkedin\.com/in/|linkedin\.com/pub/)([A-Za-z0-9-]+)",
            "github": r"(?:github\.com/)([A-Za-z0-9-]+)",
            "website": r"(?:https?://)?(www\.)?([A-Za-z0-9-]+\.[A-Za-z]{2,})"
        }
    
    def detect_sections(self, text: str) -> Dict[str, Any]:
        """
        Detect resume sections from text
        
        Args:
            text: Resume text content
            
        Returns:
            Dictionary containing detected sections and analysis
        """
        result = {
            "success": False,
            "sections": [],
            "contact_info": {},
            "structure_analysis": {},
            "error": None
        }
        
        try:
            lines = text.split('\n')
            sections = []
            contact_info = self._extract_contact_info(text)
            
            # Find section headers
            for i, line in enumerate(lines):
                line_clean = line.strip()
                if not line_clean:
                    continue
                
                # Check if line matches any section pattern
                for section_type, patterns in self.section_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, line_clean, re.IGNORECASE):
                            # Find section content
                            section_content = self._extract_section_content(lines, i)
                            confidence = self._calculate_confidence(section_type, section_content)
                            
                            section = {
                                "type": section_type,
                                "title": line_clean,
                                "content": section_content,
                                "start_line": i + 1,
                                "end_line": min(i + len(section_content.split('\n')), len(lines)),
                                "confidence": confidence,
                                "keywords_found": self._find_keywords(section_type, section_content),
                                "word_count": len(section_content.split())
                            }
                            sections.append(section)
                            break
            
            # Remove duplicates and overlaps
            sections = self._remove_duplicate_sections(sections)
            
            # Structure analysis
            structure_analysis = self._analyze_structure(sections, contact_info)
            
            result.update({
                "success": True,
                "sections": sections,
                "contact_info": contact_info,
                "structure_analysis": structure_analysis
            })
            
        except Exception as e:
            result["error"] = f"Section detection error: {str(e)}"
            
        return result
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from text"""
        contact_info = {}
        
        for info_type, pattern in self.contact_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if info_type == "phone":
                    # Clean up phone number
                    phone_match = matches[0]
                    if isinstance(phone_match, tuple):
                        phone = ''.join(phone_match)
                    else:
                        phone = phone_match
                    contact_info[info_type] = re.sub(r'[^\d+]', '', phone)
                elif info_type in ["linkedin", "github"]:
                    contact_info[info_type] = matches[0]
                else:
                    contact_info[info_type] = matches[0]
        
        return contact_info
    
    def _extract_section_content(self, lines: List[str], start_index: int) -> str:
        """Extract content for a section starting at given index"""
        content_lines = []
        
        # Look ahead for content until next section or end
        for i in range(start_index + 1, len(lines)):
            line = lines[i].strip()
            
            # Stop if we hit another section header
            if self._is_section_header(line):
                break
                
            if line:  # Only add non-empty lines
                content_lines.append(line)
            
            # Limit content length
            if len(content_lines) > 20:
                break
        
        return '\n'.join(content_lines)
    
    def _is_section_header(self, line: str) -> bool:
        """Check if line is likely a section header"""
        for patterns in self.section_patterns.values():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return True
        return False
    
    def _calculate_confidence(self, section_type: str, content: str) -> float:
        """Calculate confidence score for section detection"""
        base_confidence = 0.7
        
        # Section-specific keywords for confidence boost
        keywords = {
            "experience": ["worked", "responsible", "managed", "developed", "led", "achieved"],
            "education": ["university", "college", "degree", "bachelor", "master", "phd", "gpa"],
            "skills": ["proficient", "experienced", "knowledge", "familiar", "programming"],
            "projects": ["project", "developed", "built", "created", "implemented"],
            "certifications": ["certified", "license", "credential", "certification"]
        }
        
        if section_type in keywords:
            keyword_count = sum(1 for keyword in keywords[section_type] 
                              if keyword.lower() in content.lower())
            confidence_boost = min(keyword_count * 0.05, 0.3)
            base_confidence += confidence_boost
        
        return min(base_confidence, 1.0)
    
    def _find_keywords(self, section_type: str, content: str) -> List[str]:
        """Find relevant keywords in section content"""
        keywords = {
            "experience": ["worked", "responsible", "managed", "developed", "led", "achieved"],
            "education": ["university", "college", "degree", "bachelor", "master", "phd"],
            "skills": ["proficient", "experienced", "knowledge", "programming", "software"],
            "projects": ["project", "developed", "built", "created", "implemented"],
            "certifications": ["certified", "license", "credential", "certification"]
        }
        
        found_keywords = []
        if section_type in keywords:
            content_lower = content.lower()
            found_keywords = [kw for kw in keywords[section_type] 
                            if kw in content_lower]
        
        return found_keywords
    
    def _remove_duplicate_sections(self, sections: List[Dict]) -> List[Dict]:
        """Remove duplicate or overlapping sections"""
        # Sort by start line
        sections.sort(key=lambda x: x["start_line"])
        
        # Remove duplicates by type
        seen_types = set()
        unique_sections = []
        
        for section in sections:
            if section["type"] not in seen_types:
                unique_sections.append(section)
                seen_types.add(section["type"])
        
        return unique_sections
    
    def _analyze_structure(self, sections: List[Dict], contact_info: Dict) -> Dict[str, Any]:
        """Analyze overall resume structure"""
        section_types = [s["type"] for s in sections]
        
        analysis = {
            "total_sections": len(sections),
            "sections_found": section_types,
            "has_contact": bool(contact_info),
            "has_experience": "experience" in section_types,
            "has_education": "education" in section_types,
            "has_skills": "skills" in section_types,
            "avg_confidence": sum(s["confidence"] for s in sections) / len(sections) if sections else 0,
            "structure_quality": "unknown",
            "recommendations": []
        }
        
        # Determine structure quality
        essential_sections = ["experience", "education", "skills"]
        has_essentials = sum(1 for sec in essential_sections if sec in section_types)
        
        if has_essentials >= 3 and contact_info:
            analysis["structure_quality"] = "excellent"
        elif has_essentials >= 2:
            analysis["structure_quality"] = "good"
        elif has_essentials >= 1:
            analysis["structure_quality"] = "fair"
        else:
            analysis["structure_quality"] = "poor"
        
        # Generate recommendations
        if not contact_info:
            analysis["recommendations"].append("Add contact information")
        if "experience" not in section_types:
            analysis["recommendations"].append("Add work experience section")
        if "education" not in section_types:
            analysis["recommendations"].append("Add education section")
        if "skills" not in section_types:
            analysis["recommendations"].append("Add skills section")
        
        return analysis


def main():
    """Main function for command line usage"""
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python section_detector.py '<resume_text>'"
        }))
        sys.exit(1)
    
    text = sys.argv[1]
    detector = SectionDetector()
    result = detector.detect_sections(text)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
