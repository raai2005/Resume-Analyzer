import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import fs from 'fs';

/**
 * TypeScript interface for Python document parsing integration
 */

export interface TextNormalizationResult {
  original: string;
  normalized: string;
  lowercase_copy: string;
  sections: NormalizedSection[];
  bullet_points: BulletPoint[];
  statistics: NormalizationStatistics;
  cleaning_operations: string[];
  success?: boolean;
  error?: string;
}

export interface NormalizedSection {
  title: string;
  content: string;
  line_start: number;
  line_end: number;
  word_count: number;
  line_count: number;
}

export interface BulletPoint {
  line_number: number;
  full_line: string;
  content: string;
  bullet_type: string;
  word_count: number;
  char_count: number;
}

export interface NormalizationStatistics {
  original_length: number;
  normalized_length: number;
  compression_ratio: number;
  original_lines: number;
  normalized_lines: number;
  original_words: number;
  normalized_words: number;
  sections_found: number;
  bullet_points_found: number;
  bullet_types: string[];
  avg_section_length: number;
  avg_bullet_length: number;
}

export interface InformationExtractionResult {
  success: boolean;
  contact_info: ExtractedContactInfo;
  experience: ExtractedExperience;
  education: ExtractedEducation;
  skills: ExtractedSkills;
  projects: ExtractedProjects;
  certifications: ExtractedCertifications;
  role_inference: RoleInference;
  summary_stats: ExtractionSummaryStats;
  extraction_metadata: ExtractionMetadata;
  error?: string;
}

export interface ExtractedContactInfo {
  name?: string;
  email?: string;
  phone?: string;
  linkedin?: string;
  github?: string;
  portfolio?: string;
  address?: string;
  confidence_scores: Record<string, number>;
}

export interface ExtractedExperience {
  total_years: number;
  positions: WorkPosition[];
  companies: string[];
  internships: WorkPosition[];
  full_time_jobs: WorkPosition[];
  current_position?: WorkPosition;
  career_level: string;
}

export interface WorkPosition {
  title: string;
  company: string;
  description: string;
  start_date?: string;
  end_date?: string;
  duration_months?: number;
  is_current?: boolean;
}

export interface ExtractedEducation {
  degrees: string[];
  institutions: string[];
  graduation_years: number[];
  highest_degree?: string;
  education_level: string;
}

export interface ExtractedSkills {
  programming_languages: string[];
  web_technologies: string[];
  databases: string[];
  cloud_platforms: string[];
  tools_frameworks: string[];
  soft_skills: string[];
  matched_skills: string[];
  missing_important_skills: string[];
  skill_categories: Record<string, number>;
  total_skills_found: number;
}

export interface ExtractedProjects {
  projects: ProjectInfo[];
  total_projects: number;
  technologies_used: string[];
  project_types: string[];
}

export interface ProjectInfo {
  title: string;
  description: string;
  technologies: string[];
  url?: string;
}

export interface ExtractedCertifications {
  certifications: CertificationInfo[];
  total_certifications: number;
  providers: string[];
  certification_years: number[];
}

export interface CertificationInfo {
  name: string;
  provider?: string;
  year?: number;
  url?: string;
}

export interface RoleInference {
  primary_role: string;
  confidence: number;
  role_scores: Record<string, number>;
  supporting_keywords: string[];
}

export interface ExtractionSummaryStats {
  total_experience_years: number;
  total_skills: number;
  total_projects: number;
  total_certifications: number;
  education_level: string;
  career_level: string;
  primary_role: string;
  contact_completeness: number;
}

export interface ExtractionMetadata {
  text_length: number;
  extraction_timestamp: string;
  patterns_used: string[];
}

export interface AIAnalysisResult {
  success: boolean;
  formatted_analysis?: FormattedAnalysis;
  ai_powered: boolean;
  model_used: string;
  has_job_context: boolean;
  error?: string;
}

export interface FormattedAnalysis {
  summary: AnalysisSummary;
  strengths: string[];
  improvements: string[];
  recommendations: AnalysisRecommendations;
  contact_completeness: number;
  experience_quality: string;
  skills_relevance: string;
  job_match?: JobMatchAnalysis;
  skills_gap?: SkillsGapAnalysis;
}

export interface AnalysisSummary {
  overall_score: number;
  ats_compatibility: string;
  experience_level: string;
  target_roles: string[];
}

export interface AnalysisRecommendations {
  immediate_actions: string[];
  format_improvements: string[];
  content_improvements: string[];
  keyword_optimization: string[];
  industry_alignment?: string[];
}

export interface JobMatchAnalysis {
  overall_fit: number;
  skills_match: number;
  experience_relevance: string;
  missing_required_skills: string[];
  missing_preferred_skills: string[];
  competitive_advantages: string[];
  customization_tips: string[];
  interview_prep: string[];
  salary_points: string[];
}

