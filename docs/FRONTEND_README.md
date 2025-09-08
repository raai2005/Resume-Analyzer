# Resume Analyzer Frontend

## 🎨 Architecture Overview

The Resume Analyzer frontend is built with **Next.js 15** and **React 19**, providing a modern, responsive user interface for comprehensive resume analysis and feedback.

## 🚀 Tech Stack

### Core Framework

- **Next.js 15.5.2** - React-based full-stack framework with Turbopack
- **React 19.1.0** - Latest React with concurrent features
- **TypeScript 5** - Type-safe development
- **Tailwind CSS 4** - Utility-first CSS framework

### Build & Development Tools

- **Turbopack** - Ultra-fast bundler (Next.js native)
- **ESLint 9** - Code quality and consistency
- **PostCSS** - CSS processing and optimization
- **Node.js 20+** - Runtime environment

### State Management

- **React Hooks** - useState, useEffect for local state
- **Form Handling** - Native FormData API integration
- **File Upload** - Built-in file handling with validation

## 📁 Project Structure

```
src/
├── app/
│   ├── layout.tsx         # 🏗️ Root layout and global styles
│   ├── page.tsx          # 🏠 Main application page
│   ├── globals.css       # 🎨 Global CSS styles
│   └── favicon.ico       # 🔖 App icon
└── components/
    ├── index.ts          # 📦 Component exports
    ├── AnalysisResults.tsx    # 📊 Main results container
    ├── ATSAnalysis.tsx        # 🤖 ATS compatibility display
    ├── DetailedInsights.tsx   # 🔍 AI-powered insights
    ├── Recommendations.tsx    # 💡 Improvement suggestions
    ├── ScoreCard.tsx         # ⭐ Quality score visualization
    └── SkillsAnalysis.tsx    # 🛠️ Skills gap analysis
```

## 🔄 User Flow & Features

### 1. **File Upload Interface**

```
page.tsx → File validation → Progress indication
```

### 2. **Job Context Input**

```
Job Title + Description + Target Skills → Enhanced analysis context
```

### 3. **Real-time Analysis**

```
File upload → FastAPI backend → Live progress updates
```

### 4. **Results Display**

```
Analysis response → Component routing → Interactive visualizations
```

## 🎯 Core Components

### **page.tsx** - Main Application

- **Purpose**: Primary user interface and state management
- **Features**:
  - File upload with drag-and-drop
  - Job context form inputs
  - Analysis progress tracking
  - Results display coordination
- **State Management**:
  - `results` - Legacy analysis data
  - `enhancedResults` - New comprehensive analysis
  - `isLoading` - Upload/analysis state
  - `error` - Error handling and display

### **AnalysisResults.tsx** - Results Container

- **Purpose**: Main results display orchestration
- **Features**:
  - Component routing based on analysis type
  - Responsive layout management
  - Data validation and formatting
- **Props**: Analysis data object with comprehensive results

### **UI Components**

#### **ScoreCard.tsx**

- **Purpose**: Visual quality score display
- **Features**:
  - Animated progress rings
  - Color-coded scoring (red/yellow/green)
  - Category breakdown display
- **Styling**: Tailwind CSS with custom gradients

#### **ATSAnalysis.tsx**

- **Purpose**: ATS compatibility visualization
- **Features**:
  - Compatibility percentage
  - Keyword optimization insights
  - Format recommendations
  - Parsing quality metrics

#### **SkillsAnalysis.tsx**

- **Purpose**: Skills gap analysis and matching
- **Features**:
  - Matched skills highlighting
  - Missing skills identification
  - Skill categorization
  - Industry relevance scoring

#### **DetailedInsights.tsx**

- **Purpose**: AI-powered comprehensive analysis
- **Features**:
  - Section-by-section feedback
  - Content quality assessment
  - Professional presentation analysis
  - Industry-specific recommendations

#### **Recommendations.tsx**

- **Purpose**: Actionable improvement suggestions
- **Features**:
  - Prioritized recommendations
  - Category-based grouping
  - Implementation difficulty indicators
  - Impact assessment

## 🔌 API Integration

### **Backend Communication**

```typescript
// Primary endpoint (FastAPI Python)
const response = await fetch("http://localhost:8000/analyze-resume", {
  method: "POST",
  body: formData, // File + context data
});
```

### **Request Structure**

```typescript
FormData {
  file: File,                    // Resume file (PDF/DOCX)
  job_title?: string,           // Optional job context
  job_description?: string,     // Optional job posting
  target_skills?: string        // Optional skills list
}
```

### **Response Handling**

```typescript
interface AnalysisResponse {
  status: "success" | "error";
  status_code: number;
  message: string;
  data: {
    contact_info: ContactInfo;
    education: Education[];
    experience: Experience[];
    skills: SkillsAnalysis;
    ats_analysis: ATSResults;
    quality_analysis: QualityScores;
    ai_insights: AIInsights;
    recommendations: Recommendation[];
    // ... 30+ analysis categories
  };
}
```

