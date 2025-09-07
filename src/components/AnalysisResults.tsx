"use client";
import { useState } from "react";
import { 
  ScoreCard,
  SkillsAnalysis,
  ATSAnalysis,
  Recommendations,
  DetailedInsights
} from "./index";

// Enhanced interfaces for comprehensive analysis
export interface AnalysisResponse {
  status: string;
  status_code: number;
  message: string;
  data: {
    status: string;
    timestamp: string;
    contact_info: {
      name: string;
      email: string;
      email_valid: boolean;
      phone: string;
      phone_provided: boolean;
      location: string;
      links: Array<{
        type: string;
        url: string;
        label: string;
      }>;
      completeness_score: number;
    };
    education: any[];
    experience: any[];
    skills: {
      all_skills: string[];
      categorized: {
        technical: string[];
        programming_languages: string[];
        frameworks: string[];
        tools: string[];
        soft_skills: string[];
        languages: string[];
      };
      total_count: number;
      matched: string[];
      missing: string[];
      bonus: string[];
      match_percentage: number;
      coverage_analysis: {
        overall_coverage: number;
        gap_level: string;
        critical_missing: string[];
        nice_to_have: string[];
      };
    };
    projects: any[];
    certifications: any[];
    role_inference: string;
    quality_scores: {
      available: boolean;
      error: string | null;
    };
    ats_compatibility: {
      available: boolean;
      score: number;
      compatibility_level: string;
      file_format_score: number;
      layout_score: number;
      content_score: number;
      priority_issues: string[];
      recommendations: {
        critical: string[];
        high_priority: string[];
        medium_priority: string[];
        low_priority: string[];
      };
    };
    experience_summary: {
      total_years: number;
      career_level: string;
      total_positions: number;
      industries: string[];
      company_sizes: string[];
      most_recent_role: string;
      employment_gaps: any[];
    };
    recommendations: {
      total_count: number;
      by_priority: {
        critical: string[];
        high_priority: string[];
        medium_priority: string[];
        ats_improvements: {
          critical: string[];
          high_priority: string[];
          medium_priority: string[];
          low_priority: string[];
        };
        general: string[];
      };
      top_3: string[];
    };
    match_analysis: {
      available: boolean;
      overall_match: number;
      experience_level_match: string;
      skills_coverage: number;
      gap_analysis: {
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
      };
    };
    readability_metrics: {
      flesch_reading_ease: number;
      flesch_kincaid_grade: number;
      clarity_score: number;
      conciseness_score: number;
      professional_tone: string;
      reading_time_estimate: string;
    };
    industry_analysis: {
      industry_identification: string[];
      industry_keywords: string[];
      industry_standards_alignment: {
        alignment_score: number;
      };
    };
    competitive_analysis: {
      market_positioning: {
        market_tier: string;
        positioning_strength: number;
      };
      competitive_strengths: string[];
      differentiation_factors: string[];
      market_demand_alignment: {
        demand_alignment: number;
      };
      unique_value_proposition: string[];
    };
    [key: string]: any; // For additional fields
  };
}

interface AnalysisResultsProps {
  results: AnalysisResponse;
  onReset: () => void;
}

export function AnalysisResults({ results, onReset }: AnalysisResultsProps) {
  const [activeTab, setActiveTab] = useState("overview");
  const data = results.data;

  // Calculate overall score from available metrics
  const calculateOverallScore = () => {
    let totalScore = 0;
    let scoreCount = 0;

    if (data.ats_compatibility?.available && data.ats_compatibility.score) {
      totalScore += data.ats_compatibility.score;
      scoreCount++;
    }

    if (data.match_analysis?.available && data.match_analysis.overall_match) {
      totalScore += data.match_analysis.overall_match;
      scoreCount++;
    }

    if (data.skills?.match_percentage) {
      totalScore += data.skills.match_percentage;
      scoreCount++;
    }

    if (data.contact_info?.completeness_score) {
      totalScore += data.contact_info.completeness_score;
      scoreCount++;
    }

    return scoreCount > 0 ? Math.round(totalScore / scoreCount) : 0;
  };

  const overallScore = calculateOverallScore();

  const tabs = [
    { id: "overview", label: "Overview", icon: "📊" },
    { id: "skills", label: "Skills", icon: "🎯" },
    { id: "ats", label: "ATS Analysis", icon: "🤖" },
    { id: "recommendations", label: "Recommendations", icon: "💡" },
    { id: "insights", label: "Detailed Insights", icon: "🔍" },
  ];

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      {/* Header with Overall Score */}
      <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Analysis Complete
            </h2>
            <p className="text-gray-600">
              Role Inference: <span className="font-semibold text-blue-600">{data.role_inference}</span>
            </p>
            {data.contact_info?.name && (
              <p className="text-gray-600">
                Candidate: <span className="font-semibold">{data.contact_info.name}</span>
              </p>
            )}
          </div>
          <button
            onClick={onReset}
            className="px-6 py-3 bg-gray-100 hover:bg-gray-200 rounded-xl font-medium text-gray-700 transition-colors"
          >
            Analyze Another
          </button>
        </div>

        {/* Overall Score Display */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Overall Score</h3>
              <p className="text-gray-600">Comprehensive analysis across all categories</p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-blue-600 mb-1">{overallScore}%</div>
              <div className={`text-sm font-medium ${
                overallScore >= 80 ? 'text-green-600' : 
                overallScore >= 60 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {overallScore >= 80 ? 'Excellent' : 
                 overallScore >= 60 ? 'Good' : 'Needs Improvement'}
              </div>
            </div>
          </div>
          
          {/* Score breakdown bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className={`h-3 rounded-full transition-all duration-1000 ${
                  overallScore >= 80 ? 'bg-green-500' : 
                  overallScore >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${overallScore}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {data.skills?.total_count || 0}
            </div>
            <div className="text-sm text-gray-600">Skills Found</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {data.skills?.matched?.length || 0}
            </div>
            <div className="text-sm text-gray-600">Skills Matched</div>
          </div>
          <div className="bg-yellow-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {data.experience_summary?.total_years || 0}
            </div>
            <div className="text-sm text-gray-600">Years Experience</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {data.ats_compatibility?.score || 0}%
            </div>
            <div className="text-sm text-gray-600">ATS Score</div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === "overview" && <ScoreCard data={data} />}
          {activeTab === "skills" && <SkillsAnalysis data={data} />}
          {activeTab === "ats" && <ATSAnalysis data={data} />}
          {activeTab === "recommendations" && <Recommendations data={data} />}
          {activeTab === "insights" && <DetailedInsights data={data} />}
        </div>
      </div>
    </div>
  );
}
