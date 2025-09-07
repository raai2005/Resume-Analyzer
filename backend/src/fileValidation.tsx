import fs from 'fs';
import path from 'path';
import yauzl from 'yauzl';
import { fileTypeFromBuffer } from 'file-type';
import { Express } from 'express';

/**
 * File validation utilities for resume uploads
 */

const ALLOWED_MIME_TYPES: string[] = [
  'application/pdf',
  'application/msword', // .doc
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document' // .docx
];

const ALLOWED_EXTENSIONS: string[] = ['.pdf', '.doc', '.docx'];
const MAX_FILE_SIZE: number = 10 * 1024 * 1024; // 10MB

interface FileInfo {
  originalName: string;
  size: number;
  mimeType: string;
  extension: string;
}

interface ValidationResult {
  isValid: boolean;
  fileInfo?: FileInfo;
  error?: string;
}

interface UploadedFile {
  fieldname: string;
  originalname: string;
  encoding: string;
  mimetype: string;
  size: number;
  destination: string;
  filename: string;
  path: string;
  buffer?: Buffer;
}

/**
 * Validate file type based on content and extension
 */
async function validateFileType(buffer: Buffer, originalName: string): Promise<boolean> {
  const ext: string = path.extname(originalName).toLowerCase();
  
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    throw new Error(`Invalid file extension. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`);
  }

  // For PDF files, check magic bytes
  if (ext === '.pdf') {
    if (buffer.slice(0, 4).toString() !== '%PDF') {
      throw new Error('Invalid PDF file format');
    }
  }

  // For DOC files, check OLE header
  if (ext === '.doc') {
    const oleHeader: Buffer = buffer.slice(0, 8);
    if (!oleHeader.toString('hex').startsWith('d0cf11e0a1b11ae1')) {
      throw new Error('Invalid DOC file format');
    }
  }

  // For DOCX files, check ZIP header and validate structure
  if (ext === '.docx') {
    const zipHeader: Buffer = buffer.slice(0, 4);
    const zipHex: string = zipHeader.toString('hex');
    if (zipHex !== '504b0304' && zipHex !== '504b0506') {
      throw new Error('Invalid DOCX file format');
    }
    
    // Additional DOCX validation
    await validateDocxFile(buffer);
  }

  return true;
}

/**
 * Validate DOCX file structure and check for macros
 */
function validateDocxFile(buffer: Buffer): Promise<boolean> {
  return new Promise<boolean>((resolve, reject) => {
    yauzl.fromBuffer(buffer, { lazyEntries: true }, (err: Error | null, zipfile?: yauzl.ZipFile) => {
      if (err || !zipfile) {
        return reject(new Error('Invalid DOCX file structure'));
      }

      let hasWordDocument: boolean = false;
      let hasMacros: boolean = false;

      zipfile.readEntry();
      
      zipfile.on('entry', (entry: yauzl.Entry) => {
        // Check for required DOCX structure
        if (entry.fileName === 'word/document.xml') {
          hasWordDocument = true;
        }

        // Check for macro files (VBA)
        if (entry.fileName.includes('vba') || 
            entry.fileName.includes('macro') ||
            entry.fileName.endsWith('.bin') ||
            entry.fileName.includes('word/vbaProject.bin')) {
          hasMacros = true;
        }

        zipfile.readEntry();
      });

      zipfile.on('end', () => {
        if (!hasWordDocument) {
          return reject(new Error('Invalid DOCX file - missing required document structure'));
        }

        if (hasMacros) {
          return reject(new Error('DOCX files with macros are not allowed for security reasons'));
        }

        resolve(true);
      });

      zipfile.on('error', (err: Error) => {
        reject(new Error('Error reading DOCX file structure'));
      });
    });
  });
}

/**
 * Validate file size
 */
function validateFileSize(size: number): boolean {
  if (size > MAX_FILE_SIZE) {
    throw new Error(`File size exceeds limit. Maximum allowed: ${MAX_FILE_SIZE / (1024 * 1024)}MB`);
  }
  return true;
}

/**
 * Basic malware detection (simple heuristics)
 */
function basicMalwareCheck(buffer: Buffer, originalName: string): boolean {
  const fileName: string = originalName.toLowerCase();
  
  // Check for suspicious file patterns
  const suspiciousPatterns: RegExp[] = [
    /\.exe$/,
    /\.scr$/,
    /\.bat$/,
    /\.cmd$/,
    /\.com$/,
    /\.pif$/,
    /\.vbs$/,
    /\.js$/,
    /\.jar$/
  ];

  for (const pattern of suspiciousPatterns) {
    if (pattern.test(fileName)) {
      throw new Error('Suspicious file type detected');
    }
  }

  // Check for embedded executables in the beginning of file
  const header: string = buffer.slice(0, 100).toString();
  if (header.includes('MZ') || header.includes('PE')) {
    throw new Error('Executable content detected in file');
  }

  return true;
}

/**
 * Comprehensive file validation
 */
async function validateUploadedFile(file: UploadedFile): Promise<ValidationResult> {
  try {
    // Validate file size
    validateFileSize(file.size);

    // Read file buffer for content validation
    const buffer: Buffer = fs.readFileSync(file.path);

    // Basic malware check
    basicMalwareCheck(buffer, file.originalname);

    // Validate file type and content
    await validateFileType(buffer, file.originalname);

    return {
      isValid: true,
      fileInfo: {
        originalName: file.originalname,
        size: file.size,
        mimeType: file.mimetype,
        extension: path.extname(file.originalname).toLowerCase()
      }
    };
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown validation error';
    return {
      isValid: false,
      error: errorMessage
    };
  }
}

// Export types and functions
export {
  validateUploadedFile,
  ALLOWED_MIME_TYPES,
  ALLOWED_EXTENSIONS,
  MAX_FILE_SIZE,
  type FileInfo,
  type ValidationResult,
  type UploadedFile
};
