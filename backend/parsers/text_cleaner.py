"""
Text normalization and cleaning utilities for resume parsing
Handles text cleaning, section splitting, and bullet point extraction
"""

import re
import json
import sys
from typing import Dict, List, Any, Tuple


class TextNormalizer:
    """Handles text normalization and cleaning operations"""
    
    def __init__(self):
        # Common section heading patterns
        self.section_patterns = [
            r"^(EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT HISTORY|CAREER HISTORY)",
            r"^(EDUCATION|ACADEMIC BACKGROUND|EDUCATIONAL BACKGROUND|QUALIFICATIONS)",
            r"^(SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES|EXPERTISE|PROFICIENCIES)",
            r"^(SUMMARY|PROFESSIONAL SUMMARY|CAREER SUMMARY|PROFILE|OBJECTIVE)",
            r"^(PROJECTS|KEY PROJECTS|NOTABLE PROJECTS|PROJECT EXPERIENCE)",
            r"^(CERTIFICATIONS|LICENSES|CREDENTIALS|PROFESSIONAL CERTIFICATIONS)",
            r"^(AWARDS|HONORS|ACHIEVEMENTS|RECOGNITION)",
            r"^(CONTACT|CONTACT INFORMATION|PERSONAL DETAILS)",
            r"^(LANGUAGES|LANGUAGE SKILLS)",
            r"^(VOLUNTEER|VOLUNTEER EXPERIENCE|COMMUNITY SERVICE)",
            r"^(REFERENCES|PROFESSIONAL REFERENCES)",
            r"^(PUBLICATIONS|RESEARCH|PATENTS)"
        ]
        
        # Bullet point patterns
        self.bullet_patterns = [
            r"^\s*[\u2022\u2023\u25E6\u2043\u204C]\s+",  # Unicode bullet points
            r"^\s*[-\*\+]\s+",  # ASCII bullet points
            r"^\s*\d+\.\s+",    # Numbered lists
            r"^\s*[a-zA-Z]\.\s+",  # Lettered lists
            r"^\s*\([a-zA-Z0-9]+\)\s+",  # Parenthetical lists
        ]
        
        # Weird whitespace patterns to normalize
        self.whitespace_patterns = {
            r"\u00A0": " ",  # Non-breaking space
            r"\u2009": " ",  # Thin space
            r"\u200A": " ",  # Hair space
            r"\u2002": " ",  # En space
            r"\u2003": " ",  # Em space
            r"\u2004": " ",  # Three-per-em space
            r"\u2005": " ",  # Four-per-em space
            r"\u2006": " ",  # Six-per-em space
            r"\u2007": " ",  # Figure space
            r"\u2008": " ",  # Punctuation space
            r"\u200B": "",   # Zero-width space
            r"\u200C": "",   # Zero-width non-joiner
            r"\u200D": "",   # Zero-width joiner
            r"\uFEFF": "",   # Zero-width no-break space (BOM)
        }
    
    def normalize_text(self, text: str) -> Dict[str, Any]:
        """
        Normalize and clean text with comprehensive processing
        
        Args:
            text: Raw text content
            
        Returns:
            Dictionary containing normalized text and metadata
        """
        result = {
            "original": text,
            "normalized": "",
            "lowercase_copy": "",
            "sections": [],
            "bullet_points": [],
            "statistics": {},
            "cleaning_operations": []
        }
        
        # Start with the original text
        normalized = text
        operations = []
        
        # Step 1: Clean weird whitespace
        normalized, whitespace_ops = self._clean_whitespace(normalized)
        operations.extend(whitespace_ops)
        
        # Step 2: Collapse hyphenated line breaks
        normalized, hyphen_ops = self._collapse_hyphenated_breaks(normalized)
        operations.extend(hyphen_ops)
        
        # Step 3: Normalize line endings and extra spaces
        normalized, spacing_ops = self._normalize_spacing(normalized)
        operations.extend(spacing_ops)
        
        # Step 4: Create lowercase copy for matching
        lowercase_copy = normalized.lower()
        
        # Step 5: Split into sections
        sections = self._split_into_sections(normalized)
        
        # Step 6: Extract bullet points
        bullet_points = self._extract_bullet_points(normalized)
        
        # Step 7: Generate statistics
        statistics = self._generate_statistics(text, normalized, sections, bullet_points)
        
        result.update({
            "normalized": normalized,
            "lowercase_copy": lowercase_copy,
            "sections": sections,
            "bullet_points": bullet_points,
            "statistics": statistics,
            "cleaning_operations": operations
        })
        
        return result
    
    def _clean_whitespace(self, text: str) -> Tuple[str, List[str]]:
        """Clean weird whitespace characters"""
        operations = []
        cleaned = text
        
        for pattern, replacement in self.whitespace_patterns.items():
            if re.search(pattern, cleaned):
                cleaned = re.sub(pattern, replacement, cleaned)
                operations.append(f"Replaced {pattern} with '{replacement}'")
        
        return cleaned, operations
    
    def _collapse_hyphenated_breaks(self, text: str) -> Tuple[str, List[str]]:
        """Collapse hyphenated line breaks (word- \n word -> word)"""
        operations = []
        
        # Pattern for hyphenated line breaks: word-\n[optional whitespace]word
        pattern = r"(\w+)-\s*\n\s*(\w+)"
        
        matches = re.findall(pattern, text)
        if matches:
            text = re.sub(pattern, r"\1\2", text)
            operations.append(f"Collapsed {len(matches)} hyphenated line breaks")
        
        return text, operations
    
    def _normalize_spacing(self, text: str) -> Tuple[str, List[str]]:
        """Normalize spacing and line endings"""
        operations = []
        original_lines = len(text.split('\n'))
        
        # Normalize line endings
        text = re.sub(r'\r\n|\r', '\n', text)
        
        # Remove excessive whitespace at line ends
        text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
        operations.append("Removed trailing whitespace")
        
        # Collapse multiple spaces into single spaces (but preserve single line breaks)
        text = re.sub(r'[ \t]+', ' ', text)
        operations.append("Collapsed multiple spaces")
        
        # Remove excessive blank lines (more than 2 consecutive)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        new_lines = len(text.split('\n'))
        if new_lines != original_lines:
            operations.append(f"Normalized line count from {original_lines} to {new_lines}")
        
        return text.strip(), operations
    
    def _split_into_sections(self, text: str) -> List[Dict[str, Any]]:
        """Split text into sections based on headings"""
        sections = []
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check if line is a section heading
            is_heading = self._is_section_heading(line_stripped)
            
            if is_heading:
                # Save previous section if exists
                if current_section is not None:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_content).strip(),
                        "line_start": current_section_start,
                        "line_end": i - 1,
                        "word_count": len(' '.join(current_content).split()),
                        "line_count": len([c for c in current_content if c.strip()])
                    })
                
                # Start new section
                current_section = line_stripped
                current_section_start = i
                current_content = []
            else:
                # Add line to current section content
                if line_stripped:  # Skip empty lines for content
                    current_content.append(line)
        
        # Add the last section
        if current_section is not None:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content).strip(),
                "line_start": current_section_start,
                "line_end": len(lines) - 1,
                "word_count": len(' '.join(current_content).split()),
                "line_count": len([c for c in current_content if c.strip()])
            })
        
        return sections
    
    def _is_section_heading(self, line: str) -> bool:
        """Check if a line is likely a section heading"""
        if not line or len(line) < 3:
            return False
        
        # Check against known section patterns
        line_upper = line.upper()
        for pattern in self.section_patterns:
            if re.match(pattern, line_upper):
                return True
        
        # Additional heuristics for section headings
        # All caps and short
        if line.isupper() and len(line.split()) <= 4:
            return True
        
        # Ends with colon
        if line.endswith(':') and len(line.split()) <= 4:
            return True
        
        # Title case and short
        words = line.split()
        if (len(words) <= 4 and 
            all(word[0].isupper() if word else False for word in words) and
            len(line) < 50):
            return True
        
        return False
    
    def _extract_bullet_points(self, text: str) -> List[Dict[str, Any]]:
        """Extract bullet points from text"""
        bullet_points = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.bullet_patterns:
                if re.match(pattern, line):
                    # Extract the bullet content (remove bullet marker)
                    content = re.sub(pattern, '', line).strip()
                    
                    if content:  # Only add non-empty bullet points
                        bullet_points.append({
                            "line_number": i + 1,
                            "full_line": line,
                            "content": content,
                            "bullet_type": self._identify_bullet_type(line),
                            "word_count": len(content.split()),
                            "char_count": len(content)
                        })
                    break
        
        return bullet_points
    
    def _identify_bullet_type(self, line: str) -> str:
        """Identify the type of bullet point"""
        if re.match(r"^\s*[\u2022\u2023\u25E6\u2043\u204C]", line):
            return "unicode_bullet"
        elif re.match(r"^\s*[-]", line):
            return "dash"
        elif re.match(r"^\s*[\*]", line):
            return "asterisk"
        elif re.match(r"^\s*[+]", line):
            return "plus"
        elif re.match(r"^\s*\d+\.", line):
            return "numbered"
        elif re.match(r"^\s*[a-zA-Z]\.", line):
            return "lettered"
        elif re.match(r"^\s*\([a-zA-Z0-9]+\)", line):
            return "parenthetical"
        else:
            return "unknown"
    
    def _generate_statistics(self, original: str, normalized: str, sections: List[Dict], bullets: List[Dict]) -> Dict[str, Any]:
        """Generate statistics about the text processing"""
        return {
            "original_length": len(original),
            "normalized_length": len(normalized),
            "compression_ratio": len(normalized) / len(original) if original else 0,
            "original_lines": len(original.split('\n')),
            "normalized_lines": len(normalized.split('\n')),
            "original_words": len(original.split()),
            "normalized_words": len(normalized.split()),
            "sections_found": len(sections),
            "bullet_points_found": len(bullets),
            "bullet_types": list(set(b["bullet_type"] for b in bullets)),
            "avg_section_length": sum(s["word_count"] for s in sections) / len(sections) if sections else 0,
            "avg_bullet_length": sum(b["word_count"] for b in bullets) / len(bullets) if bullets else 0
        }


def main():
    """Main function for command line usage"""
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python text_normalizer.py '<text_content>'"
        }))
        sys.exit(1)
    
    text = sys.argv[1]
    normalizer = TextNormalizer()
    result = normalizer.normalize_text(text)
    
    # Add success flag
    result["success"] = True
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