export interface SkillsGapAnalysis {
  overall_coverage: number;
  gap_level: string;
  gap_description: string;
  target_source: string;
  matched_skills: string[];
  missing_required: string[];
  missing_preferred: string[];
  bonus_skills: string[];
  priority_skills_to_add: string[];
  recommendations: {
    immediate_priority: string[];
    medium_priority: string[];
    long_term: string[];
    leverage_existing: string[];
    source_note: string[];
  };
  coverage_breakdown: {
    required_coverage: number;
    preferred_coverage: number;
    total_target_skills: number;
    total_resume_skills: number;
  };
}

export interface ATSAnalysisResult {
  file_info: {
    filename: string;
    extension: string;
    size_bytes: number;
    size_mb: number;
    exists: boolean;
  };
  file_format_analysis: {
    format_score: number;
    is_preferred_format: boolean;
    is_scanned_pdf: boolean;
    format_warnings: string[];
    format_recommendations: string[];
  };
  layout_analysis: {
    layout_score: number;
    has_multi_column: boolean;
    excessive_tables: boolean;
    excessive_images: boolean;
    excessive_textboxes: boolean;
    layout_warnings: string[];
    layout_recommendations: string[];
  };
  content_analysis: {
    content_score: number;
    has_required_sections: Record<string, boolean>;
    contact_info_complete: boolean;
    excessive_symbols: boolean;
    content_warnings: string[];
    content_recommendations: string[];
  };
  length_analysis: {
    length_score: number;
    word_count: number;
    estimated_pages: number;
    experience_years: number;
    recommended_pages: number;
    length_appropriate: boolean;
    length_warnings: string[];
    length_recommendations: string[];
  };
  ats_score: {
    total_score: number;
    breakdown: {
      file_format: number;
      layout: number;
      content: number;
      length: number;
    };
    critical_penalty: boolean;
    max_possible_score: number;
  };
  recommendations: {
    critical: string[];
    high_priority: string[];
    medium_priority: string[];
    low_priority: string[];
  };
  compatibility_level: string;
  priority_issues: string[];
}

export interface QualityAnalysisResult {
  overall_score: number;
  quality_level: string;
  score_breakdown: {
    content_fit: QualityScoreCategory;
    clarity_quantification: QualityScoreCategory;
    structure_readability: QualityScoreCategory;
    ats_friendliness: QualityScoreCategory;
  };
  recommendations: {
    critical: string[];
    high_priority: string[];
    medium_priority: string[];
    low_priority: string[];
  };
  scoring_rubric: {
    description: string;
    categories: Record<string, string>;
  };
}

export interface QualityScoreCategory {
  score: number;
  max_possible: number;
  percentage: number;
  details: QualityCategoryDetails;
}

export interface QualityCategoryDetails {
  // Content Fit Details
  skills_coverage_score?: number;
  experience_alignment_score?: number;
  skills_analysis?: {
    target_skills_count: number;
    matched_skills_count: number;
    coverage_percentage: number;
    matched_skills: string[];
    missing_skills: string[];
    bonus_skills: string[];
  };
  experience_analysis?: {
    actual_years: number;
    target_years?: number;
    career_level: string;
    alignment_type: string;
  };
  
  // Clarity & Quantification Details
  metrics_score?: number;
  action_verbs_score?: number;
  metrics_analysis?: {
    total_bullet_points: number;
    lines_with_metrics: number;
    metrics_percentage: number;
    total_metrics_found: number;
    sample_metrics: string[];
    improvement_potential: number;
  };
  action_verbs_analysis?: {
    total_bullet_points: number;
    verb_distribution: {
      strong: number;
      moderate: number;
      weak: number;
      none: number;
    };
    strong_verb_percentage: number;
    sample_verbs_found: string[];
    weak_or_missing_count: number;
  };
  
  // Structure & Readability Details
  sections_score?: number;
  readability_score?: number;
  sections_analysis?: {
    required_sections: string[];
    sections_found: Record<string, boolean>;
    found_count: number;
    required_count: number;
    completion_percentage: number;
    missing_sections: string[];
  };
  readability_analysis?: {
    total_sentences: number;
    average_sentence_length: number;
    long_sentences_count: number;
    long_sentences_percentage: number;
    passive_sentences_count: number;
    passive_voice_percentage: number;
    readability_issues: string[];
  };
  
  // ATS Friendliness Details (can reuse existing ATSAnalysisResult or create simplified version)
  score_source?: string;
  original_ats_score?: number;
  compatibility_level?: string;
  priority_issues?: string[];
  symbol_count?: number;
  detected_issues?: string[];
  recommendations?: string[];
}

