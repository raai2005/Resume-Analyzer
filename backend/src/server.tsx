import express, { Express, Request, Response, NextFunction } from 'express';
import multer, { MulterError } from 'multer';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

import { 
  validateUploadedFile, 
  ALLOWED_MIME_TYPES, 
  MAX_FILE_SIZE,
  type UploadedFile,
  type ValidationResult 
} from './fileValidation';

import { 
  documentParserService,
  type ParsedDocument 
} from './documentParser';

// Load environment variables
dotenv.config();

const app: Express = express();
const PORT: number = parseInt(process.env.PORT || '3002', 10);

// Define interfaces for request/response types
interface AnalyzeRequestBody {
  job_title?: string;
  job_description?: string;
  company?: string;
  required_skills?: string; // JSON string of skills array
  preferred_skills?: string; // JSON string of skills array
}

interface FileMetadata {
  resumeId: string;
  originalName: string;
  filename: string;
  size: number;
  mimeType: string;
  uploadedAt: string;
  jobTitle: string | null;
  jobDescription: string | null;
  status: string;
  filePath: string;
}

interface ApiResponse<T = any> {
  success?: boolean;
  error?: string;
  message?: string;
  data?: T;
  timestamp?: string;
  retryAfter?: string;
  details?: string;
}

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));

// Rate limiting
const uploadLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // limit each IP to 10 uploads per windowMs
  message: {
    error: 'Too many upload attempts, please try again later',
    retryAfter: '15 minutes'
  } as ApiResponse,
  standardHeaders: true,
  legacyHeaders: false,
});

// Basic middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Ensure uploads directory exists
const uploadsDir: string = path.join(__dirname, '..', 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req: Request, file: Express.Multer.File, cb: (error: Error | null, destination: string) => void) {
    cb(null, uploadsDir);
  },
  filename: function (req: Request, file: Express.Multer.File, cb: (error: Error | null, filename: string) => void) {
    // Generate unique filename with timestamp and UUID
    const uniqueSuffix: string = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const fileExtension: string = path.extname(file.originalname);
    cb(null, `resume-${uniqueSuffix}${fileExtension}`);
  }
});

// File filter for initial validation
const fileFilter = (req: Request, file: Express.Multer.File, cb: multer.FileFilterCallback): void => {
  // Check MIME type
  if (ALLOWED_MIME_TYPES.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new Error(`Invalid file type. Allowed types: PDF, DOC, DOCX`));
  }
};

const upload = multer({
  storage: storage,
  limits: {
    fileSize: MAX_FILE_SIZE,
    files: 1 // Only allow single file upload
  },
  fileFilter: fileFilter
});

// Health check endpoint
app.get('/health', (req: Request, res: Response<ApiResponse>) => {
  res.status(200).json({
    success: true,
    message: 'Resume Analyzer API is running',
    timestamp: new Date().toISOString()
  });
});

