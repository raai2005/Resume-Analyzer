import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import fs from 'fs';

/**
 * TypeScript interface for Python document parsing integration
 */

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
  async parseDocument(filePath: string): Promise<ParsedDocument> {
    try {
      // Validate input
      if (!fs.existsSync(filePath)) {
        throw new Error(`File not found: ${filePath}`);
      }

      if (!fs.existsSync(this.documentParserScript)) {
        throw new Error(`Parser script not found: ${this.documentParserScript}`);
      }

      // Execute Python parser
      const result = await this.executePythonScript(this.documentParserScript, [filePath]);
      
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