export interface ParsedDocument {
  success: boolean;
  file_info: {
    filename: string;
    extension: string;
    size_bytes: number;
    size_mb: number;
  };
  text_extraction: {
    success: boolean;
    text: string;
    metadata: Record<string, any>;
    parsing_method?: string;
    is_scanned?: boolean;
    char_count?: number;
    error?: string;
  };
  text_normalization?: TextNormalizationResult;
  information_extraction?: InformationExtractionResult;
  ai_analysis?: AIAnalysisResult;
  ats_analysis?: ATSAnalysisResult;
  quality_analysis?: QualityAnalysisResult;
  section_detection: {
    success: boolean;
    sections: ResumeSection[];
    contact_info: ContactInfo;
    structure_analysis: StructureAnalysis;
    error?: string;
  };
  summary: {
    total_characters: number;
    total_words: number;
    total_lines: number;
    sections_detected: number;
    parsing_method?: string;
    is_scanned: boolean;
    structure_quality: string;
    // Text normalization summary fields
    normalized_characters?: number;
    normalized_words?: number;
    bullet_points_found?: number;
    sections_by_headings?: number;
    compression_ratio?: number;
    // Information extraction summary fields
    total_experience_years?: number;
    total_skills_found?: number;
    total_projects?: number;
    total_certifications?: number;
    education_level?: string;
    career_level?: string;
    primary_role?: string;
    // AI analysis scores
    ai_overall_score?: number;
    ats_compatibility?: string;
    contact_completeness?: number;
    ai_powered?: boolean;
    // ATS analysis scores
    ats_score?: number;
    ats_compatibility_level?: string;
    ats_priority_issues?: number;
    ats_word_count?: number;
    ats_estimated_pages?: number;
    // Quality analysis scores
    quality_score?: number;
    quality_level?: string;
    content_fit_score?: number;
    clarity_score?: number;
    structure_score?: number;
  };
  recommendations: string[];
  error?: string;
}

export interface ResumeSection {
  type: string;
  title: string;
  content: string;
  start_line: number;
  end_line: number;
  confidence: number;
  keywords_found: string[];
  word_count: number;
}

export interface ContactInfo {
  email?: string;
  phone?: string;
  linkedin?: string;
  github?: string;
  website?: string;
  address?: string;
}

export interface StructureAnalysis {
  total_sections: number;
  sections_found: string[];
  has_contact: boolean;
  has_experience: boolean;
  has_education: boolean;
  has_skills: boolean;
  avg_confidence: number;
  structure_quality: string;
  recommendations: string[];
}

export interface ParsingCapabilities {
  supported_formats: string[];
  parsers_available: {
    pdf: boolean;
    docx: boolean;
    section_detector: boolean;
  };
  features: {
    text_extraction: boolean;
    section_detection: boolean;
    contact_extraction: boolean;
    metadata_extraction: boolean;
    scanned_pdf_detection: boolean;
    structure_analysis: boolean;
  };
}

export class DocumentParserService {
  private pythonScriptsPath: string;
  private documentParserScript: string;
  private pythonExecutable: string;

  constructor() {
    this.pythonScriptsPath = path.join(__dirname, '..', '..', 'python_scripts');
    this.documentParserScript = path.join(this.pythonScriptsPath, 'document_parser.py');
    this.pythonExecutable = process.env.PYTHON_EXECUTABLE || 'python';
  }

