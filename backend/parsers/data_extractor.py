"""
Information extraction module for resume parsing
Extracts structured data like contact info, experience, education, skills, projects, certifications
"""

import re
import json
import sys
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime


class InformationExtractor:
    """Extracts structured information from resume text"""
    
    def __init__(self):
        # Initialize skill dictionaries and patterns
        self.skills_database = self._load_skills_database()
        self.regex_patterns = self._initialize_regex_patterns()
        self.certification_providers = self._load_certification_providers()
        self.degree_patterns = self._load_degree_patterns()
        
    def extract_all_information(self, text: str, normalized_text: str = None) -> Dict[str, Any]:
        """
        Extract all structured information from resume text
        
        Args:
            text: Original resume text
            normalized_text: Cleaned/normalized text (optional)
            
        Returns:
            Dictionary containing all extracted information
        """
        # Use normalized text if available, otherwise use original
        working_text = normalized_text if normalized_text else text
        
        result = {
            "success": True,
            "contact_info": self.extract_contact_info(working_text),
            "experience": self.extract_experience(working_text),
            "education": self.extract_education(working_text),
            "skills": self.extract_skills(working_text),
            "projects": self.extract_projects(working_text),
            "certifications": self.extract_certifications(working_text),
            "role_inference": self.infer_role(working_text),
            "summary_stats": {},
            "extraction_metadata": {
                "text_length": len(working_text),
                "extraction_timestamp": datetime.now().isoformat(),
                "patterns_used": list(self.regex_patterns.keys())
            }
        }
        
        # Generate summary statistics
        result["summary_stats"] = self._generate_summary_stats(result)
        
        return result
    
    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information including name, email, phone, links"""
        contact_info = {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "portfolio": None,
            "address": None,
            "confidence_scores": {}
        }
        
        lines = text.split('\n')
        
        # Extract name (usually first meaningful line)
        contact_info["name"] = self._extract_name(lines)
        
        # Extract email
        email_match = re.search(self.regex_patterns["email"], text, re.IGNORECASE)
        if email_match:
            contact_info["email"] = email_match.group().strip()
            contact_info["confidence_scores"]["email"] = 0.95
        
        # Extract phone
        phone_match = re.search(self.regex_patterns["phone"], text)
        if phone_match:
            contact_info["phone"] = phone_match.group().strip()
            contact_info["confidence_scores"]["phone"] = 0.90
        
        # Extract LinkedIn
        linkedin_match = re.search(self.regex_patterns["linkedin"], text, re.IGNORECASE)
        if linkedin_match:
            contact_info["linkedin"] = linkedin_match.group().strip()
            contact_info["confidence_scores"]["linkedin"] = 0.95
        
        # Extract GitHub
        github_match = re.search(self.regex_patterns["github"], text, re.IGNORECASE)
        if github_match:
            contact_info["github"] = github_match.group().strip()
            contact_info["confidence_scores"]["github"] = 0.95
        
        # Extract portfolio/personal website
        portfolio_match = re.search(self.regex_patterns["website"], text, re.IGNORECASE)
        if portfolio_match:
            url = portfolio_match.group().strip()
            # Filter out common social media sites to focus on portfolios
            if not any(domain in url.lower() for domain in ['linkedin', 'github', 'facebook', 'twitter', 'instagram']):
                contact_info["portfolio"] = url
                contact_info["confidence_scores"]["portfolio"] = 0.80
        
        return contact_info
    
    def _extract_name(self, lines: List[str]) -> Optional[str]:
        """Extract name from the first few lines of resume"""
        for line in lines[:5]:  # Check first 5 lines
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 3:
                continue
                
            # Skip lines that look like section headers
            if line_clean.upper() in ['RESUME', 'CV', 'CURRICULUM VITAE', 'CONTACT', 'CONTACT INFORMATION']:
                continue
                
            # Skip lines with email/phone patterns
            if re.search(r'@|[\d\-\(\)\+\s]{8,}', line_clean):
                continue
                
            # Check if line looks like a name (2-4 words, proper case, no special chars)
            words = line_clean.split()
            if 2 <= len(words) <= 4:
                # Check if all words start with capital letter and contain mostly letters
                if all(word[0].isupper() and word.replace('-', '').replace("'", "").isalpha() for word in words):
                    return line_clean
        
        return None
    
    def extract_experience(self, text: str) -> Dict[str, Any]:
        """Extract work experience including jobs and internships"""
        experience_data = {
            "total_years": 0,
            "positions": [],
            "companies": [],
            "internships": [],
            "full_time_jobs": [],
            "current_position": None,
            "career_level": "entry"
        }
        
        # Find experience section
        exp_section = self._find_section(text, ["experience", "work experience", "professional experience", "employment"])
        if not exp_section:
            return experience_data
        
        # Extract date ranges and positions
        positions = self._extract_positions(exp_section)
        
        for position in positions:
            # Classify as internship or full-time
            if self._is_internship(position["title"], position["description"]):
                experience_data["internships"].append(position)
            else:
                experience_data["full_time_jobs"].append(position)
            
            experience_data["positions"].append(position)
            if position["company"] not in experience_data["companies"]:
                experience_data["companies"].append(position["company"])
        
        # Calculate total years of experience
        experience_data["total_years"] = self._calculate_total_experience(positions)
        
        # Determine career level
        experience_data["career_level"] = self._determine_career_level(experience_data["total_years"], positions)
        
        # Identify current position
        current_pos = self._find_current_position(positions)
        if current_pos:
            experience_data["current_position"] = current_pos
        
        return experience_data
    
    def extract_education(self, text: str) -> Dict[str, Any]:
        """Extract education information"""
        education_data = {
            "degrees": [],
            "institutions": [],
            "graduation_years": [],
            "highest_degree": None,
            "education_level": "unknown"
        }
        
        # Find education section
        edu_section = self._find_section(text, ["education", "academic", "qualification"])
        if not edu_section:
            return education_data
        
        # Extract degrees
        degrees = self._extract_degrees(edu_section)
        education_data["degrees"] = degrees
        
        # Extract institutions
        institutions = self._extract_institutions(edu_section)
        education_data["institutions"] = institutions
        
        # Extract graduation years
        years = self._extract_graduation_years(edu_section)
        education_data["graduation_years"] = years
        
        # Determine highest degree
        if degrees:
            education_data["highest_degree"] = self._determine_highest_degree(degrees)
            education_data["education_level"] = self._determine_education_level(education_data["highest_degree"])
        
        return education_data
    
    def extract_skills(self, text: str) -> Dict[str, Any]:
        """Extract skills and technologies using curated dictionary"""
        skills_data = {
            "programming_languages": [],
            "web_technologies": [],
            "databases": [],
            "cloud_platforms": [],
            "tools_frameworks": [],
            "soft_skills": [],
            "matched_skills": [],
            "missing_important_skills": [],
            "skill_categories": {},
            "total_skills_found": 0
        }
        
        text_lower = text.lower()
        
        # Search for skills in each category
        for category, skills_list in self.skills_database.items():
            found_skills = []
            for skill in skills_list:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
                    skills_data["matched_skills"].append(skill)
            
            skills_data[category] = found_skills
            skills_data["skill_categories"][category] = len(found_skills)
        
        skills_data["total_skills_found"] = len(skills_data["matched_skills"])
        
        # Add all_skills as an alias for matched_skills for compatibility
        skills_data["all_skills"] = skills_data["matched_skills"].copy()
        
        # Identify missing important skills (high-demand skills not found)
        important_skills = self._get_important_skills()
        for skill in important_skills:
            if skill not in skills_data["matched_skills"]:
                skills_data["missing_important_skills"].append(skill)
        
        return skills_data
    
    def extract_projects(self, text: str) -> Dict[str, Any]:
        """Extract project information"""
        projects_data = {
            "projects": [],
            "total_projects": 0,
            "technologies_used": [],
            "project_types": []
        }
        
        # Find projects section
        projects_section = self._find_section(text, ["project", "portfolio", "work"])
        if not projects_section:
            return projects_data
        
        # Extract individual projects
        projects = self._extract_individual_projects(projects_section)
        projects_data["projects"] = projects
        projects_data["total_projects"] = len(projects)
        
        # Extract technologies mentioned in projects
        all_tech = []
        for project in projects:
            tech = self._extract_technologies_from_text(project.get("description", ""))
            all_tech.extend(tech)
            project["technologies"] = tech
        
        projects_data["technologies_used"] = list(set(all_tech))
        
        return projects_data
    
    def extract_certifications(self, text: str) -> Dict[str, Any]:
        """Extract certifications and courses"""
        cert_data = {
            "certifications": [],
            "total_certifications": 0,
            "providers": [],
            "certification_years": []
        }
        
        # Find certifications section
        cert_section = self._find_section(text, ["certification", "certificate", "course", "training"])
        if not cert_section:
            return cert_data
        
        # Extract individual certifications
        certifications = self._extract_individual_certifications(cert_section)
        cert_data["certifications"] = certifications
        cert_data["total_certifications"] = len(certifications)
        
        # Extract providers and years
        for cert in certifications:
            if cert.get("provider") and cert["provider"] not in cert_data["providers"]:
                cert_data["providers"].append(cert["provider"])
            if cert.get("year") and cert["year"] not in cert_data["certification_years"]:
                cert_data["certification_years"].append(cert["year"])
        
        return cert_data
    
    def infer_role(self, text: str) -> Dict[str, Any]:
        """Infer likely job role based on keywords and experience"""
        role_data = {
            "primary_role": "unknown",
            "confidence": 0.0,
            "role_scores": {},
            "supporting_keywords": []
        }
        
        text_lower = text.lower()
        
        # Role keyword mapping
        role_keywords = {
            "backend_engineer": ["backend", "api", "database", "server", "microservices", "rest", "graphql", "node.js", "django", "flask", "spring"],
            "frontend_engineer": ["frontend", "react", "vue", "angular", "javascript", "typescript", "css", "html", "ui", "ux"],
            "fullstack_engineer": ["fullstack", "full-stack", "mern", "mean", "django", "rails", "end-to-end"],
            "mobile_developer": ["android", "ios", "flutter", "react native", "swift", "kotlin", "mobile"],
            "data_scientist": ["data science", "machine learning", "deep learning", "python", "r", "pandas", "numpy", "tensorflow", "pytorch"],
            "ai_ml_engineer": ["artificial intelligence", "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "keras"],
            "devops_engineer": ["devops", "kubernetes", "docker", "aws", "azure", "gcp", "jenkins", "ci/cd", "terraform"],
            "qa_engineer": ["testing", "automation", "selenium", "cypress", "qa", "quality assurance", "test"],
            "product_manager": ["product management", "roadmap", "stakeholder", "agile", "scrum", "product owner"],
            "data_engineer": ["data engineering", "etl", "spark", "hadoop", "kafka", "data pipeline", "big data"]
        }
        
        # Calculate scores for each role
        for role, keywords in role_keywords.items():
            score = 0
            found_keywords = []
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
                    found_keywords.append(keyword)
            
            # Normalize score
            normalized_score = score / len(keywords)
            role_data["role_scores"][role] = normalized_score
            
            if normalized_score > role_data["confidence"]:
                role_data["confidence"] = normalized_score
                role_data["primary_role"] = role.replace("_", " ").title()
                role_data["supporting_keywords"] = found_keywords
        
        return role_data
    
    def _load_skills_database(self) -> Dict[str, List[str]]:
        """Load curated skills database"""
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
    
    def _initialize_regex_patterns(self) -> Dict[str, str]:
        """Initialize regex patterns for information extraction"""
        return {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'(\+?\d[\d\-\s\(\)]{7,15})',
            "linkedin": r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+/?',
            "github": r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+/?',
            "website": r'(?:https?://)?(?:www\.)?[\w\-]+\.[\w\-]+(?:/[\w\-/]*)?',
            "date_range": r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\b|Present|Current',
            "year": r'\b20\d{2}\b',
            "company_pattern": r'(?:at|@)\s+([A-Z][A-Za-z\s&,.-]+?)(?:\s|$|,|\.|;)',
            "degree_pattern": r'\b(?:B\.?Tech|B\.?E\.?|B\.?Sc|M\.?Tech|M\.?E\.?|M\.?Sc|MBA|MCA|Ph\.?D|Bachelor|Master|Doctor)\b'
        }
    
    def _load_certification_providers(self) -> List[str]:
        """Load known certification providers"""
        return [
            "AWS", "Microsoft", "Google", "Oracle", "Cisco", "IBM", "Salesforce", "Adobe",
            "Coursera", "Udemy", "edX", "Pluralsight", "LinkedIn Learning", "Udacity",
            "CompTIA", "PMI", "Scrum.org", "SAFe", "CISSP", "CISA", "PMP"
        ]
    
    def _load_degree_patterns(self) -> Dict[str, int]:
        """Load degree patterns with hierarchy levels"""
        return {
            "Ph.D": 4, "PhD": 4, "Doctor": 4,
            "M.Tech": 3, "MTech": 3, "M.E.": 3, "ME": 3, "M.Sc": 3, "MSc": 3, "MBA": 3, "MCA": 3, "Master": 3,
            "B.Tech": 2, "BTech": 2, "B.E.": 2, "BE": 2, "B.Sc": 2, "BSc": 2, "Bachelor": 2,
            "Diploma": 1, "Certificate": 1
        }
    
    def _find_section(self, text: str, section_keywords: List[str]) -> Optional[str]:
        """Find a specific section in the text"""
        lines = text.split('\n')
        section_start = None
        
        for i, line in enumerate(lines):
            line_clean = line.strip().lower()
            if any(keyword in line_clean for keyword in section_keywords):
                section_start = i
                break
        
        if section_start is None:
            return None
        
        # Find section end (next major section or end of document)
        section_end = len(lines)
        for i in range(section_start + 1, len(lines)):
            line = lines[i].strip()
            if self._looks_like_section_header(line):
                section_end = i
                break
        
        return '\n'.join(lines[section_start:section_end])
    
    def _looks_like_section_header(self, line: str) -> bool:
        """Check if a line looks like a section header"""
        if not line or len(line) < 3:
            return False
        
        common_sections = ['experience', 'education', 'skills', 'projects', 'certifications', 'contact']
        line_lower = line.lower()
        
        return (line.isupper() or 
                any(section in line_lower for section in common_sections) or
                line.endswith(':'))
    
    def _extract_positions(self, text: str) -> List[Dict[str, Any]]:
        """Extract job positions from experience text"""
        positions = []
        # This is a simplified implementation - would need more sophisticated parsing
        # For now, return empty list as placeholder
        return positions
    
    def _is_internship(self, title: str, description: str) -> bool:
        """Check if a position is an internship"""
        internship_keywords = ['intern', 'internship', 'trainee', 'summer', 'co-op']
        text = (title + ' ' + description).lower()
        return any(keyword in text for keyword in internship_keywords)
    
    def _calculate_total_experience(self, positions: List[Dict]) -> float:
        """Calculate total years of experience"""
        # Placeholder implementation
        return 0.0
    
    def _determine_career_level(self, years: float, positions: List[Dict]) -> str:
        """Determine career level based on experience"""
        if years < 1:
            return "entry"
        elif years < 3:
            return "junior"
        elif years < 7:
            return "mid"
        else:
            return "senior"
    
    def _find_current_position(self, positions: List[Dict]) -> Optional[Dict]:
        """Find current position from list of positions"""
        # Placeholder implementation
        return None
    
    def _extract_degrees(self, text: str) -> List[str]:
        """Extract degree information"""
        degrees = []
        for degree, level in self.degree_patterns.items():
            if degree.lower() in text.lower():
                degrees.append(degree)
        return degrees
    
    def _extract_institutions(self, text: str) -> List[str]:
        """Extract institution names"""
        # Placeholder implementation
        return []
    
    def _extract_graduation_years(self, text: str) -> List[int]:
        """Extract graduation years"""
        years = []
        year_matches = re.findall(self.regex_patterns["year"], text)
        for year_str in year_matches:
            years.append(int(year_str))
        return years
    
    def _determine_highest_degree(self, degrees: List[str]) -> str:
        """Determine highest degree from list"""
        if not degrees:
            return None
        
        highest_level = 0
        highest_degree = degrees[0]
        
        for degree in degrees:
            level = self.degree_patterns.get(degree, 0)
            if level > highest_level:
                highest_level = level
                highest_degree = degree
        
        return highest_degree
    
    def _determine_education_level(self, highest_degree: str) -> str:
        """Determine education level"""
        if not highest_degree:
            return "unknown"
        
        level = self.degree_patterns.get(highest_degree, 0)
        if level >= 4:
            return "doctorate"
        elif level >= 3:
            return "masters"
        elif level >= 2:
            return "bachelors"
        else:
            return "diploma"
    
    def _get_important_skills(self) -> List[str]:
        """Get list of important/high-demand skills"""
        return [
            "Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes",
            "Git", "SQL", "MongoDB", "Machine Learning", "Data Science"
        ]
    
    def _extract_individual_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract individual projects"""
        # Placeholder implementation
        return []
    
    def _extract_technologies_from_text(self, text: str) -> List[str]:
        """Extract technologies mentioned in text"""
        technologies = []
        text_lower = text.lower()
        
        # Check against all skills in database
        for category, skills in self.skills_database.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    technologies.append(skill)
        
        return technologies
    
    def _extract_individual_certifications(self, text: str) -> List[Dict[str, Any]]:
        """Extract individual certifications"""
        # Placeholder implementation
        return []
    
    def _generate_summary_stats(self, extracted_data: Dict) -> Dict[str, Any]:
        """Generate summary statistics from extracted data"""
        return {
            "total_experience_years": extracted_data["experience"]["total_years"],
            "total_skills": extracted_data["skills"]["total_skills_found"],
            "total_projects": extracted_data["projects"]["total_projects"],
            "total_certifications": extracted_data["certifications"]["total_certifications"],
            "education_level": extracted_data["education"]["education_level"],
            "career_level": extracted_data["experience"]["career_level"],
            "primary_role": extracted_data["role_inference"]["primary_role"],
            "contact_completeness": len([v for v in extracted_data["contact_info"].values() if v]) / 6
        }


def main():
    """Main function for command line usage"""
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: python info_extractor.py '<resume_text>'"
        }))
        sys.exit(1)
    
    text = sys.argv[1]
    extractor = InformationExtractor()
    result = extractor.extract_all_information(text)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
