"use client";
import { useState } from "react";

// Define interfaces for the parsing results
interface ContactInfo {
  email?: string;
  phone?: string;
  linkedin?: string;
  github?: string;
  website?: string;
}

interface ResumeSection {
  type: string;
  title: string;
  wordCount: number;
  confidence: number;
}

interface ParsedResults {
  success: boolean;
  filename: string;
  parsing: {
    success: boolean;
    totalCharacters: number;
    totalWords: number;
    sectionsDetected: number;
    structureQuality: string;
    hasContact: boolean;
    hasExperience: boolean;
    hasEducation: boolean;
    hasSkills: boolean;
    recommendations: string[];
  };
  contactInfo: ContactInfo;
  sections: ResumeSection[];
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [jobTitle, setJobTitle] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [jobDescUrl, setJobDescUrl] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState<ParsedResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResults(null); // Clear previous results
      setError(null);
    }
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    
    setAnalyzing(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (jobTitle) formData.append('job_title', jobTitle);
      if (jobDesc) formData.append('job_description', jobDesc);
      
      const response = await fetch('http://localhost:3002/analyze', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (data.success && data.data) {
        setResults(data.data);
      } else {
        setError(data.message || 'Analysis failed');
      }
      
    } catch (err) {
      setError('Failed to connect to analysis service. Please ensure the backend is running.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-8 left-1/3 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
      
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="pt-12 pb-8 text-center">
          <div className="max-w-4xl mx-auto px-6">
            <h1 className="text-5xl md:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 mb-6 tracking-tight leading-tight">
              Resume Analyzer
            </h1>
            <p className="text-xl md:text-2xl text-slate-600 font-medium max-w-2xl mx-auto leading-relaxed">
              AI-powered resume analysis that helps you land your dream job
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-4 text-sm text-slate-500">
              <div className="flex items-center bg-white/70 backdrop-blur-sm px-4 py-2 rounded-full border border-white/40 shadow-sm">
                <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Instant Analysis
              </div>
              <div className="flex items-center bg-white/70 backdrop-blur-sm px-4 py-2 rounded-full border border-white/40 shadow-sm">
                <svg className="w-4 h-4 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                ATS Compatible
              </div>
              <div className="flex items-center bg-white/70 backdrop-blur-sm px-4 py-2 rounded-full border border-white/40 shadow-sm">
                <svg className="w-4 h-4 mr-2 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Professional Insights
              </div>
            </div>
          </div>
        </header>
        
        {/* Main Content */}
        <main className="flex-1 flex items-center justify-center px-6">
          <div className="w-full max-w-2xl">
            <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8 md:p-12">
              <form className="space-y-8" onSubmit={handleAnalyze}>
                {/* File Upload Section */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-slate-800">Upload Your Resume</h3>
                      <p className="text-sm text-slate-500">PDF, DOC, or DOCX format accepted</p>
                    </div>
                  </div>
                  
                  <div className="relative">
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileChange}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                      required
                    />
                    <div className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
                      file 
                        ? 'border-green-300 bg-green-50' 
                        : 'border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50'
                    }`}>
                      {file ? (
                        <div className="space-y-2">
                          <svg className="w-8 h-8 text-green-500 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          <p className="text-green-700 font-medium">{file.name}</p>
                          <p className="text-green-600 text-sm">Ready to analyze</p>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          <svg className="w-8 h-8 text-slate-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                          </svg>
                          <p className="text-slate-600 font-medium">Click to upload or drag and drop</p>
                          <p className="text-slate-500 text-sm">Maximum file size: 10MB</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Job Title Section */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2V6" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-slate-800">Target Job Title</h3>
                      <p className="text-sm text-slate-500">Optional - helps tailor the analysis</p>
                    </div>
                  </div>
                  
                  <input
                    type="text"
                    value={jobTitle}
                    onChange={e => setJobTitle(e.target.value)}
                    className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white/90 backdrop-blur-sm"
                    placeholder="e.g. Senior Software Engineer, Data Scientist, Product Manager"
                  />
                </div>

                {/* Job Description Section */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-slate-800">Job Description</h3>
                      <p className="text-sm text-slate-500">Optional - for more targeted insights</p>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <textarea
                      value={jobDesc}
                      onChange={e => setJobDesc(e.target.value)}
                      className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white/90 backdrop-blur-sm resize-none"
                      rows={4}
                      placeholder="Paste the job description here for more accurate analysis..."
                    />
                    
                    <div className="relative">
                      <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-slate-200"></div>
                      </div>
                      <div className="relative flex justify-center text-sm">
                        <span className="px-3 bg-white text-slate-500">or</span>
                      </div>
                    </div>
                    
                    <input
                      type="url"
                      value={jobDescUrl}
                      onChange={e => setJobDescUrl(e.target.value)}
                      className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white/90 backdrop-blur-sm"
                      placeholder="https://company.com/job-posting"
                    />
                  </div>
                </div>
                
                {/* Analyze Button */}
                <div className="pt-4">
                  <button
                    type="submit"
                    disabled={analyzing}
                    className={`w-full py-4 px-8 rounded-xl font-semibold text-lg transition-all duration-200 transform ${
                      analyzing
                        ? 'bg-slate-400 cursor-not-allowed'
                        : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:scale-[1.02] hover:shadow-xl text-white shadow-lg'
                    }`}
                  >
                    {analyzing ? (
                      <div className="flex items-center justify-center space-x-3">
                        <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span>Analyzing Resume...</span>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center space-x-3">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                        </svg>
                        <span>Analyze My Resume</span>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                      </div>
                    )}
                  </button>
                </div>
              </form>
              
              {/* Error Display */}
              {error && (
                <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl">
                  <div className="flex items-center space-x-2">
                    <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span className="text-red-700 font-medium">{error}</span>
                  </div>
                </div>
              )}
            </div>
            
            {/* Results Display */}
            {results && (
              <div className="mt-8 space-y-6">
                {/* Summary Card */}
                <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg">
                      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-800">Analysis Complete</h3>
                      <p className="text-sm text-slate-500">Resume: {results.filename}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="text-center p-4 bg-blue-50 rounded-xl">
                      <div className="text-2xl font-bold text-blue-600">{results.parsing.totalWords}</div>
                      <div className="text-sm text-slate-600">Words</div>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-xl">
                      <div className="text-2xl font-bold text-purple-600">{results.parsing.sectionsDetected}</div>
                      <div className="text-sm text-slate-600">Sections</div>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-xl">
                      <div className={`text-2xl font-bold ${
                        results.parsing.structureQuality === 'excellent' ? 'text-green-600' :
                        results.parsing.structureQuality === 'good' ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {results.parsing.structureQuality}
                      </div>
                      <div className="text-sm text-slate-600">Quality</div>
                    </div>
                    <div className="text-center p-4 bg-orange-50 rounded-xl">
                      <div className="text-2xl font-bold text-orange-600">{Math.round(results.parsing.totalCharacters / 1000)}K</div>
                      <div className="text-sm text-slate-600">Characters</div>
                    </div>
                  </div>
                  
                  {/* Section Checklist */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className={`flex items-center space-x-2 ${results.parsing.hasContact ? 'text-green-600' : 'text-red-500'}`}>
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d={results.parsing.hasContact ? "M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" : "M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"} clipRule="evenodd" />
                      </svg>
                      <span className="text-sm font-medium">Contact Info</span>
                    </div>
                    <div className={`flex items-center space-x-2 ${results.parsing.hasExperience ? 'text-green-600' : 'text-red-500'}`}>
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d={results.parsing.hasExperience ? "M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" : "M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"} clipRule="evenodd" />
                      </svg>
                      <span className="text-sm font-medium">Experience</span>
                    </div>
                    <div className={`flex items-center space-x-2 ${results.parsing.hasEducation ? 'text-green-600' : 'text-red-500'}`}>
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d={results.parsing.hasEducation ? "M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" : "M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"} clipRule="evenodd" />
                      </svg>
                      <span className="text-sm font-medium">Education</span>
                    </div>
                    <div className={`flex items-center space-x-2 ${results.parsing.hasSkills ? 'text-green-600' : 'text-red-500'}`}>
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d={results.parsing.hasSkills ? "M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" : "M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"} clipRule="evenodd" />
                      </svg>
                      <span className="text-sm font-medium">Skills</span>
                    </div>
                  </div>
                </div>
                
                {/* Contact Information */}
                {Object.keys(results.contactInfo).length > 0 && (
                  <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8">
                    <h3 className="text-lg font-bold text-slate-800 mb-4">Contact Information Detected</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {results.contactInfo.email && (
                        <div className="flex items-center space-x-3">
                          <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                            <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                          </svg>
                          <span className="text-slate-700">{results.contactInfo.email}</span>
                        </div>
                      )}
                      {results.contactInfo.phone && (
                        <div className="flex items-center space-x-3">
                          <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
                          </svg>
                          <span className="text-slate-700">{results.contactInfo.phone}</span>
                        </div>
                      )}
                      {results.contactInfo.linkedin && (
                        <div className="flex items-center space-x-3">
                          <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z" clipRule="evenodd" />
                          </svg>
                          <span className="text-slate-700">{results.contactInfo.linkedin}</span>
                        </div>
                      )}
                      {results.contactInfo.github && (
                        <div className="flex items-center space-x-3">
                          <svg className="w-5 h-5 text-gray-800" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
                          </svg>
                          <span className="text-slate-700">{results.contactInfo.github}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {/* Sections Detected */}
                {results.sections.length > 0 && (
                  <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8">
                    <h3 className="text-lg font-bold text-slate-800 mb-4">Sections Detected</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {results.sections.map((section, index) => (
                        <div key={index} className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                          <div>
                            <div className="font-medium text-slate-800 capitalize">{section.type}</div>
                            <div className="text-sm text-slate-500">{section.wordCount} words</div>
                          </div>
                          <div className="text-right">
                            <div className={`text-sm font-medium ${
                              section.confidence > 0.8 ? 'text-green-600' :
                              section.confidence > 0.6 ? 'text-yellow-600' : 'text-red-500'
                            }`}>
                              {Math.round(section.confidence * 100)}% confident
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Recommendations */}
                {results.parsing.recommendations.length > 0 && (
                  <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 p-8">
                    <h3 className="text-lg font-bold text-slate-800 mb-4">Recommendations</h3>
                    <div className="space-y-3">
                      {results.parsing.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-xl">
                          <svg className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                          <span className="text-sm text-slate-700">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </main>

        {/* Footer */}
        <footer className="py-8 mt-auto">
          <div className="max-w-4xl mx-auto px-6">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/30">
              <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
                <div className="flex items-center space-x-6">
                  <a href="#" className="text-slate-600 hover:text-blue-600 transition-colors duration-200 font-medium text-sm">
                    Privacy Policy
                  </a>
                  <span className="text-slate-300">•</span>
                  <a href="#" className="text-slate-600 hover:text-blue-600 transition-colors duration-200 font-medium text-sm">
                    Terms of Service
                  </a>
                  <span className="text-slate-300">•</span>
                  <a href="#" className="text-slate-600 hover:text-blue-600 transition-colors duration-200 font-medium text-sm">
                    Contact
                  </a>
                </div>
                <p className="text-sm text-slate-500">
                  © {new Date().getFullYear()} Resume Analyzer. All rights reserved.
                </p>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