  /**
   * Parse a document file and extract structured information
   */
  async parseDocument(
    filePath: string,
    jobDescription?: string,
    jobTitle?: string,
    company?: string,
    requiredSkills?: string[],
    preferredSkills?: string[]
  ): Promise<ParsedDocument> {
    try {
      // Validate input
      if (!fs.existsSync(filePath)) {
        throw new Error(`File not found: ${filePath}`);
      }

      if (!fs.existsSync(this.documentParserScript)) {
        throw new Error(`Parser script not found: ${this.documentParserScript}`);
      }

      // Prepare Python script arguments
      const args = [filePath];
      
      // Add job context parameters (use 'None' for undefined values)
      args.push(jobDescription || 'None');
      args.push(jobTitle || 'None');
      args.push(company || 'None');
      args.push(requiredSkills ? JSON.stringify(requiredSkills) : 'None');
      args.push(preferredSkills ? JSON.stringify(preferredSkills) : 'None');

      // Execute Python parser
      const result = await this.executePythonScript(this.documentParserScript, args);
      
      // Validate and return result
      if (!this.isValidParseResult(result)) {
        throw new Error('Invalid parsing result structure');
      }

      return result as ParsedDocument;

    } catch (error) {
      console.error('Document parsing error:', error);
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown parsing error',
        file_info: {
          filename: path.basename(filePath),
          extension: path.extname(filePath),
          size_bytes: 0,
          size_mb: 0
        },
        text_extraction: {
          success: false,
          text: '',
          metadata: {},
          error: error instanceof Error ? error.message : 'Text extraction failed'
        },
        section_detection: {
          success: false,
          sections: [],
          contact_info: {},
          structure_analysis: {
            total_sections: 0,
            sections_found: [],
            has_contact: false,
            has_experience: false,
            has_education: false,
            has_skills: false,
            avg_confidence: 0,
            structure_quality: 'unknown',
            recommendations: []
          },
          error: error instanceof Error ? error.message : 'Section detection failed'
        },
        summary: {
          total_characters: 0,
          total_words: 0,
          total_lines: 0,
          sections_detected: 0,
          is_scanned: false,
          structure_quality: 'unknown'
        },
        recommendations: ['Document parsing failed - please check file format and try again']
      };
    }
  }

  /**
   * Get parsing capabilities and system status
   */
  async getCapabilities(): Promise<ParsingCapabilities> {
    try {
      const capabilitiesScript = path.join(this.pythonScriptsPath, 'document_parser.py');
      
      // Check if Python and scripts are available
      const pythonAvailable = await this.checkPythonAvailable();
      const scriptsExist = this.checkScriptsExist();

      if (!pythonAvailable) {
        throw new Error('Python executable not found');
      }

      return {
        supported_formats: ['.pdf', '.docx', '.doc'],
        parsers_available: scriptsExist,
        features: {
          text_extraction: scriptsExist.pdf && scriptsExist.docx,
          section_detection: scriptsExist.section_detector,
          contact_extraction: scriptsExist.section_detector,
          metadata_extraction: true,
          scanned_pdf_detection: scriptsExist.pdf,
          structure_analysis: scriptsExist.section_detector
        }
      };

    } catch (error) {
      console.error('Error checking capabilities:', error);
      
      return {
        supported_formats: [],
        parsers_available: {
          pdf: false,
          docx: false,
          section_detector: false
        },
        features: {
          text_extraction: false,
          section_detection: false,
          contact_extraction: false,
          metadata_extraction: false,
          scanned_pdf_detection: false,
          structure_analysis: false
        }
      };
    }
  }

  /**
   * Execute a Python script and return parsed JSON result
   */
  private async executePythonScript(scriptPath: string, args: string[]): Promise<any> {
    return new Promise((resolve, reject) => {
      const pythonProcess: ChildProcess = spawn(this.pythonExecutable, [scriptPath, ...args], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: this.pythonScriptsPath
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout?.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr?.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python script failed with code ${code}: ${stderr}`));
          return;
        }

        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (error) {
          reject(new Error(`Failed to parse JSON output: ${error}\nOutput: ${stdout}`));
        }
      });

      pythonProcess.on('error', (error) => {
        reject(new Error(`Failed to start Python process: ${error.message}`));
      });

      // Set timeout
      setTimeout(() => {
        pythonProcess.kill();
        reject(new Error('Python script execution timed out'));
      }, 60000); // 60 second timeout
    });
  }

  /**
   * Check if Python is available
   */
  private async checkPythonAvailable(): Promise<boolean> {
    try {
      await this.executePythonScript('-c', ['print("test")']);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Check if required Python scripts exist
   */
  private checkScriptsExist(): { pdf: boolean; docx: boolean; section_detector: boolean } {
    return {
      pdf: fs.existsSync(path.join(this.pythonScriptsPath, 'pdf_parser.py')),
      docx: fs.existsSync(path.join(this.pythonScriptsPath, 'docx_parser.py')),
      section_detector: fs.existsSync(path.join(this.pythonScriptsPath, 'section_detector.py'))
    };
  }

  /**
   * Validate parsing result structure
   */
  private isValidParseResult(result: any): boolean {
    return (
      result &&
      typeof result === 'object' &&
      typeof result.success === 'boolean' &&
      result.file_info &&
      result.text_extraction &&
      result.section_detection &&
      result.summary
    );
  }

  /**
   * Install Python dependencies
   */
  async installDependencies(): Promise<{ success: boolean; message: string }> {
    try {
      const requirementsPath = path.join(this.pythonScriptsPath, 'requirements.txt');
      
      if (!fs.existsSync(requirementsPath)) {
        return {
          success: false,
          message: 'requirements.txt not found'
        };
      }

      await this.executePythonScript('-m', ['pip', 'install', '-r', requirementsPath]);
      
      return {
        success: true,
        message: 'Dependencies installed successfully'
      };

    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to install dependencies'
      };
    }
  }
}

// Export singleton instance
export const documentParserService = new DocumentParserService();