## 🎨 Styling & Design

### **Tailwind CSS Architecture**

- **Utility-first approach** for rapid development
- **Custom color scheme** for professional appearance
- **Responsive design** with mobile-first approach
- **Component-specific styles** for reusable patterns

### **Design System**

```css
/* Color Palette */
Primary: Blue gradients (#3B82F6 → #1D4ED8)
Success: Green (#10B981)
Warning: Yellow (#F59E0B)
Error: Red (#EF4444)
Neutral: Gray scale (#F8FAFC → #1E293B)

/* Typography */
Headings: font-bold, various sizes
Body: font-medium, readable line-height
Labels: font-semibold, smaller sizes

/* Layout */
Cards: rounded-lg, shadow-lg, padding
Containers: max-width constraints
Grid: responsive grid layouts
```

### **Interactive Elements**

- **Hover effects** on buttons and cards
- **Loading animations** during analysis
- **Progress indicators** for file upload
- **Smooth transitions** between states

## 📱 Responsive Design

### **Breakpoint Strategy**

```css
Mobile: < 640px (sm)
Tablet: 640px - 1024px (md-lg)
Desktop: > 1024px (xl+)
```

### **Layout Adaptations**

- **Mobile**: Single column, stacked components
- **Tablet**: Two-column layout with flexible wrapping
- **Desktop**: Multi-column grid with sidebar navigation

### **Component Responsiveness**

- **File upload**: Touch-friendly on mobile
- **Score cards**: Scalable visualizations
- **Analysis results**: Collapsible sections on small screens

## 🚀 Development & Build

### **Development Server**

```bash
# Start development server with Turbopack
npm run dev

# Access application
http://localhost:3000
```

### **Build Process**

```bash
# Production build
npm run build

# Start production server
npm run start

# Lint code
npm run lint
```

### **Build Optimization**

- **Turbopack**: Ultra-fast hot reload and bundling
- **Static generation**: Pre-rendered pages where possible
- **Code splitting**: Automatic bundle optimization
- **Image optimization**: Next.js built-in image handling

## 🔧 Configuration Files

### **next.config.ts**

```typescript
// Next.js configuration
export default {
  // Turbopack enabled by default
  // Custom webpack configurations
  // Environment-specific settings
};
```

### **tailwind.config.js**

```javascript
// Tailwind CSS customization
module.exports = {
  // Custom colors, fonts, spacing
  // Component-specific utilities
  // Responsive breakpoints
};
```

### **eslint.config.mjs**

```javascript
// ESLint rules for code quality
export default [
  // TypeScript rules
  // React best practices
  // Custom project rules
];
```

## 🛡️ Security & Performance

### **Security Features**

- **File type validation** on frontend
- **Size limits** before upload
- **CORS handling** for API communication
- **XSS prevention** through React's built-in protection

### **Performance Optimizations**

- **Code splitting** for faster initial load
- **Lazy loading** for analysis components
- **Memoization** for expensive computations
- **Optimized images** and assets

### **Error Handling**

```typescript
// Comprehensive error boundaries
try {
  // API call
} catch (error) {
  setError("User-friendly error message");
  // Log technical details
}
```

## 🔄 State Management

### **Local State (React Hooks)**

```typescript
// File upload state
const [file, setFile] = useState<File | null>(null);

// Analysis results
const [results, setResults] = useState<AnalysisData | null>(null);

// UI state
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
```

### **Form Management**

```typescript
// Job context form
const [jobTitle, setJobTitle] = useState("");
const [jobDescription, setJobDescription] = useState("");
const [targetSkills, setTargetSkills] = useState("");
```

## 🎯 Future Enhancements

### **Planned Features**

- **Real-time collaboration** for team reviews
- **Export functionality** (PDF reports)
- **Comparison tools** for multiple resumes
- **Analytics dashboard** for hiring managers

### **Technical Improvements**

- **Offline support** with service workers
- **Progressive Web App** features
- **Advanced state management** (Redux Toolkit)
- **End-to-end testing** with Playwright

### **UI/UX Enhancements**

- **Dark mode** theme toggle
- **Accessibility improvements** (WCAG compliance)
- **Animation library** integration
- **Advanced data visualizations**

## 📞 Development Support

### **Hot Reload & Debugging**

- **Turbopack** provides instant feedback
- **React DevTools** for component inspection
- **Browser DevTools** for performance analysis
- **Error boundaries** for graceful error handling

### **Common Development Tasks**

```bash
# Add new component
mkdir src/components/NewComponent
touch src/components/NewComponent/index.tsx

# Update dependencies
npm update

# Type checking
npm run type-check

# Build analysis
npm run build --analyze
```

---

## 📞 Support

For frontend-specific issues:

1. Check browser console for errors
2. Verify React component props and state
3. Test responsive design on different devices
4. Validate API communication in Network tab

**Frontend Entry Point**: `src/app/page.tsx`  
**Component Library**: `src/components/`  
**Styling**: `src/app/globals.css` + Tailwind utilities