// Main analyze endpoint
app.post('/analyze', uploadLimiter, upload.single('file'), async (req: Request<{}, ApiResponse, AnalyzeRequestBody>, res: Response<ApiResponse>) => {
  let uploadedFilePath: string | null = null;
  
  try {
    // Check if file was uploaded
    if (!req.file) {
      return res.status(400).json({
        error: 'No file uploaded',
        message: 'Please upload a resume file (PDF, DOC, or DOCX)'
      });
    }

    uploadedFilePath = req.file.path;

    // Extract form data
    const { 
      job_title, 
      job_description, 
      company, 
      required_skills: requiredSkillsStr, 
      preferred_skills: preferredSkillsStr 
    }: AnalyzeRequestBody = req.body;

    // Parse skills arrays from JSON strings
    let requiredSkills: string[] | undefined;
    let preferredSkills: string[] | undefined;
    
    try {
      if (requiredSkillsStr) {
        requiredSkills = JSON.parse(requiredSkillsStr);
      }
      if (preferredSkillsStr) {
        preferredSkills = JSON.parse(preferredSkillsStr);
      }
    } catch (parseError) {
      console.warn('Failed to parse skills arrays:', parseError);
      // Continue without skills arrays
    }

    // Convert Express.Multer.File to UploadedFile type
    const uploadedFile: UploadedFile = {
      fieldname: req.file.fieldname,
      originalname: req.file.originalname,
      encoding: req.file.encoding,
      mimetype: req.file.mimetype,
      size: req.file.size,
      destination: req.file.destination,
      filename: req.file.filename,
      path: req.file.path
    };

    // Validate the uploaded file
    const validationResult: ValidationResult = await validateUploadedFile(uploadedFile);

    if (!validationResult.isValid) {
      // Clean up uploaded file if validation fails
      if (uploadedFilePath && fs.existsSync(uploadedFilePath)) {
        fs.unlinkSync(uploadedFilePath);
      }

      return res.status(400).json({
        error: 'File validation failed',
        message: validationResult.error,
        details: 'Please ensure your file is a valid PDF, DOC, or DOCX without macros'
      });
    }

    // Generate unique resume ID
    const resumeId: string = uuidv4();

    // Store file metadata (in production, this would go to a database)
    const fileMetadata: FileMetadata = {
      resumeId: resumeId,
      originalName: req.file.originalname,
      filename: req.file.filename,
      size: req.file.size,
      mimeType: req.file.mimetype,
      uploadedAt: new Date().toISOString(),
      jobTitle: job_title || null,
      jobDescription: job_description || null,
      status: 'uploaded',
      filePath: req.file.path
    };

    // In production, save metadata to database
    // For now, we'll save to a JSON file for demo purposes
    const metadataPath: string = path.join(uploadsDir, `${resumeId}-metadata.json`);
    fs.writeFileSync(metadataPath, JSON.stringify(fileMetadata, null, 2));

    // Log successful upload
    console.log(`✅ Resume uploaded successfully:`, {
      resumeId,
      filename: req.file.originalname,
      size: `${(req.file.size / 1024).toFixed(2)} KB`,
      jobTitle: job_title || 'Not specified'
    });

    // Parse the document using Python scripts
    let parseResult: ParsedDocument;
    try {
      parseResult = await documentParserService.parseDocument(
        req.file.path, 
        job_description, 
        job_title, 
        company, 
        requiredSkills, 
        preferredSkills
      );
      
      // Update metadata with parsing results
      fileMetadata.status = parseResult.success ? 'parsed' : 'parse_failed';
      fs.writeFileSync(metadataPath, JSON.stringify(fileMetadata, null, 2));
      
      console.log(`📄 Document parsed:`, {
        resumeId,
        success: parseResult.success,
        sections: parseResult.section_detection.sections.length,
        characters: parseResult.summary.total_characters
      });
      
    } catch (parseError) {
      console.error('❌ Document parsing error:', parseError);
      
      // Still return success for upload, but with parsing error
      return res.status(200).json({
        success: true,
        message: 'Resume uploaded successfully, but parsing failed',
        data: {
          resumeId: resumeId,
          filename: validationResult.fileInfo?.originalName,
          fileSize: validationResult.fileInfo?.size,
          fileType: validationResult.fileInfo?.extension,
          uploadedAt: fileMetadata.uploadedAt,
          jobTitle: job_title || null,
          hasJobDescription: !!job_description,
          status: 'upload_success_parse_failed',
          parseError: parseError instanceof Error ? parseError.message : 'Unknown parsing error'
        }
      });
    }

    // Return success response with parsing results
    res.status(200).json({
      success: true,
      message: 'Resume uploaded and processed successfully',
      data: {
        resumeId: resumeId,
        filename: validationResult.fileInfo?.originalName,
        fileSize: validationResult.fileInfo?.size,
        fileType: validationResult.fileInfo?.extension,
        uploadedAt: fileMetadata.uploadedAt,
        jobTitle: job_title || null,
        hasJobDescription: !!job_description,
        status: parseResult.success ? 'parsed' : 'parse_failed',
        parsing: {
          success: parseResult.success,
          totalCharacters: parseResult.summary.total_characters,
          totalWords: parseResult.summary.total_words,
          sectionsDetected: parseResult.summary.sections_detected,
          structureQuality: parseResult.summary.structure_quality,
          hasContact: parseResult.section_detection.structure_analysis.has_contact,
          hasExperience: parseResult.section_detection.structure_analysis.has_experience,
          hasEducation: parseResult.section_detection.structure_analysis.has_education,
          hasSkills: parseResult.section_detection.structure_analysis.has_skills,
          recommendations: parseResult.recommendations
        },
        contactInfo: parseResult.section_detection.contact_info,
        sections: parseResult.section_detection.sections.map(section => ({
          type: section.type,
          title: section.title,
          wordCount: section.word_count,
          confidence: section.confidence
        }))
      }
    });
    return;

  } catch (error: unknown) {
    // Clean up uploaded file on any error
    if (uploadedFilePath && fs.existsSync(uploadedFilePath)) {
      try {
        fs.unlinkSync(uploadedFilePath);
      } catch (cleanupError) {
        console.error('Failed to cleanup uploaded file:', cleanupError);
      }
    }

    console.error('❌ Upload error:', error);

    // Handle specific multer errors
    if (error instanceof MulterError) {
      if (error.code === 'LIMIT_FILE_SIZE') {
        return res.status(400).json({
          error: 'File too large',
          message: `File size exceeds the maximum limit of ${MAX_FILE_SIZE / (1024 * 1024)}MB`
        });
      }
      if (error.code === 'LIMIT_UNEXPECTED_FILE') {
        return res.status(400).json({
          error: 'Invalid file field',
          message: 'Please use the "file" field for upload'
        });
      }
    }

    // Generic error response
    const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred during file upload';
    res.status(500).json({
      error: 'Upload failed',
      message: errorMessage,
      timestamp: new Date().toISOString()
    });
    return;
  }
});

