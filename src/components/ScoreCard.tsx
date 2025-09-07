import React from 'react';

interface ScoreCardProps {
  data: any;
}

export function ScoreCard({ data }: ScoreCardProps) {
  // Extract scores from various analysis components
  const scores = [
    {
      name: "ATS Compatibility",
      score: data.ats_compatibility?.score || 0,
      available: data.ats_compatibility?.available,
      color: "blue",
      description: "How well your resume works with Applicant Tracking Systems"
    },
    {
      name: "Skills Match",
      score: data.skills?.match_percentage || 0,
      available: true,
      color: "green",
      description: "Percentage of required skills found in your resume"
    },
    {
      name: "Overall Match",
      score: data.match_analysis?.overall_match || 0,
      available: data.match_analysis?.available,
      color: "purple",
      description: "Overall compatibility with target role"
    },
    {
      name: "Contact Completeness",
      score: data.contact_info?.completeness_score || 0,
      available: true,
      color: "indigo",
      description: "Completeness of your contact information"
    }
  ];

  const getScoreColor = (score: number, baseColor: string) => {
    if (score >= 80) return `text-green-600 bg-green-50`;
    if (score >= 60) return `text-yellow-600 bg-yellow-50`;
    return `text-red-600 bg-red-50`;
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Score Breakdown</h3>
        <p className="text-gray-600 mb-6">
          Detailed analysis of your resume across key performance indicators
        </p>
      </div>

      {/* Score Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {scores.map((item, index) => (
          <div key={index} className="bg-gray-50 rounded-xl p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-gray-900">{item.name}</h4>
              {item.available ? (
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(item.score, item.color)}`}>
                  {item.score}%
                </span>
              ) : (
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-500">
                  N/A
                </span>
              )}
            </div>
            
            <p className="text-sm text-gray-600 mb-4">{item.description}</p>
            
            {item.available && (
              <div className="space-y-2">
                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-1000 ${getProgressColor(item.score)}`}
                    style={{ width: `${item.score}%` }}
                  ></div>
                </div>
                
                {/* Score Interpretation */}
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Poor</span>
                  <span>Average</span>
                  <span>Excellent</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Additional Metrics */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6">
        <h4 className="font-semibold text-gray-900 mb-4">Additional Metrics</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {data.readability_metrics?.clarity_score || 0}%
            </div>
            <div className="text-sm text-gray-600">Clarity Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {data.industry_analysis?.industry_standards_alignment?.alignment_score || 0}%
            </div>
            <div className="text-sm text-gray-600">Industry Alignment</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {data.competitive_analysis?.market_positioning?.positioning_strength || 0}%
            </div>
            <div className="text-sm text-gray-600">Market Position</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-indigo-600">
              {data.competitive_analysis?.market_demand_alignment?.demand_alignment || 0}%
            </div>
            <div className="text-sm text-gray-600">Market Demand</div>
          </div>
        </div>
      </div>

      {/* Reading Metrics */}
      {data.readability_metrics && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Readability Analysis</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-lg font-semibold text-gray-900">
                {data.readability_metrics.flesch_reading_ease?.toFixed(1) || 'N/A'}
              </div>
              <div className="text-sm text-gray-600">Flesch Reading Ease</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-lg font-semibold text-gray-900">
                {data.readability_metrics.flesch_kincaid_grade?.toFixed(1) || 'N/A'}
              </div>
              <div className="text-sm text-gray-600">Grade Level</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-lg font-semibold text-gray-900">
                {data.readability_metrics.reading_time_estimate || 'N/A'}
              </div>
              <div className="text-sm text-gray-600">Reading Time</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
