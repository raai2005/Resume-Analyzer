# Resume Analyzer Backend API

TypeScript/Express.js backend for the Resume Analyzer application.

## Setup

1. **Install dependencies:**

   ```bash
   npm install
   ```

2. **Environment Configuration:**

   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env with your specific values
   nano .env
   ```

3. **Development:**

   ```bash
   # Start development server with hot reload
   npm run dev

   # Build TypeScript
   npm run build

   # Start production server
   npm start
   ```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `PORT` - Server port (default: 3002)
- `FRONTEND_URL` - Frontend URL for CORS
- `MAX_FILE_SIZE` - Maximum file upload size in bytes
- `SESSION_SECRET` - Secret key for sessions (change in production!)

## API Endpoints

- `GET /health` - Health check
- `POST /analyze` - Upload and analyze resume
- `GET /resume/:id/status` - Get analysis status

## File Upload

Supports PDF, DOC, and DOCX files with:

- File type validation
- Size limits (10MB default)
- Basic malware/macro detection
- Secure file storage

## Security Features

- CORS protection
- Rate limiting
- File validation
- Helmet security headers
- Input sanitization
