import React from 'react';

interface RecommendationsProps {
  data: any;
}

export function Recommendations({ data }: RecommendationsProps) {
  const recommendations = data.recommendations || {};
  const matchAnalysis = data.match_analysis || {};
  const optimizationSuggestions = data.optimization_suggestions || {};

  // Suggestion card component
  const SuggestionCard = ({ 
    title, 
    suggestions, 
    priority, 
    icon 
  }: { 
    title: string; 
    suggestions: string[]; 
    priority: 'critical' | 'high' | 'medium' | 'low';
    icon: string;
  }) => {
    const colors = {
      critical: 'border-red-200 bg-red-50',
      high: 'border-orange-200 bg-orange-50',
      medium: 'border-yellow-200 bg-yellow-50',
      low: 'border-blue-200 bg-blue-50'
    };

    const textColors = {
      critical: 'text-red-800',
      high: 'text-orange-800',
      medium: 'text-yellow-800',
      low: 'text-blue-800'
    };

    const headerColors = {
      critical: 'text-red-900',
      high: 'text-orange-900',
      medium: 'text-yellow-900',
      low: 'text-blue-900'
    };

    if (!suggestions || suggestions.length === 0) return null;

    return (
      <div className={`rounded-xl p-6 border ${colors[priority]}`}>
        <h4 className={`font-semibold mb-4 flex items-center ${headerColors[priority]}`}>
          <span className="mr-2 text-lg">{icon}</span>
          {title} ({suggestions.length})
        </h4>
        <div className="space-y-3">
          {suggestions.map((suggestion: string, index: number) => (
            <div key={index} className={`flex items-start ${textColors[priority]}`}>
              <span className="mr-2 mt-1">•</span>
              <span className="text-sm">{suggestion}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Concrete Suggestions</h3>
        <p className="text-gray-600 mb-6">
          Actionable recommendations to improve your resume's performance and appeal
        </p>
      </div>

      {/* Summary Stats */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-6 border border-purple-100">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {recommendations.total_count || 0}
            </div>
            <div className="text-sm text-gray-600">Total Recommendations</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {(recommendations.by_priority?.critical?.length || 0) + 
               (recommendations.by_priority?.high_priority?.length || 0)}
            </div>
            <div className="text-sm text-gray-600">High Priority</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {recommendations.by_priority?.medium_priority?.length || 0}
            </div>
            <div className="text-sm text-gray-600">Medium Priority</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {recommendations.by_priority?.general?.length || 0}
            </div>
            <div className="text-sm text-gray-600">General Improvements</div>
          </div>
        </div>
      </div>

      {/* Top 3 Priority Recommendations */}
      {recommendations.top_3 && recommendations.top_3.length > 0 && (
        <div className="bg-yellow-50 rounded-xl p-6 border border-yellow-200">
          <h4 className="font-semibold text-yellow-900 mb-4 flex items-center">
            <span className="mr-2">⭐</span>
            Top Priority Actions
          </h4>
          <div className="space-y-3">
            {recommendations.top_3.map((rec: string, index: number) => (
              <div key={index} className="flex items-center bg-white rounded-lg p-3 border border-yellow-200">
                <span className="flex items-center justify-center w-6 h-6 bg-yellow-500 text-white rounded-full text-sm font-bold mr-3">
                  {index + 1}
                </span>
                <span className="text-yellow-800 font-medium">{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations by Category */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Critical Issues */}
        <SuggestionCard 
          title="Critical Issues"
          suggestions={recommendations.by_priority?.critical || []}
          priority="critical"
          icon="🚨"
        />

        {/* High Priority */}
        <SuggestionCard 
          title="High Priority"
          suggestions={recommendations.by_priority?.high_priority || []}
          priority="high"
          icon="⚠️"
        />

        {/* Medium Priority */}
        <SuggestionCard 
          title="Medium Priority"
          suggestions={recommendations.by_priority?.medium_priority || []}
          priority="medium"
          icon="⚡"
        />

        {/* General Improvements */}
        <SuggestionCard 
          title="General Improvements"
          suggestions={recommendations.by_priority?.general || []}
          priority="low"
          icon="💡"
        />
      </div>

      {/* ATS-Specific Recommendations */}
      {recommendations.by_priority?.ats_improvements && (
        <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
          <h4 className="font-semibold text-blue-900 mb-4 flex items-center">
            <span className="mr-2">🤖</span>
            ATS Optimization Recommendations
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(recommendations.by_priority.ats_improvements).map(([priority, items]: [string, any]) => (
              items && items.length > 0 && (
                <div key={priority} className="bg-white rounded-lg p-4 border border-blue-200">
                  <h5 className="font-medium text-blue-800 mb-2 capitalize">
                    {priority.replace('_', ' ')} ({items.length})
                  </h5>
                  <div className="space-y-1">
                    {items.map((item: string, index: number) => (
                      <div key={index} className="text-sm text-blue-700 flex items-start">
                        <span className="mr-2">•</span>
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* Immediate Actions from Gap Analysis */}
      {matchAnalysis.recommendations?.immediate_actions && (
        <div className="bg-red-50 rounded-xl p-6 border border-red-100">
          <h4 className="font-semibold text-red-900 mb-4 flex items-center">
            <span className="mr-2">🎯</span>
            Immediate Actions Required
          </h4>
          <div className="space-y-3">
            {matchAnalysis.recommendations.immediate_actions.map((action: string, index: number) => (
              <div key={index} className="bg-white rounded-lg p-3 border border-red-200">
                <div className="flex items-start">
                  <span className="text-red-500 mr-2 mt-1">•</span>
                  <span className="text-red-700 font-medium">{action}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Optimization Suggestions by Category */}
      {optimizationSuggestions && Object.keys(optimizationSuggestions).length > 0 && (
        <div className="bg-gray-50 rounded-xl p-6 border border-gray-100">
          <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
            <span className="mr-2">🔧</span>
            Detailed Optimization Suggestions
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(optimizationSuggestions).map(([category, suggestions]: [string, any]) => (
              suggestions && suggestions.length > 0 && (
                <div key={category} className="bg-white rounded-lg p-4 border border-gray-200">
                  <h5 className="font-medium text-gray-900 mb-3 capitalize">
                    {category.replace('_', ' ')}
                  </h5>
                  <div className="space-y-2">
                    {suggestions.map((suggestion: string, index: number) => (
                      <div key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="text-gray-400 mr-2">•</span>
                        {suggestion}
                      </div>
                    ))}
                  </div>
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* Action Plan Template */}
      <div className="bg-green-50 rounded-xl p-6 border border-green-100">
        <h4 className="font-semibold text-green-900 mb-4 flex items-center">
          <span className="mr-2">📋</span>
          Recommended Action Plan
        </h4>
        <div className="space-y-4">
          <div className="bg-white rounded-lg p-4 border border-green-200">
            <h5 className="font-medium text-green-800 mb-2">Week 1: Critical Issues</h5>
            <ul className="text-sm text-green-700 space-y-1">
              <li>• Address critical formatting and ATS compatibility issues</li>
              <li>• Fix missing or incomplete contact information</li>
              <li>• Add missing required sections</li>
            </ul>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-green-200">
            <h5 className="font-medium text-green-800 mb-2">Week 2: Content Enhancement</h5>
            <ul className="text-sm text-green-700 space-y-1">
              <li>• Add quantified achievements and metrics</li>
              <li>• Include relevant keywords from job descriptions</li>
              <li>• Improve bullet point structure and clarity</li>
            </ul>
          </div>
          
          <div className="bg-white rounded-lg p-4 border border-green-200">
            <h5 className="font-medium text-green-800 mb-2">Week 3: Skills & Optimization</h5>
            <ul className="text-sm text-green-700 space-y-1">
              <li>• Add missing skills identified in analysis</li>
              <li>• Optimize for industry-specific keywords</li>
              <li>• Review and refine overall presentation</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Progress Tracking */}
      <div className="bg-indigo-50 rounded-xl p-6 border border-indigo-100">
        <h4 className="font-semibold text-indigo-900 mb-4 flex items-center">
          <span className="mr-2">📈</span>
          Track Your Progress
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 border border-indigo-200 text-center">
            <div className="text-2xl font-bold text-indigo-600 mb-2">Before</div>
            <div className="text-sm text-gray-600">Current analysis shows areas for improvement</div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-indigo-200 text-center">
            <div className="text-2xl font-bold text-indigo-600 mb-2">During</div>
            <div className="text-sm text-gray-600">Implement recommendations systematically</div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-indigo-200 text-center">
            <div className="text-2xl font-bold text-indigo-600 mb-2">After</div>
            <div className="text-sm text-gray-600">Re-analyze to measure improvements</div>
          </div>
        </div>
      </div>
    </div>
  );
}
