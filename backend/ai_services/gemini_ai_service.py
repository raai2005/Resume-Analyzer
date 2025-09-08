"""
Gemini AI integration for enhanced resume analysis
Provides intelligent analysis and formatting of extracted resume data
"""

import json
import os
import sys
import re
from typing import Dict, Any, Optional, List
import requests


class GeminiAnalyzer:
    """Integrates with Google Gemini AI for advanced resume analysis"""
    
    def __init__(self, api_key: Optional[str] = None, include_full_text: bool = False, max_text_chars: int = 2000):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        self.include_full_text = include_full_text
        self.max_text_chars = max_text_chars
        
    def analyze_resume(self, extracted_data: Dict[str, Any], original_text: str, job_title: str = None, job_description: str = None, company: str = None, required_skills: List[str] = None, preferred_skills: List[str] = None) -> Dict[str, Any]:
        """
        Analyze extracted resume data using Gemini AI
        
        Args:
            extracted_data: Structured data extracted from resume
            original_text: Original resume text
            job_title: Target job title (optional)
            job_description: Target job description (optional)
            company: Target company (optional)
            required_skills: List of required skills (optional)
            preferred_skills: List of preferred skills (optional)
            
        Returns:
            Enhanced analysis results with comprehensive skills gap analysis
        """
        # Perform skills gap analysis regardless of AI availability
        skills_analysis = self._analyze_skills_gap(extracted_data, job_title, job_description, required_skills, preferred_skills)
        
        if not self.api_key:
            return self._fallback_analysis(extracted_data, job_title, job_description, skills_analysis)
        
        # Prepare the analysis prompt with job context and skills gap
        prompt = self._create_analysis_prompt(extracted_data, original_text, job_title, job_description, skills_analysis)
        
        try:
            # Make API call to Gemini
            response = self._call_gemini_api(prompt)
            
            if response:
                # Parse and structure the response
                analysis = self._parse_gemini_response(response)
                # Inject skills gap analysis into AI response
                analysis["skills_gap_analysis"] = skills_analysis
                
                return {
                    "success": True,
                    "analysis": analysis,
                    "ai_powered": True,
                    "model_used": "gemini-pro",
                    "job_match_analysis": bool(job_title or job_description or required_skills or preferred_skills)
                }
            else:
                return self._fallback_analysis(extracted_data, job_title, job_description, skills_analysis)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._fallback_analysis(extracted_data, job_title, job_description, skills_analysis)
    
    def _create_analysis_prompt(self, extracted_data: Dict[str, Any], original_text: str, job_title: str = None, job_description: str = None, skills_analysis: Dict[str, Any] = None) -> str:
        """Create a comprehensive analysis prompt for Gemini with job-match context and skills gap analysis"""
        
        # Choose text inclusion strategy based on configuration
        if self.include_full_text:
            text_section = f"FULL RESUME TEXT:\n{original_text}"
        else:
            # Smart text truncation - prioritize important sections
            relevant_text = self._extract_relevant_text_sections(original_text, self.max_text_chars)
            text_section = f"RELEVANT RESUME TEXT SECTIONS:\n{relevant_text}"
        
        # Build job context section if provided
        job_context = self._build_job_context(job_title, job_description, extracted_data)
        
        # Build skills gap analysis section
        skills_gap_section = ""
        if skills_analysis:
            skills_gap_section = f"""
SKILLS GAP ANALYSIS:
Source: {skills_analysis['source']}
Overall Coverage: {skills_analysis['coverage_analysis']['overall_coverage_percent']}%
Gap Level: {skills_analysis['skills_gap_score']['level']} - {skills_analysis['skills_gap_score']['description']}

Target Skills Required: {', '.join(skills_analysis['target_skills']['required'])}
Target Skills Preferred: {', '.join(skills_analysis['target_skills']['preferred'])}

Skills Matched: {', '.join(skills_analysis['skills_breakdown']['matched_required'] + skills_analysis['skills_breakdown']['matched_preferred'])}
Missing Required: {', '.join(skills_analysis['skills_breakdown']['missing_required'])}
Missing Preferred: {', '.join(skills_analysis['skills_breakdown']['missing_preferred'])}
Bonus Skills: {', '.join(skills_analysis['skills_breakdown']['bonus_skills'])}

Priority Skills to Add: {', '.join(skills_analysis['priority_skills_to_add'])}
"""

        prompt = f"""
You are an expert resume analyst and career counselor. Analyze the following resume data and provide a comprehensive assessment with focus on skills gap analysis.

EXTRACTED RESUME DATA:
{json.dumps(extracted_data, indent=2)}

{text_section}

{job_context}

{skills_gap_section}

Please provide a detailed analysis in the following JSON format, incorporating the skills gap analysis above:

{{
  "job_match_analysis": {{
    "overall_job_fit": 0-100,
    "skills_match_percentage": 0-100,
    "experience_relevance": "highly_relevant|relevant|somewhat_relevant|not_relevant",
    "missing_required_skills": ["critical skills not found in resume"],
    "missing_preferred_skills": ["nice-to-have skills not found"],
    "competitive_advantages": ["unique strengths for this role"],
    "customization_recommendations": ["specific changes to improve job fit"],
    "interview_preparation": ["key areas to emphasize in interviews"],
    "salary_negotiation_points": ["strengths to leverage for compensation"],
    "skills_gap_summary": {{
      "coverage_score": {skills_analysis['coverage_analysis']['overall_coverage_percent'] if skills_analysis else 0},
      "gap_level": "{skills_analysis['skills_gap_score']['level'] if skills_analysis else 'unknown'}",
      "top_missing_skills": {skills_analysis['priority_skills_to_add'] if skills_analysis else []},
      "learning_recommendations": ["specific courses or certifications to pursue"]
    }}
  }}
}}

Focus on providing actionable, specific recommendations based on the skills gap analysis. Be honest about skill gaps while highlighting existing strengths and transferable skills.
"""
        return prompt
    
    def _analyze_skills_gap(self, extracted_data: Dict[str, Any], job_title: str = None, job_description: str = None, required_skills: List[str] = None, preferred_skills: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive skills gap analysis comparing extracted skills vs target skills
        
        Args:
            extracted_data: Resume data with extracted skills
            job_title: Target job title for role template fallback
            job_description: Job description to extract skills from
            required_skills: Explicitly provided required skills
            preferred_skills: Explicitly provided preferred skills
            
        Returns:
            Detailed skills gap analysis with coverage metrics
        """
        # Get extracted skills from resume
        resume_skills_data = extracted_data.get("skills", {})
        resume_skills_raw = []
        
        # Collect all skills from different categories
        for category in ["programming_languages", "web_technologies", "databases", "cloud_platforms", "tools_frameworks", "soft_skills"]:
            resume_skills_raw.extend(resume_skills_data.get(category, []))
        
        # Add matched skills if available
        resume_skills_raw.extend(resume_skills_data.get("matched_skills", []))
        
        # Normalize resume skills (remove duplicates, lowercase)
        resume_skills = set(skill.lower().strip() for skill in resume_skills_raw if skill)
        
        # Determine target skills
        target_skills = self._get_target_skills(job_title, job_description, required_skills, preferred_skills)
        
        # Perform gap analysis calculations
        target_required = set(skill.lower().strip() for skill in target_skills["required"])
        target_preferred = set(skill.lower().strip() for skill in target_skills["preferred"])
        all_target_skills = target_required | target_preferred
        
        # Calculate intersections and differences
        matched_required = resume_skills & target_required
        matched_preferred = resume_skills & target_preferred
        matched_all = resume_skills & all_target_skills
        
        missing_required = target_required - resume_skills
        missing_preferred = target_preferred - resume_skills
        missing_all = all_target_skills - resume_skills
        
        # Calculate coverage percentages
        required_coverage = (len(matched_required) / len(target_required) * 100) if target_required else 100
        preferred_coverage = (len(matched_preferred) / len(target_preferred) * 100) if target_preferred else 100
        overall_coverage = (len(matched_all) / len(all_target_skills) * 100) if all_target_skills else 0
        
        # Identify skill strengths (resume skills not in target but valuable)
        bonus_skills = resume_skills - all_target_skills
        valuable_bonus_skills = self._filter_valuable_skills(list(bonus_skills))
        
        # Generate recommendations
        recommendations = self._generate_skills_recommendations(
            list(missing_required), list(missing_preferred), list(valuable_bonus_skills), target_skills["source"]
        )
        
        return {
            "source": target_skills["source"],
            "target_skills": {
                "required": list(target_required),
                "preferred": list(target_preferred),
                "total_count": len(all_target_skills)
            },
            "resume_skills": {
                "all_skills": list(resume_skills),
                "total_count": len(resume_skills)
            },
            "coverage_analysis": {
                "required_coverage_percent": round(required_coverage, 1),
                "preferred_coverage_percent": round(preferred_coverage, 1),
                "overall_coverage_percent": round(overall_coverage, 1),
                "matched_required_count": len(matched_required),
                "matched_preferred_count": len(matched_preferred),
                "total_matched_count": len(matched_all)
            },
            "skills_breakdown": {
                "matched_required": list(matched_required),
                "matched_preferred": list(matched_preferred),
                "missing_required": list(missing_required),
                "missing_preferred": list(missing_preferred),
                "bonus_skills": valuable_bonus_skills
            },
            "recommendations": recommendations,
            "priority_skills_to_add": list(missing_required)[:5] + list(missing_preferred)[:3],
            "skills_gap_score": {
                "score": round(overall_coverage, 0),
                "level": self._get_gap_level(overall_coverage),
                "description": self._get_gap_description(overall_coverage)
            }
        }
    
    def _get_target_skills(self, job_title: str = None, job_description: str = None, required_skills: List[str] = None, preferred_skills: List[str] = None) -> Dict[str, Any]:
        """
        Get target skills from various sources with fallback to role templates
        
        Returns:
            Dictionary with required/preferred skills and source indication
        """
        # Priority 1: Explicitly provided skills
        if required_skills or preferred_skills:
            return {
                "required": required_skills or [],
                "preferred": preferred_skills or [],
                "source": "explicit_skills"
            }
        
        # Priority 2: Extract from job description
        if job_description:
            extracted = self._extract_target_skills_from_jd(job_description)
            return {
                "required": extracted["required"],
                "preferred": extracted["preferred"],
                "source": "job_description"
            }
        
        # Priority 3: Use role template based on job title
        if job_title:
            template = self._get_role_template(job_title)
            return {
                "required": template["required"],
                "preferred": template["preferred"],
                "source": f"role_template_{template['role_type']}"
            }
        
        # Fallback: Generic software engineer template
        default_template = self._get_role_template("Software Engineer")
        return {
            "required": default_template["required"],
            "preferred": default_template["preferred"],
            "source": "default_template"
        }
    
    def _get_role_template(self, job_title: str) -> Dict[str, Any]:
        """
        Get skills template for common roles
        
        Args:
            job_title: Job title to match against templates
            
        Returns:
            Skills template with required/preferred skills
        """
        job_title_lower = job_title.lower()
        
        # Backend Engineering roles
        if any(term in job_title_lower for term in ["backend", "server", "api", "microservices"]):
            return {
                "role_type": "backend_engineer",
                "required": ["Python", "JavaScript", "SQL", "REST API", "Git", "Testing"],
                "preferred": ["Node.js", "Express.js", "FastAPI", "PostgreSQL", "Redis", "Docker", "AWS", "Microservices"]
            }
        
        # Frontend Engineering roles  
        elif any(term in job_title_lower for term in ["frontend", "front-end", "ui", "react", "angular", "vue"]):
            return {
                "role_type": "frontend_engineer", 
                "required": ["JavaScript", "HTML", "CSS", "React", "Git", "Testing"],
                "preferred": ["TypeScript", "Vue.js", "Angular", "SASS", "Webpack", "Next.js", "Redux", "Figma"]
            }
        
        # Full Stack roles
        elif any(term in job_title_lower for term in ["fullstack", "full-stack", "full stack"]):
            return {
                "role_type": "fullstack_engineer",
                "required": ["JavaScript", "Python", "React", "SQL", "REST API", "Git"],
                "preferred": ["TypeScript", "Node.js", "PostgreSQL", "MongoDB", "Docker", "AWS", "CI/CD"]
            }
        
        # DevOps/Infrastructure roles
        elif any(term in job_title_lower for term in ["devops", "infrastructure", "platform", "sre", "cloud"]):
            return {
                "role_type": "devops_engineer",
                "required": ["Linux", "Docker", "Kubernetes", "AWS", "Git", "Shell"],
                "preferred": ["Terraform", "Ansible", "Jenkins", "Monitoring", "Python", "Helm", "CI/CD"]
            }
        
        # Data Engineering roles
        elif any(term in job_title_lower for term in ["data engineer", "data science", "machine learning", "ml", "ai"]):
            return {
                "role_type": "data_engineer",
                "required": ["Python", "SQL", "Pandas", "Git", "Statistics"],
                "preferred": ["Spark", "Airflow", "Kafka", "scikit-learn", "TensorFlow", "AWS", "Docker", "Jupyter"]
            }
        
        # Mobile Development roles
        elif any(term in job_title_lower for term in ["mobile", "ios", "android", "react native", "flutter"]):
            return {
                "role_type": "mobile_engineer",
                "required": ["Swift", "Kotlin", "React Native", "Git", "Testing"],
                "preferred": ["Flutter", "Dart", "Objective-C", "Java", "Firebase", "App Store", "CI/CD"]
            }
        
        # QA/Testing roles
        elif any(term in job_title_lower for term in ["qa", "test", "quality assurance"]):
            return {
                "role_type": "qa_engineer",
                "required": ["Testing", "Automation", "Selenium", "Git", "SQL"],
                "preferred": ["Cypress", "Jest", "Postman", "Jenkins", "Python", "JavaScript", "Performance Testing"]
            }
        
        # Product Manager roles
        elif any(term in job_title_lower for term in ["product manager", "pm", "product owner"]):
            return {
                "role_type": "product_manager",
                "required": ["Agile", "Scrum", "Product Management", "Analytics", "Communication"],
                "preferred": ["JIRA", "Figma", "SQL", "A/B Testing", "User Research", "Roadmapping", "Stakeholder Management"]
            }
        
        # Default: Software Engineer
        else:
            return {
                "role_type": "software_engineer",
                "required": ["Programming", "Git", "Testing", "Problem Solving", "Communication"],
                "preferred": ["JavaScript", "Python", "SQL", "Cloud Platforms", "Docker", "CI/CD", "Agile"]
            }
    
    def _filter_valuable_skills(self, skills: List[str]) -> List[str]:
        """Filter skills to include only valuable/recognized ones"""
        # Define valuable skills that might not be in job requirements but are good to have
        valuable_skills = {
            # Programming languages
            "python", "javascript", "typescript", "java", "go", "rust", "swift", "kotlin", "c++", "c#",
            # Frameworks & libraries  
            "react", "vue.js", "angular", "node.js", "express", "django", "flask", "spring", "laravel",
            # Databases
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite", "oracle",
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "github actions",
            # Tools & Technologies
            "git", "linux", "nginx", "apache", "webpack", "babel", "jest", "cypress", "postman",
            # Soft skills
            "leadership", "communication", "teamwork", "agile", "scrum", "project management"
        }
        
        return [skill for skill in skills if skill.lower() in valuable_skills]
    
    def _generate_skills_recommendations(self, missing_required: List[str], missing_preferred: List[str], bonus_skills: List[str], source: str) -> Dict[str, List[str]]:
        """Generate actionable skills recommendations"""
        recommendations = {
            "immediate_priority": [],
            "medium_priority": [], 
            "long_term": [],
            "leverage_existing": [],
            "source_note": []
        }
        
        # Immediate priority: Missing required skills
        if missing_required:
            recommendations["immediate_priority"] = [
                f"Add '{skill}' - critical for role requirements" for skill in missing_required[:3]
            ]
        
        # Medium priority: Missing preferred skills
        if missing_preferred:
            recommendations["medium_priority"] = [
                f"Consider learning '{skill}' - preferred by employers" for skill in missing_preferred[:3]
            ]
        
        # Long term: Advanced skills based on role
        recommendations["long_term"] = [
            "Consider cloud certifications (AWS, Azure, GCP)",
            "Learn modern testing frameworks and methodologies", 
            "Develop leadership and communication skills"
        ]
        
        # Leverage existing bonus skills
        if bonus_skills:
            recommendations["leverage_existing"] = [
                f"Highlight '{skill}' - valuable differentiator" for skill in bonus_skills[:3]
            ]
        
        # Source-specific notes
        if source == "job_description":
            recommendations["source_note"] = ["Skills extracted from specific job posting"]
        elif source.startswith("role_template"):
            role_type = source.split("_")[-1]
            recommendations["source_note"] = [f"Based on {role_type.replace('_', ' ').title()} role template"]
        elif source == "explicit_skills":
            recommendations["source_note"] = ["Based on explicitly provided skill requirements"]
        else:
            recommendations["source_note"] = ["Based on general software engineering expectations"]
        
        return recommendations
    
    def _get_gap_level(self, coverage_percent: float) -> str:
        """Get skill gap level description"""
        if coverage_percent >= 80:
            return "excellent"
        elif coverage_percent >= 60:
            return "good" 
        elif coverage_percent >= 40:
            return "moderate"
        elif coverage_percent >= 20:
            return "significant"
        else:
            return "substantial"
    
    def _get_gap_description(self, coverage_percent: float) -> str:
        """Get human-readable gap description"""
        if coverage_percent >= 80:
            return "Strong skill alignment - excellent match for target role"
        elif coverage_percent >= 60:
            return "Good skill foundation - some additional skills would strengthen profile"
        elif coverage_percent >= 40:
            return "Moderate skills match - several key areas need development"
        elif coverage_percent >= 20:
            return "Significant skills gap - substantial upskilling needed"
        else:
            return "Major skills gap - extensive learning required for target role"
        """Create a comprehensive analysis prompt for Gemini with job-match context"""
        
        # Choose text inclusion strategy based on configuration
        if self.include_full_text:
            text_section = f"FULL RESUME TEXT:\n{original_text}"
        else:
            # Smart text truncation - prioritize important sections
            relevant_text = self._extract_relevant_text_sections(original_text, self.max_text_chars)
            text_section = f"RELEVANT RESUME TEXT SECTIONS:\n{relevant_text}"
        
        # Build job context section if provided
        job_context = self._build_job_context(job_title, job_description, extracted_data)
        
        prompt = f"""
You are an expert resume analyst and career counselor. Analyze the following resume data and provide a comprehensive assessment.

EXTRACTED RESUME DATA:
{json.dumps(extracted_data, indent=2)}

{text_section}

{job_context}

Please provide a detailed analysis in the following JSON format:

{{
  "contact_analysis": {{
    "completeness_score": 0-100,
    "missing_elements": ["list of missing contact info"],
    "recommendations": ["specific suggestions for contact section"]
  }},
  "experience_analysis": {{
    "experience_quality": "excellent|good|average|poor",
    "strengths": ["list of experience strengths"],
    "weaknesses": ["list of areas for improvement"],
    "career_progression": "clear|unclear",
    "years_of_experience": {{
      "total": 0,
      "relevant": 0,
      "breakdown": {{"full_time": 0, "internship": 0}}
    }},
    "recommendations": ["specific suggestions for experience section"]
  }},
  "skills_analysis": {{
    "skill_relevance": "high|medium|low",
    "skill_depth": "deep|moderate|shallow",
    "trending_skills": ["list of modern/in-demand skills found"],
    "missing_critical_skills": ["important skills not mentioned"],
    "skill_categorization": {{
      "technical_skills": ["list"],
      "soft_skills": ["list"],
      "domain_specific": ["list"]
    }},
    "recommendations": ["specific suggestions for skills section"]
  }},
  "education_analysis": {{
    "education_relevance": "highly_relevant|relevant|somewhat_relevant|not_relevant",
    "academic_achievements": ["list of notable achievements"],
    "recommendations": ["suggestions for education section"]
  }},
  "projects_analysis": {{
    "project_quality": "excellent|good|average|poor",
    "technical_complexity": "high|medium|low",
    "business_impact": "clear|unclear|not_mentioned",
    "recommendations": ["suggestions for projects section"]
  }},
  "overall_assessment": {{
    "resume_score": 0-100,
    "ats_compatibility": "high|medium|low",
    "target_roles": ["list of suitable job roles"],
    "experience_level": "entry|junior|mid|senior|executive",
    "key_strengths": ["top 3-5 strengths"],
    "critical_improvements": ["top 3-5 areas needing improvement"],
    "estimated_salary_range": {{"min": 0, "max": 0, "currency": "USD"}},
    "market_competitiveness": "highly_competitive|competitive|average|below_average"
  }},
  "detailed_recommendations": {{
    "immediate_actions": ["urgent improvements needed"],
    "format_improvements": ["formatting and structure suggestions"],
    "content_improvements": ["content-related suggestions"],
    "keyword_optimization": ["keywords to add for ATS"],
    "industry_alignment": ["suggestions for specific industry targeting"]
  }},
    "role_fit_analysis": {{
    "best_matching_roles": [
      {{
        "role": "role name",
        "fit_score": 0-100,
        "missing_skills": ["list"],
        "preparation_needed": ["list of improvements"]
      }}
    ],
    "career_path_suggestions": ["potential career progression paths"]
  }},
  "job_match_analysis": {{
    "overall_job_fit": 0-100,
    "skills_match_percentage": 0-100,
    "experience_relevance": "highly_relevant|relevant|somewhat_relevant|not_relevant",
    "missing_required_skills": ["critical skills not found in resume"],
    "missing_preferred_skills": ["nice-to-have skills not found"],
    "competitive_advantages": ["unique strengths for this role"],
    "customization_recommendations": ["specific changes to improve job fit"],
    "interview_preparation": ["key areas to emphasize in interviews"],
    "salary_negotiation_points": ["strengths to leverage for compensation"]
  }}
}}Focus on providing actionable, specific recommendations. Be honest about weaknesses while highlighting strengths. Consider current market trends and hiring practices.
"""
        return prompt
    
    def _extract_relevant_text_sections(self, original_text: str, max_chars: int = 2000) -> str:
        """
        Intelligently extract the most relevant parts of the resume text
        instead of just taking the first 1000 characters
        """
        if len(original_text) <= max_chars:
            return original_text
        
        lines = original_text.split('\n')
        sections = {}
        current_section = "header"
        current_content = []
        
        # Section keywords to identify important parts
        section_keywords = {
            'experience': ['experience', 'work', 'employment', 'professional', 'career'],
            'education': ['education', 'academic', 'university', 'college', 'degree'],
            'skills': ['skills', 'technical', 'technologies', 'tools', 'programming'],
            'projects': ['projects', 'portfolio', 'work samples'],
            'summary': ['summary', 'objective', 'profile', 'about'],
            'certifications': ['certification', 'licenses', 'credentials']
        }
        
        # First, try to identify sections
        for line in lines:
            line_clean = line.strip().lower()
            
            # Check if this line is a section header
            section_found = None
            for section_name, keywords in section_keywords.items():
                if any(keyword in line_clean for keyword in keywords):
                    # Only consider it a section if it's short enough to be a header
                    if len(line.strip()) < 50:
                        section_found = section_name
                        break
            
            if section_found:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = section_found
                current_content = [line]
            else:
                current_content.append(line)
        
        # Save the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        # Prioritize sections by importance for analysis
        priority_order = ['header', 'summary', 'experience', 'skills', 'projects', 'education', 'certifications']
        
        # Build the relevant text, prioritizing important sections
        relevant_parts = []
        char_count = 0
        
        for section_name in priority_order:
            if section_name in sections:
                section_text = sections[section_name].strip()
                
                # For experience and projects, include more content
                if section_name in ['experience', 'projects']:
                    max_section_chars = max_chars // 3  # Allow up to 1/3 for experience
                elif section_name == 'header':
                    max_section_chars = 200  # Header info
                else:
                    max_section_chars = max_chars // 6  # Other sections get smaller portions
                
                if char_count + len(section_text) <= max_chars:
                    relevant_parts.append(f"=== {section_name.upper()} ===")
                    relevant_parts.append(section_text)
                    char_count += len(section_text) + 20  # +20 for section header
                else:
                    # Truncate this section to fit
                    remaining_chars = max_chars - char_count - 20
                    if remaining_chars > 100:  # Only add if we have meaningful space
                        relevant_parts.append(f"=== {section_name.upper()} ===")
                        relevant_parts.append(section_text[:remaining_chars] + "...")
                    break
        
        # If we couldn't parse sections well, fall back to smart truncation
        if char_count < max_chars // 2:
            # Take first part + last part to get both header and conclusion info
            first_part = original_text[:max_chars//2]
            last_part = original_text[-(max_chars//2):]
            return f"{first_part}\n\n... [middle content truncated] ...\n\n{last_part}"
        
        return '\n'.join(relevant_parts)
    
    def _build_job_context(self, job_title: str, job_description: str, extracted_data: Dict[str, Any]) -> str:
        """Build job context section for targeted analysis"""
        if not job_title and not job_description:
            return ""
        
        context_parts = ["TARGET JOB ANALYSIS:"]
        
        if job_title:
            context_parts.append(f"Job Title: {job_title}")
        
        if job_description:
            # Extract target skills from job description
            target_skills = self._extract_target_skills_from_jd(job_description)
            
            context_parts.append(f"Job Description: {job_description[:1000]}...")
            context_parts.append(f"Required Skills Extracted: {', '.join(target_skills['required'])}")
            context_parts.append(f"Preferred Skills Extracted: {', '.join(target_skills['preferred'])}")
            
            # Skills gap analysis
            resume_skills = set(extracted_data.get("skills", {}).get("matched_skills", []))
            required_skills = set(target_skills['required'])
            preferred_skills = set(target_skills['preferred'])
            
            missing_required = list(required_skills - resume_skills)
            missing_preferred = list(preferred_skills - resume_skills)
            matching_skills = list(resume_skills & (required_skills | preferred_skills))
            
            context_parts.append(f"Skills Match: {len(matching_skills)} skills match")
            context_parts.append(f"Missing Required Skills: {', '.join(missing_required[:10])}")  # Limit for prompt size
            context_parts.append(f"Missing Preferred Skills: {', '.join(missing_preferred[:10])}")
        
        context_parts.append("\nPLEASE FOCUS YOUR ANALYSIS ON:")
        context_parts.append("1. How well this resume matches the target job requirements")
        context_parts.append("2. Specific skills gaps and how to address them")
        context_parts.append("3. Resume customization recommendations for this specific role")
        context_parts.append("4. Competitive positioning for this job market")
        
        return '\n'.join(context_parts)
    
    def _extract_target_skills_from_jd(self, job_description: str) -> Dict[str, List[str]]:
        """Extract required and preferred skills from job description"""
        jd_lower = job_description.lower()
        
        # Load skills database
        skills_database = self._load_skills_database()
        
        # Create comprehensive skills list with synonyms
        all_skills = []
        skill_synonyms = self._get_skill_synonyms()
        
        for category, skills in skills_database.items():
            all_skills.extend(skills)
        
        # Add synonyms to search
        for skill in list(all_skills):
            if skill.lower() in skill_synonyms:
                all_skills.extend(skill_synonyms[skill.lower()])
        
        # Find skills in job description
        found_skills = []
        for skill in set(all_skills):  # Remove duplicates
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, jd_lower):
                found_skills.append(skill)
        
        # Categorize as required vs preferred based on context
        required_skills = []
        preferred_skills = []
        
        # Simple heuristic: look for context clues
        for skill in found_skills:
            skill_contexts = self._find_skill_contexts(skill, job_description)
            if any(req_word in skill_contexts.lower() for req_word in ['required', 'must', 'essential', 'mandatory']):
                required_skills.append(skill)
            elif any(pref_word in skill_contexts.lower() for pref_word in ['preferred', 'nice', 'plus', 'bonus', 'ideal']):
                preferred_skills.append(skill)
            else:
                # If no clear context, assume required for core skills, preferred for others
                if skill.lower() in ['python', 'javascript', 'java', 'react', 'node.js', 'sql', 'aws', 'docker']:
                    required_skills.append(skill)
                else:
                    preferred_skills.append(skill)
        
        return {
            'required': list(set(required_skills)),
            'preferred': list(set(preferred_skills))
        }
    
    def _get_skill_synonyms(self) -> Dict[str, List[str]]:
        """Get skill synonyms for better matching"""
        return {
            'javascript': ['js', 'ecmascript'],
            'typescript': ['ts'],
            'react': ['reactjs', 'react.js'],
            'vue.js': ['vue', 'vuejs'],
            'angular': ['angularjs'],
            'node.js': ['nodejs', 'node'],
            'express.js': ['express', 'expressjs'],
            'python': ['py'],
            'postgresql': ['postgres', 'psql'],
            'mysql': ['sql'],
            'mongodb': ['mongo'],
            'aws': ['amazon web services'],
            'gcp': ['google cloud platform', 'google cloud'],
            'azure': ['microsoft azure'],
            'docker': ['containerization'],
            'kubernetes': ['k8s'],
            'machine learning': ['ml', 'artificial intelligence', 'ai'],
            'artificial intelligence': ['ai', 'machine learning', 'ml'],
            'rest api': ['restful', 'rest', 'api'],
            'graphql': ['graph ql']
        }
    
    def _load_skills_database(self) -> Dict[str, List[str]]:
        """Load curated skills database - same as InformationExtractor"""
        return {
            "programming_languages": [
                "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Swift", "Kotlin",
                "PHP", "Ruby", "Scala", "R", "MATLAB", "C", "Objective-C", "Dart", "Perl", "Shell"
            ],
            "web_technologies": [
                "React", "Vue.js", "Angular", "Node.js", "Express.js", "Django", "Flask", "FastAPI",
                "Spring Boot", "ASP.NET", "Ruby on Rails", "Laravel", "Next.js", "Nuxt.js", "Svelte",
                "HTML", "CSS", "SASS", "SCSS", "Bootstrap", "Tailwind CSS", "jQuery", "Webpack", "Vite"
            ],
            "databases": [
                "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "SQLite", "Oracle",
                "SQL Server", "Cassandra", "DynamoDB", "Firebase", "Supabase", "Neo4j", "MariaDB"
            ],
            "cloud_platforms": [
                "AWS", "Azure", "Google Cloud", "GCP", "Heroku", "Vercel", "Netlify", "DigitalOcean",
                "Linode", "Cloudflare", "Firebase", "Supabase"
            ],
            "tools_frameworks": [
                "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab", "Terraform", "Ansible",
                "Nginx", "Apache", "Linux", "Ubuntu", "CentOS", "Bash", "PowerShell", "Vim", "VS Code",
                "IntelliJ", "Eclipse", "Postman", "Swagger", "Figma", "Adobe Creative Suite"
            ],
            "soft_skills": [
                "Leadership", "Communication", "Teamwork", "Problem Solving", "Critical Thinking",
                "Project Management", "Agile", "Scrum", "Time Management", "Adaptability"
            ]
        }
    
    def _find_skill_contexts(self, skill: str, text: str, context_window: int = 50) -> str:
        """Find context around a skill mention in text"""
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Find all occurrences
        contexts = []
        start = 0
        while True:
            pos = text_lower.find(skill_lower, start)
            if pos == -1:
                break
            
            # Extract context around the skill
            context_start = max(0, pos - context_window)
            context_end = min(len(text), pos + len(skill) + context_window)
            context = text[context_start:context_end]
            contexts.append(context)
            
            start = pos + 1
        
        return ' '.join(contexts)
    
    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Make API call to Gemini"""
        if not self.api_key:
            return None
        
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 4096,
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"Gemini API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
        
        return None
    
    def _parse_gemini_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate Gemini's JSON response"""
        try:
            # Extract JSON from the response (in case there's extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # If no JSON found, create structured response from text
                return self._create_structured_response_from_text(response)
                
        except json.JSONDecodeError:
            # Fallback: create basic structure from text response
            return self._create_structured_response_from_text(response)
    
    def _create_structured_response_from_text(self, text: str) -> Dict[str, Any]:
        """Create structured response when JSON parsing fails"""
        return {
            "contact_analysis": {
                "completeness_score": 75,
                "missing_elements": [],
                "recommendations": ["Improve contact section based on AI analysis"]
            },
            "experience_analysis": {
                "experience_quality": "good",
                "strengths": ["Relevant experience"],
                "weaknesses": ["Need more details"],
                "recommendations": ["Add more quantifiable achievements"]
            },
            "overall_assessment": {
                "resume_score": 75,
                "ats_compatibility": "medium",
                "target_roles": ["Software Engineer"],
                "key_strengths": ["Technical skills"],
                "critical_improvements": ["Add metrics and achievements"]
            },
            "raw_ai_response": text
        }
    
    def _fallback_analysis(self, extracted_data: Dict[str, Any], job_title: str = None, job_description: str = None, skills_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Provide fallback analysis when AI is not available, including comprehensive skills gap analysis"""
        contact_info = extracted_data.get("contact_info", {})
        experience = extracted_data.get("experience", {})
        skills = extracted_data.get("skills", {})
        education = extracted_data.get("education", {})
        
        # Calculate basic scores
        contact_score = len([v for v in contact_info.values() if v and v != "None"]) * 20
        skills_score = min(skills.get("total_skills_found", 0) * 5, 100)
        experience_years = experience.get("total_years", 0)
        experience_score = min(experience_years * 20, 100)
        
        overall_score = (contact_score + skills_score + experience_score) / 3
        
        # Job match analysis if job context provided
        job_match_analysis = {}
        if job_title or job_description:
            job_match_analysis = self._calculate_job_fit_fallback(extracted_data, job_title, job_description)
        
        analysis = {
            "contact_analysis": {
                "completeness_score": contact_score,
                "missing_elements": self._get_missing_contact_elements(contact_info),
                "recommendations": ["Add missing contact information for better reachability"]
            },
            "experience_analysis": {
                "experience_quality": "good" if experience_years > 2 else "average",
                "strengths": ["Relevant experience found"],
                "weaknesses": ["Consider adding more quantifiable achievements"],
                "years_of_experience": {
                    "total": experience_years,
                    "relevant": experience_years
                },
                "recommendations": ["Add specific metrics and achievements to experience entries"]
            },
            "skills_analysis": {
                "skill_relevance": "high" if skills.get("total_skills_found", 0) > 10 else "medium",
                "trending_skills": skills.get("programming_languages", [])[:3],
                "missing_critical_skills": ["Consider adding cloud platforms", "Add modern frameworks"],
                "recommendations": ["Include more trending technologies and tools"]
            },
            "overall_assessment": {
                "resume_score": int(overall_score),
                "ats_compatibility": "medium",
                "target_roles": [extracted_data.get("role_inference", {}).get("primary_role", "Software Engineer")],
                "experience_level": experience.get("career_level", "entry"),
                "key_strengths": ["Technical skills", "Relevant experience"],
                "critical_improvements": ["Add quantifiable achievements", "Improve formatting", "Add keywords"]
            },
            "detailed_recommendations": {
                "immediate_actions": ["Add contact information", "Include metrics in experience"],
                "format_improvements": ["Use consistent formatting", "Add bullet points"],
                "content_improvements": ["Add project outcomes", "Include soft skills"],
                "keyword_optimization": ["Add industry-specific keywords", "Include technical terms"]
            }
        }
        
        # Add skills gap analysis if available
        if skills_analysis:
            analysis["skills_gap_analysis"] = skills_analysis
            
            # Enhance skills analysis with gap insights
            analysis["skills_analysis"]["skills_gap_insights"] = {
                "coverage_assessment": f"Based on {skills_analysis['coverage_analysis']['overall_coverage_percent']}% skills coverage",
                "priority_additions": skills_analysis['priority_skills_to_add'][:3],
                "learning_path": [rec for rec in skills_analysis['recommendations']['immediate_priority'][:3]]
            }
        
        # Add job match analysis if available  
        if job_match_analysis:
            analysis["job_match_analysis"] = job_match_analysis
        
        return {
            "success": True,
            "analysis": analysis,
            "ai_powered": False,
            "model_used": "rule_based_fallback",
            "job_match_analysis": bool(job_title or job_description),
            "skills_gap_included": bool(skills_analysis)
        }
    
    def _get_missing_contact_elements(self, contact_info: Dict) -> List[str]:
        """Identify missing contact elements"""
        missing = []
        required_fields = ["name", "email", "phone", "linkedin"]
        
        for field in required_fields:
            if not contact_info.get(field):
                missing.append(field)
        
        return missing
    
    def _calculate_job_fit_fallback(self, user_skills: List[str], required_skills: List[str], preferred_skills: List[str]) -> Dict[str, Any]:
        """Calculate job fit using rule-based analysis when AI is not available"""
        if not required_skills and not preferred_skills:
            return {
                "overall_job_fit": 50,
                "skills_match_percentage": 0,
                "experience_relevance": "unknown",
                "missing_required_skills": [],
                "missing_preferred_skills": [],
                "competitive_advantages": ["Experience in relevant field"],
                "customization_recommendations": ["Consider adding more specific skills"],
                "interview_preparation": ["Research company and role requirements"],
                "salary_negotiation_points": ["Highlight unique technical skills"]
            }
        
        # Calculate skills match
        resume_skills = set(skill.lower().strip() for skill in user_skills)
        required_skills_set = set(skill.lower().strip() for skill in required_skills)
        preferred_skills_set = set(skill.lower().strip() for skill in preferred_skills)
        all_target_skills = required_skills_set | preferred_skills_set
        
        if all_target_skills:
            matching_skills = resume_skills & all_target_skills
            skills_match_percentage = int((len(matching_skills) / len(all_target_skills)) * 100)
        else:
            skills_match_percentage = 0
        
        # Calculate overall job fit (simplified)
        skills_score = min(skills_match_percentage * 0.6, 60)  # Skills weighted at 60%
        base_score = 30  # Base score for having relevant experience
        overall_fit = int(skills_score + base_score)
        
        # Determine experience relevance
        if skills_match_percentage > 70:
            experience_relevance = "highly_relevant"
        elif skills_match_percentage > 40:
            experience_relevance = "relevant"
        elif skills_match_percentage > 20:
            experience_relevance = "somewhat_relevant"
        else:
            experience_relevance = "not_relevant"
        
        # Missing skills
        missing_required = [skill for skill in required_skills if skill.lower() not in resume_skills]
        missing_preferred = [skill for skill in preferred_skills if skill.lower() not in resume_skills]
        
        # Competitive advantages based on skills match
        advantages = []
        if skills_match_percentage > 80:
            advantages.append("Exceptional skill alignment with job requirements")
        elif skills_match_percentage > 60:
            advantages.append("Strong technical skill match")
        elif skills_match_percentage > 40:
            advantages.append("Good foundation of relevant skills")
        else:
            advantages.append("Transferable skills applicable to the role")
        
        # Add specific skill advantages
        matched_skills_list = list(resume_skills & all_target_skills)
        if matched_skills_list:
            top_matches = matched_skills_list[:3]  # Top 3 matched skills
            advantages.append(f"Experience with key technologies: {', '.join(top_matches)}")
        
        # Customization recommendations
        customizations = []
        if missing_required:
            customizations.append(f"Highlight any experience with: {', '.join(missing_required[:3])}")
        if missing_preferred:
            customizations.append(f"Consider adding experience with preferred skills: {', '.join(missing_preferred[:2])}")
        if skills_match_percentage < 50:
            customizations.append("Emphasize transferable skills and related experience")
        customizations.append("Use specific keywords from job description throughout resume")
        
        return {
            "overall_job_fit": overall_fit,
            "skills_match_percentage": skills_match_percentage,
            "experience_relevance": experience_relevance,
            "missing_required_skills": missing_required[:10],  # Limit for readability
            "missing_preferred_skills": missing_preferred[:10],
            "competitive_advantages": advantages,
            "customization_recommendations": customizations,
            "interview_preparation": [
                "Prepare examples demonstrating matching skills",
                "Research company culture and values",
                "Practice explaining career progression"
            ],
            "salary_negotiation_points": [
                "Highlight unique technical expertise",
                "Emphasize problem-solving achievements",
                "Reference market rates for similar roles"
            ]
        }
    
    def format_analysis_for_display(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis result for frontend display"""
        if not analysis_result.get("success"):
            return analysis_result
        
        analysis = analysis_result.get("analysis", {})
        
        formatted = {
            "success": True,
            "formatted_analysis": {
                "summary": {
                    "overall_score": analysis.get("overall_assessment", {}).get("resume_score", 0),
                    "ats_compatibility": analysis.get("overall_assessment", {}).get("ats_compatibility", "unknown"),
                    "experience_level": analysis.get("overall_assessment", {}).get("experience_level", "unknown"),
                    "target_roles": analysis.get("overall_assessment", {}).get("target_roles", [])
                },
                "strengths": analysis.get("overall_assessment", {}).get("key_strengths", []),
                "improvements": analysis.get("overall_assessment", {}).get("critical_improvements", []),
                "recommendations": analysis.get("detailed_recommendations", {}),
                "contact_completeness": analysis.get("contact_analysis", {}).get("completeness_score", 0),
                "experience_quality": analysis.get("experience_analysis", {}).get("experience_quality", "unknown"),
                "skills_relevance": analysis.get("skills_analysis", {}).get("skill_relevance", "unknown")
            },
            "ai_powered": analysis_result.get("ai_powered", False),
            "model_used": analysis_result.get("model_used", "unknown"),
            "has_job_context": analysis_result.get("job_match_analysis", False)
        }
        
        # Add skills gap analysis if available
        if "skills_gap_analysis" in analysis:
            skills_gap = analysis["skills_gap_analysis"]
            formatted["formatted_analysis"]["skills_gap"] = {
                "overall_coverage": skills_gap.get("coverage_analysis", {}).get("overall_coverage_percent", 0),
                "gap_level": skills_gap.get("skills_gap_score", {}).get("level", "unknown"),
                "gap_description": skills_gap.get("skills_gap_score", {}).get("description", ""),
                "target_source": skills_gap.get("source", "unknown"),
                "matched_skills": skills_gap.get("skills_breakdown", {}).get("matched_required", []) + 
                                skills_gap.get("skills_breakdown", {}).get("matched_preferred", []),
                "missing_required": skills_gap.get("skills_breakdown", {}).get("missing_required", []),
                "missing_preferred": skills_gap.get("skills_breakdown", {}).get("missing_preferred", []),
                "bonus_skills": skills_gap.get("skills_breakdown", {}).get("bonus_skills", []),
                "priority_skills_to_add": skills_gap.get("priority_skills_to_add", []),
                "recommendations": skills_gap.get("recommendations", {}),
                "coverage_breakdown": {
                    "required_coverage": skills_gap.get("coverage_analysis", {}).get("required_coverage_percent", 0),
                    "preferred_coverage": skills_gap.get("coverage_analysis", {}).get("preferred_coverage_percent", 0),
                    "total_target_skills": skills_gap.get("target_skills", {}).get("total_count", 0),
                    "total_resume_skills": skills_gap.get("resume_skills", {}).get("total_count", 0)
                }
            }
        
        # Add job match analysis if available
        if "job_match_analysis" in analysis:
            job_match = analysis["job_match_analysis"]
            formatted["formatted_analysis"]["job_match"] = {
                "overall_fit": job_match.get("overall_job_fit", 0),
                "skills_match": job_match.get("skills_match_percentage", 0),
                "experience_relevance": job_match.get("experience_relevance", "unknown"),
                "missing_required_skills": job_match.get("missing_required_skills", []),
                "missing_preferred_skills": job_match.get("missing_preferred_skills", []),
                "competitive_advantages": job_match.get("competitive_advantages", []),
                "customization_tips": job_match.get("customization_recommendations", []),
                "interview_prep": job_match.get("interview_preparation", []),
                "salary_points": job_match.get("salary_negotiation_points", [])
            }
        
        return formatted


def main():
    """Main function for command line usage"""
    if len(sys.argv) != 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: python gemini_analyzer.py '<extracted_data_json>' '<original_text>'"
        }))
        sys.exit(1)
    
    try:
        extracted_data = json.loads(sys.argv[1])
        original_text = sys.argv[2]
        
        analyzer = GeminiAnalyzer()
        result = analyzer.analyze_resume(extracted_data, original_text)
        formatted_result = analyzer.format_analysis_for_display(result)
        
        print(json.dumps(formatted_result, indent=2, ensure_ascii=False))
        
    except json.JSONDecodeError:
        print(json.dumps({
            "success": False,
            "error": "Invalid JSON in extracted_data parameter"
        }))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }))


if __name__ == "__main__":
    main()
