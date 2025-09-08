"""
Resume Quality Scorer - Transparent rubric-based evaluation system
Provides detailed scoring with actionable recommendations for improvement
"""

import re
import statistics
from typing import Dict, Any, List, Tuple
from collections import Counter


class ResumeQualityScorer:
    """
    Comprehensive resume quality scoring system with transparent rubrics
    
    Scoring Breakdown (0-100 total):
    - Content Fit (40%): Skills coverage (30) + Experience alignment (10)
    - Clarity & Quantification (25%): Metrics usage (15) + Action verbs (10) 
    - Structure & Readability (20%): Key sections (10) + Sentence quality (10)
    - ATS Friendliness (15%): Format compatibility (15)
    """
    
    def __init__(self):
        self.max_scores = {
            "content_fit": 40,
            "clarity_quantification": 25, 
            "structure_readability": 20,
            "ats_friendliness": 15
        }
        
        self.action_verbs = {
            'strong': [
                'achieved', 'built', 'created', 'designed', 'developed', 'directed', 'established',
                'generated', 'implemented', 'improved', 'increased', 'launched', 'led', 'managed',
                'optimized', 'organized', 'produced', 'reduced', 'restructured', 'solved', 
                'streamlined', 'transformed', 'upgraded'
            ],
            'moderate': [
                'administered', 'analyzed', 'assisted', 'collaborated', 'coordinated', 'delivered',
                'executed', 'facilitated', 'maintained', 'operated', 'participated', 'performed',
                'processed', 'provided', 'supported', 'utilized', 'worked'
            ],
            'weak': [
                'responsible for', 'duties included', 'involved in', 'helped with', 'tasked with'
            ]
        }
        
        self.metric_patterns = [
            r'\b\d+%',  # Percentages
            r'\$\d+[\d,]*(?:\.\d+)?[kmb]?',  # Money amounts
            r'\b\d+[\d,]*\+?\s*(?:users?|customers?|clients?)',  # User counts
            r'\b\d+[\d,]*\s*(?:ms|seconds?|minutes?|hours?|days?)',  # Time
            r'\b\d+[\d,]*x\b',  # Multipliers
            r'\b\d+[\d,]*\s*(?:GB|MB|TB)',  # Data sizes
            r'\b\d+[\d,]*\s*(?:requests?|transactions?|operations?)',  # Volume metrics
            r'\b(?:improved|increased|reduced|decreased)\s+(?:by\s+)?\d+',  # Improvement metrics
            r'\b\d+[\d,]*\s*(?:lines?|functions?|components?|features?)',  # Code metrics
        ]
        
        self.required_sections = {
            'experience': ['experience', 'work', 'employment', 'professional', 'career'],
            'education': ['education', 'academic', 'university', 'college', 'degree'],
            'skills': ['skills', 'technical', 'technologies', 'tools', 'competencies'],
            'contact': ['contact', 'phone', 'email', 'address', 'linkedin']
        }
    
    def score_resume_quality(self, extracted_text: str, extracted_data: Dict[str, Any] = None, 
                           target_skills: List[str] = None, target_experience_years: int = None,
                           ats_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive resume quality scoring with detailed breakdowns
        
        Args:
            extracted_text: Full resume text
            extracted_data: Structured data from information extraction
            target_skills: Target skills for role (optional)
            target_experience_years: Target years of experience (optional)
            ats_analysis: ATS compatibility analysis results (optional)
            
        Returns:
            Detailed quality score with subscores and recommendations
        """
        
        # Content Fit Scoring (40 points max)
        content_fit_score, content_fit_details = self._score_content_fit(
            extracted_data, target_skills, target_experience_years
        )
        
        # Clarity & Quantification Scoring (25 points max)
        clarity_score, clarity_details = self._score_clarity_quantification(extracted_text)
        
        # Structure & Readability Scoring (20 points max)
        structure_score, structure_details = self._score_structure_readability(extracted_text)
        
        # ATS Friendliness Scoring (15 points max)
        ats_score, ats_details = self._score_ats_friendliness(ats_analysis, extracted_text)
        
        # Calculate total score
        total_score = content_fit_score + clarity_score + structure_score + ats_score
        
        # Generate overall recommendations
        recommendations = self._generate_quality_recommendations(
            content_fit_details, clarity_details, structure_details, ats_details
        )
        
        # Determine overall quality level
        quality_level = self._get_quality_level(total_score)
        
        return {
            "overall_score": round(total_score, 1),
            "quality_level": quality_level,
            "score_breakdown": {
                "content_fit": {
                    "score": round(content_fit_score, 1),
                    "max_possible": self.max_scores["content_fit"],
                    "percentage": round((content_fit_score / self.max_scores["content_fit"]) * 100, 1),
                    "details": content_fit_details
                },
                "clarity_quantification": {
                    "score": round(clarity_score, 1),
                    "max_possible": self.max_scores["clarity_quantification"],
                    "percentage": round((clarity_score / self.max_scores["clarity_quantification"]) * 100, 1),
                    "details": clarity_details
                },
                "structure_readability": {
                    "score": round(structure_score, 1),
                    "max_possible": self.max_scores["structure_readability"],
                    "percentage": round((structure_score / self.max_scores["structure_readability"]) * 100, 1),
                    "details": structure_details
                },
                "ats_friendliness": {
                    "score": round(ats_score, 1),
                    "max_possible": self.max_scores["ats_friendliness"],
                    "percentage": round((ats_score / self.max_scores["ats_friendliness"]) * 100, 1),
                    "details": ats_details
                }
            },
            "recommendations": recommendations,
            "scoring_rubric": {
                "description": "Transparent 0-100 point system",
                "categories": {
                    "Content Fit (40%)": "Skills coverage (30) + Experience alignment (10)",
                    "Clarity & Quantification (25%)": "Metrics usage (15) + Action verbs (10)",
                    "Structure & Readability (20%)": "Key sections (10) + Sentence quality (10)",
                    "ATS Friendliness (15%)": "Format compatibility (15)"
                }
            }
        }
    
    def _score_content_fit(self, extracted_data: Dict[str, Any], target_skills: List[str] = None, 
                          target_experience_years: int = None) -> Tuple[float, Dict[str, Any]]:
        """Score content fit against target requirements (40 points max)"""
        
        details = {
            "skills_coverage_score": 0,
            "experience_alignment_score": 0,
            "skills_analysis": {},
            "experience_analysis": {},
            "recommendations": []
        }
        
        total_score = 0
        
        # Skills Coverage (30 points max)
        if extracted_data and target_skills:
            skills_score, skills_analysis = self._analyze_skills_coverage(extracted_data, target_skills)
            details["skills_coverage_score"] = skills_score
            details["skills_analysis"] = skills_analysis
            total_score += skills_score
        elif extracted_data:
            # Partial scoring based on skill diversity without target
            skills_data = extracted_data.get("skills", {})
            total_skills = skills_data.get("total_skills_found", 0)
            skills_score = min(total_skills * 2, 20)  # Up to 20 points for skill diversity
            details["skills_coverage_score"] = skills_score
            details["skills_analysis"] = {
                "total_skills_found": total_skills,
                "coverage_type": "diversity_based",
                "note": "Scored on skill diversity - provide target skills for better analysis"
            }
            total_score += skills_score
            details["recommendations"].append("Provide target skills for more accurate content fit analysis")
        
        # Experience Alignment (10 points max)
        if extracted_data:
            exp_score, exp_analysis = self._analyze_experience_alignment(extracted_data, target_experience_years)
            details["experience_alignment_score"] = exp_score
            details["experience_analysis"] = exp_analysis
            total_score += exp_score
        
        return total_score, details
    
    def _analyze_skills_coverage(self, extracted_data: Dict[str, Any], target_skills: List[str]) -> Tuple[float, Dict[str, Any]]:
        """Analyze skills coverage against target (30 points max)"""
        
        # Get resume skills
        skills_data = extracted_data.get("skills", {})
        resume_skills = []
        
        for category in ["programming_languages", "web_technologies", "databases", "cloud_platforms", "tools_frameworks", "soft_skills"]:
            resume_skills.extend(skills_data.get(category, []))
        
        resume_skills.extend(skills_data.get("matched_skills", []))
        resume_skills_lower = set(skill.lower().strip() for skill in resume_skills if skill)
        
        # Calculate coverage
        target_skills_lower = set(skill.lower().strip() for skill in target_skills if skill)
        matched_skills = resume_skills_lower & target_skills_lower
        
        if target_skills_lower:
            coverage_percentage = len(matched_skills) / len(target_skills_lower)
            coverage_score = coverage_percentage * 30  # Max 30 points
        else:
            coverage_percentage = 0
            coverage_score = 0
        
        analysis = {
            "target_skills_count": len(target_skills_lower),
            "matched_skills_count": len(matched_skills),
            "coverage_percentage": round(coverage_percentage * 100, 1),
            "matched_skills": list(matched_skills),
            "missing_skills": list(target_skills_lower - resume_skills_lower),
            "bonus_skills": list(resume_skills_lower - target_skills_lower)
        }
        
        return coverage_score, analysis
    
    def _analyze_experience_alignment(self, extracted_data: Dict[str, Any], target_experience_years: int = None) -> Tuple[float, Dict[str, Any]]:
        """Analyze experience alignment with target (10 points max)"""
        
        experience_data = extracted_data.get("experience", {})
        total_years = experience_data.get("total_years", 0)
        career_level = experience_data.get("career_level", "entry")
        
        analysis = {
            "actual_years": total_years,
            "target_years": target_experience_years,
            "career_level": career_level,
            "alignment_type": "none"
        }
        
        if target_experience_years is not None:
            # Score based on how close actual experience is to target
            if total_years >= target_experience_years:
                # Perfect match or over-qualified
                score = 10
                analysis["alignment_type"] = "meets_or_exceeds"
            elif total_years >= target_experience_years * 0.8:
                # Close to target (80%+)
                score = 8
                analysis["alignment_type"] = "close_match"
            elif total_years >= target_experience_years * 0.6:
                # Somewhat close (60%+)
                score = 6
                analysis["alignment_type"] = "partial_match"
            elif total_years >= target_experience_years * 0.4:
                # Below target but some experience
                score = 4
                analysis["alignment_type"] = "below_target"
            else:
                # Significantly below target
                score = 2
                analysis["alignment_type"] = "well_below_target"
        else:
            # Score based on career progression without specific target
            if total_years >= 7:
                score = 10  # Senior level
            elif total_years >= 3:
                score = 8   # Mid level
            elif total_years >= 1:
                score = 6   # Junior level
            else:
                score = 4   # Entry level
            analysis["alignment_type"] = "general_assessment"
        
        return score, analysis
    
    def _score_clarity_quantification(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Score clarity and quantification (25 points max)"""
        
        details = {
            "metrics_score": 0,
            "action_verbs_score": 0,
            "metrics_analysis": {},
            "action_verbs_analysis": {},
            "recommendations": []
        }
        
        total_score = 0
        
        # Metrics Usage (15 points max)
        metrics_score, metrics_analysis = self._analyze_metrics_usage(text)
        details["metrics_score"] = metrics_score
        details["metrics_analysis"] = metrics_analysis
        total_score += metrics_score
        
        # Action Verbs (10 points max)
        verbs_score, verbs_analysis = self._analyze_action_verbs(text)
        details["action_verbs_score"] = verbs_score
        details["action_verbs_analysis"] = verbs_analysis
        total_score += verbs_score
        
        return total_score, details
    
    def _analyze_metrics_usage(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Analyze usage of quantifiable metrics (15 points max)"""
        
        lines = text.split('\n')
        bullet_lines = [line.strip() for line in lines if line.strip().startswith('•') or line.strip().startswith('-') or line.strip().startswith('*')]
        
        if not bullet_lines:
            # Also check for numbered achievements or bullet-like patterns
            bullet_lines = [line.strip() for line in lines if re.match(r'^\s*[•\-\*▪▫]\s*', line) or re.match(r'^\s*\d+[\.\)]\s*', line)]
        
        total_bullets = len(bullet_lines)
        metrics_found = []
        lines_with_metrics = 0
        
        # Find metrics in bullet points
        for line in bullet_lines:
            line_metrics = []
            for pattern in self.metric_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                line_metrics.extend(matches)
            
            if line_metrics:
                lines_with_metrics += 1
                metrics_found.extend(line_metrics)
        
        # Calculate score
        if total_bullets > 0:
            metrics_percentage = lines_with_metrics / total_bullets
            metrics_score = min(metrics_percentage * 15, 15)  # Max 15 points
        else:
            metrics_percentage = 0
            metrics_score = 0
        
        analysis = {
            "total_bullet_points": total_bullets,
            "lines_with_metrics": lines_with_metrics,
            "metrics_percentage": round(metrics_percentage * 100, 1),
            "total_metrics_found": len(metrics_found),
            "sample_metrics": metrics_found[:10],  # Show first 10 examples
            "improvement_potential": max(0, total_bullets - lines_with_metrics)
        }
        
        return metrics_score, analysis
    
    def _analyze_action_verbs(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Analyze usage of strong action verbs (10 points max)"""
        
        lines = text.split('\n')
        bullet_lines = [line.strip() for line in lines if line.strip().startswith('•') or line.strip().startswith('-') or line.strip().startswith('*')]
        
        if not bullet_lines:
            bullet_lines = [line.strip() for line in lines if re.match(r'^\s*[•\-\*▪▫]\s*', line) or re.match(r'^\s*\d+[\.\)]\s*', line)]
        
        total_bullets = len(bullet_lines)
        verb_analysis = {
            'strong': 0,
            'moderate': 0,
            'weak': 0,
            'none': 0
        }
        
        found_verbs = []
        
        for line in bullet_lines:
            # Extract the first few words to check for action verbs
            clean_line = re.sub(r'^[•\-\*▪▫\d\.\)]\s*', '', line).strip()
            first_words = clean_line.split()[:3]
            first_phrase = ' '.join(first_words).lower()
            
            verb_found = False
            verb_strength = 'none'
            
            # Check for strong verbs
            for verb in self.action_verbs['strong']:
                if first_phrase.startswith(verb):
                    verb_analysis['strong'] += 1
                    found_verbs.append(verb)
                    verb_found = True
                    verb_strength = 'strong'
                    break
            
            # Check for moderate verbs if no strong verb found
            if not verb_found:
                for verb in self.action_verbs['moderate']:
                    if first_phrase.startswith(verb):
                        verb_analysis['moderate'] += 1
                        found_verbs.append(verb)
                        verb_found = True
                        verb_strength = 'moderate'
                        break
            
            # Check for weak patterns
            if not verb_found:
                for pattern in self.action_verbs['weak']:
                    if pattern in first_phrase:
                        verb_analysis['weak'] += 1
                        verb_found = True
                        verb_strength = 'weak'
                        break
            
            if not verb_found:
                verb_analysis['none'] += 1
        
        # Calculate score
        if total_bullets > 0:
            strong_percentage = verb_analysis['strong'] / total_bullets
            moderate_percentage = verb_analysis['moderate'] / total_bullets
            
            # Strong verbs get full points, moderate gets partial
            verb_score = (strong_percentage * 10) + (moderate_percentage * 6)
            verb_score = min(verb_score, 10)  # Max 10 points
        else:
            verb_score = 0
        
        analysis = {
            "total_bullet_points": total_bullets,
            "verb_distribution": verb_analysis,
            "strong_verb_percentage": round((verb_analysis['strong'] / total_bullets * 100) if total_bullets > 0 else 0, 1),
            "sample_verbs_found": list(set(found_verbs))[:10],
            "weak_or_missing_count": verb_analysis['weak'] + verb_analysis['none']
        }
        
        return verb_score, analysis
    
    def _score_structure_readability(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Score structure and readability (20 points max)"""
        
        details = {
            "sections_score": 0,
            "readability_score": 0,
            "sections_analysis": {},
            "readability_analysis": {},
            "recommendations": []
        }
        
        total_score = 0
        
        # Key Sections (10 points max)
        sections_score, sections_analysis = self._analyze_key_sections(text)
        details["sections_score"] = sections_score
        details["sections_analysis"] = sections_analysis
        total_score += sections_score
        
        # Readability (10 points max)
        readability_score, readability_analysis = self._analyze_readability(text)
        details["readability_score"] = readability_score
        details["readability_analysis"] = readability_analysis
        total_score += readability_score
        
        return total_score, details
    
    def _analyze_key_sections(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Analyze presence of key resume sections (10 points max)"""
        
        text_lower = text.lower()
        sections_found = {}
        
        for section_name, keywords in self.required_sections.items():
            found = False
            for keyword in keywords:
                # Look for keywords as section headers (short lines)
                lines = text.split('\n')
                for line in lines:
                    line_clean = line.strip().lower()
                    if len(line_clean) < 50 and keyword in line_clean:
                        # Additional check: line should be relatively standalone
                        if any(kw == line_clean or line_clean.startswith(kw) for kw in keywords):
                            found = True
                            break
                if found:
                    break
            sections_found[section_name] = found
        
        # Calculate score
        found_count = sum(sections_found.values())
        required_count = len(self.required_sections)
        sections_score = (found_count / required_count) * 10  # Max 10 points
        
        analysis = {
            "required_sections": list(self.required_sections.keys()),
            "sections_found": sections_found,
            "found_count": found_count,
            "required_count": required_count,
            "completion_percentage": round((found_count / required_count) * 100, 1),
            "missing_sections": [section for section, found in sections_found.items() if not found]
        }
        
        return sections_score, analysis
    
    def _analyze_readability(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Analyze sentence length and passive voice (10 points max)"""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        if not sentences:
            return 0, {"error": "No readable sentences found"}
        
        # Analyze sentence lengths
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = statistics.mean(sentence_lengths) if sentence_lengths else 0
        long_sentences = [s for s in sentence_lengths if s > 25]  # Consider >25 words as long
        
        # Analyze passive voice patterns
        passive_patterns = [
            r'\b(?:was|were|is|are|been|being)\s+\w+ed\b',  # was/were + past participle
            r'\b(?:was|were|is|are)\s+\w+en\b',  # was/were + past participle ending in 'en'
            r'\bby\s+(?:the\s+)?[A-Z]\w*',  # "by [Company/Person]" pattern
        ]
        
        passive_sentences = 0
        for sentence in sentences:
            for pattern in passive_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    passive_sentences += 1
                    break
        
        # Calculate readability score
        readability_score = 10  # Start with max points
        
        # Deduct for overly long sentences
        if len(long_sentences) > len(sentences) * 0.3:  # More than 30% long sentences
            readability_score -= 3
        elif len(long_sentences) > len(sentences) * 0.2:  # More than 20% long sentences
            readability_score -= 2
        
        # Deduct for excessive passive voice
        passive_percentage = passive_sentences / len(sentences) if sentences else 0
        if passive_percentage > 0.3:  # More than 30% passive
            readability_score -= 4
        elif passive_percentage > 0.2:  # More than 20% passive
            readability_score -= 2
        
        # Deduct for extremely short or long average sentence length
        if avg_sentence_length < 5:  # Too short, might be fragmented
            readability_score -= 2
        elif avg_sentence_length > 20:  # Too long, might be complex
            readability_score -= 2
        
        readability_score = max(0, readability_score)  # Don't go below 0
        
        analysis = {
            "total_sentences": len(sentences),
            "average_sentence_length": round(avg_sentence_length, 1),
            "long_sentences_count": len(long_sentences),
            "long_sentences_percentage": round((len(long_sentences) / len(sentences)) * 100, 1),
            "passive_sentences_count": passive_sentences,
            "passive_voice_percentage": round(passive_percentage * 100, 1),
            "readability_issues": []
        }
        
        # Add specific issues
        if len(long_sentences) > len(sentences) * 0.2:
            analysis["readability_issues"].append(f"{len(long_sentences)} sentences are too long (>25 words)")
        if passive_percentage > 0.2:
            analysis["readability_issues"].append(f"{passive_sentences} sentences use passive voice")
        if avg_sentence_length < 5:
            analysis["readability_issues"].append("Average sentence length is too short")
        elif avg_sentence_length > 20:
            analysis["readability_issues"].append("Average sentence length is too long")
        
        return readability_score, analysis
    
    def _score_ats_friendliness(self, ats_analysis: Dict[str, Any] = None, text: str = None) -> Tuple[float, Dict[str, Any]]:
        """Score ATS friendliness (15 points max)"""
        
        if ats_analysis:
            # Use existing ATS analysis
            ats_score_data = ats_analysis.get("ats_score", {})
            total_ats_score = ats_score_data.get("total_score", 0)
            
            # Convert ATS score (0-100) to our scale (0-15)
            score = (total_ats_score / 100) * 15
            
            details = {
                "score_source": "ats_analysis",
                "original_ats_score": total_ats_score,
                "compatibility_level": ats_analysis.get("compatibility_level", "unknown"),
                "priority_issues": ats_analysis.get("priority_issues", []),
                "format_analysis": ats_analysis.get("file_format_analysis", {}),
                "layout_analysis": ats_analysis.get("layout_analysis", {}),
                "recommendations": []
            }
            
            # Add specific recommendations based on ATS issues
            if ats_analysis.get("priority_issues"):
                details["recommendations"].extend(ats_analysis.get("priority_issues", [])[:3])
            
        else:
            # Fallback: basic ATS heuristics from text analysis
            score, details = self._basic_ats_analysis(text)
        
        return score, details
    
    def _basic_ats_analysis(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """Basic ATS analysis when detailed analysis not available (15 points max)"""
        
        score = 15  # Start with max points
        issues = []
        
        # Check for problematic symbols
        problematic_symbols = ['★', '☆', '●', '◆', '▲', '▼', '♦', '♠', '♥', '♣', '✓', '✗', '→', '←']
        symbol_count = sum(text.count(symbol) for symbol in problematic_symbols)
        
        if symbol_count > 5:
            score -= 5
            issues.append(f"Excessive special symbols ({symbol_count} found)")
        elif symbol_count > 0:
            score -= 2
            issues.append(f"Some special symbols detected ({symbol_count} found)")
        
        # Check for table-like structures (multiple tabs or excessive spacing)
        lines = text.split('\n')
        table_like_lines = [line for line in lines if line.count('\t') > 2 or len(re.findall(r'  +', line)) > 3]
        
        if len(table_like_lines) > len(lines) * 0.2:  # More than 20% table-like
            score -= 4
            issues.append("Potential table formatting detected")
        
        # Check for complex formatting patterns
        complex_patterns = [
            r'[│┌┐└┘├┤┬┴┼]',  # Box drawing characters
            r'[═║╔╗╚╝╠╣╦╩╬]',  # Double box drawing
            r'[▓▒░]',  # Block characters
        ]
        
        complex_formatting = sum(len(re.findall(pattern, text)) for pattern in complex_patterns)
        if complex_formatting > 0:
            score -= 3
            issues.append("Complex formatting characters detected")
        
        score = max(0, score)
        
        details = {
            "score_source": "basic_heuristics",
            "symbol_count": symbol_count,
            "table_like_lines": len(table_like_lines),
            "complex_formatting_count": complex_formatting,
            "detected_issues": issues,
            "recommendations": [
                "Use standard bullet points (• or -) instead of special symbols",
                "Avoid table formatting, use simple text layout",
                "Stick to standard fonts and formatting"
            ] if issues else ["Good ATS formatting detected"]
        }
        
        return score, details
    
    def _generate_quality_recommendations(self, content_fit: Dict, clarity: Dict, 
                                        structure: Dict, ats: Dict) -> Dict[str, List[str]]:
        """Generate prioritized recommendations for improvement"""
        
        recommendations = {
            "critical": [],
            "high_priority": [],
            "medium_priority": [],
            "low_priority": []
        }
        
        # Critical issues (score <50% in any category)
        if content_fit.get("skills_coverage_score", 0) < 15:  # <50% of 30 points
            recommendations["critical"].append("Improve skills alignment with target requirements")
        
        if clarity.get("metrics_score", 0) < 7.5:  # <50% of 15 points
            recommendations["critical"].append("Add quantifiable metrics and achievements to bullet points")
        
        if structure.get("sections_score", 0) < 5:  # <50% of 10 points
            recommendations["critical"].append("Add missing resume sections (Experience, Education, Skills)")
        
        # High priority issues
        if clarity.get("action_verbs_score", 0) < 7:  # <70% of 10 points
            recommendations["high_priority"].append("Start bullet points with strong action verbs (achieved, built, led)")
        
        if structure.get("readability_score", 0) < 7:  # <70% of 10 points
            recommendations["high_priority"].append("Improve sentence structure and reduce passive voice")
        
        if ats.get("score", 0) < 10:  # <67% of 15 points
            recommendations["high_priority"].append("Improve ATS compatibility by simplifying formatting")
        
        # Medium priority improvements
        metrics_analysis = clarity.get("metrics_analysis", {})
        if metrics_analysis.get("improvement_potential", 0) > 0:
            recommendations["medium_priority"].append(
                f"Add metrics to {metrics_analysis['improvement_potential']} more bullet points"
            )
        
        verbs_analysis = clarity.get("action_verbs_analysis", {})
        if verbs_analysis.get("weak_or_missing_count", 0) > 0:
            recommendations["medium_priority"].append(
                f"Strengthen {verbs_analysis['weak_or_missing_count']} bullet points with better action verbs"
            )
        
        # Low priority enhancements
        recommendations["low_priority"].extend([
            "Consider adding more specific technical skills",
            "Include soft skills and leadership examples",
            "Ensure consistent formatting throughout document",
            "Add links to portfolio or professional profiles"
        ])
        
        return recommendations
    
    def _get_quality_level(self, score: float) -> str:
        """Get quality level description based on total score"""
        if score >= 85:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 65:
            return "average"
        elif score >= 50:
            return "below_average"
        else:
            return "needs_improvement"


def main():
    """Main function for command line testing"""
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python quality_scorer.py '<resume_text>' [extracted_data_json] [target_skills_json] [target_years] [ats_analysis_json]")
        sys.exit(1)
    
    text = sys.argv[1]
    extracted_data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
    target_skills = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    target_years = int(sys.argv[4]) if len(sys.argv) > 4 else None
    ats_analysis = json.loads(sys.argv[5]) if len(sys.argv) > 5 else None
    
    scorer = ResumeQualityScorer()
    result = scorer.score_resume_quality(text, extracted_data, target_skills, target_years, ats_analysis)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
