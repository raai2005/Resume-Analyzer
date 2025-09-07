import { UploadedFile, ValidationResult } from './fileValidation';

/**
 * Type definitions for the Resume Analyzer API
 */

export interface ResumeAnalysisRequest {
  file: UploadedFile;
  jobTitle?: string;
  jobDescription?: string;
}

export interface ResumeAnalysisResponse {
  resumeId: string;
  filename: string;
  fileSize: number;
  fileType: string;
  uploadedAt: string;
  jobTitle?: string;
  hasJobDescription: boolean;
  status: 'ready_for_analysis' | 'processing' | 'completed' | 'error';
  validationResult: ValidationResult;
}

export interface ErrorResponse {
  error: string;
  message: string;
  timestamp?: string;
  details?: string;
}

export interface ApiResponse<T = any> {
  success?: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp?: string;
}

// Export specific types for use in other modules
export type { UploadedFile, ValidationResult } from './fileValidation';