// Get resume status endpoint
app.get('/resume/:resumeId/status', (req: Request<{ resumeId: string }>, res: Response<ApiResponse>) => {
  try {
    const { resumeId }: { resumeId: string } = req.params;
    const metadataPath: string = path.join(uploadsDir, `${resumeId}-metadata.json`);

    if (!fs.existsSync(metadataPath)) {
      return res.status(404).json({
        error: 'Resume not found',
        message: 'No resume found with the provided ID'
      });
    }

    const metadata: FileMetadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
    
    res.status(200).json({
      success: true,
      data: {
        resumeId: metadata.resumeId,
        status: metadata.status,
        filename: metadata.originalName,
        uploadedAt: metadata.uploadedAt
      }
    });
    return;

  } catch (error: unknown) {
    console.error('❌ Status check error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to check resume status';
    res.status(500).json({
      error: 'Status check failed',
      message: errorMessage
    });
    return;
  }
});

// Get full parsed resume data endpoint
app.get('/resume/:resumeId/parsed', async (req: Request<{ resumeId: string }>, res: Response<ApiResponse>) => {
  try {
    const { resumeId }: { resumeId: string } = req.params;
    const metadataPath: string = path.join(uploadsDir, `${resumeId}-metadata.json`);

    if (!fs.existsSync(metadataPath)) {
      return res.status(404).json({
        error: 'Resume not found',
        message: 'No resume found with the provided ID'
      });
    }

    const metadata: FileMetadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
    
    // Re-parse the document to get latest data
    if (!fs.existsSync(metadata.filePath)) {
      return res.status(404).json({
        error: 'Resume file not found',
        message: 'The resume file is no longer available'
      });
    }

    const parseResult: ParsedDocument = await documentParserService.parseDocument(metadata.filePath);
    
    res.status(200).json({
      success: true,
      data: {
        resumeId: metadata.resumeId,
        filename: metadata.originalName,
        uploadedAt: metadata.uploadedAt,
        jobTitle: metadata.jobTitle,
        jobDescription: metadata.jobDescription,
        parsing: parseResult
      }
    });
    return;

  } catch (error: unknown) {
    console.error('❌ Parse data retrieval error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to retrieve parsed data';
    res.status(500).json({
      error: 'Parse data retrieval failed',
      message: errorMessage
    });
    return;
  }
});

// Get parser capabilities endpoint  
app.get('/capabilities', async (req: Request, res: Response<ApiResponse>) => {
  try {
    const capabilities = await documentParserService.getCapabilities();
    
    res.status(200).json({
      success: true,
      data: capabilities
    });
    return;

  } catch (error: unknown) {
    console.error('❌ Capabilities check error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to check capabilities';
    res.status(500).json({
      error: 'Capabilities check failed',
      message: errorMessage
    });
    return;
  }
});

// Error handling middleware
app.use((error: Error, req: Request, res: Response<ApiResponse>, next: NextFunction) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    error: 'Internal server error',
    message: 'An unexpected error occurred'
  });
});

// 404 handler
app.use('*', (req: Request, res: Response<ApiResponse>) => {
  res.status(404).json({
    error: 'Endpoint not found',
    message: `The endpoint ${req.method} ${req.originalUrl} does not exist`
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Resume Analyzer API running on port ${PORT}`);
  console.log(`📁 Upload directory: ${uploadsDir}`);
  console.log(`🔒 Security features enabled: CORS, Helmet, Rate Limiting`);
  console.log(`📋 Accepted file types: PDF, DOC, DOCX`);
  console.log(`📏 Max file size: ${MAX_FILE_SIZE / (1024 * 1024)}MB`);
});

export default app;
