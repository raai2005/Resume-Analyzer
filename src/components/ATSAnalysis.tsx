import React from 'react';

interface ATSAnalysisProps {
  data: any;
}

export function ATSAnalysis({ data }: ATSAnalysisProps) {
  const ats = data.ats_compatibility || {};
  const atsDetailed = data.ats_detailed_analysis || {};

  // Warning badge component
  const WarningBadge = ({ level, text }: { level: 'critical' | 'high' | 'medium' | 'low'; text: string }) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-200',
      high: 'bg-orange-100 text-orange-800 border-orange-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      low: 'bg-blue-100 text-blue-800 border-blue-200'
    };

    const icons = {
      critical: '🚨',
      high: '⚠️',
      medium: '⚡',
      low: 'ℹ️'
    };

    return (
      <div className={`inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium border ${colors[level]} mr-2 mb-2`}>
        <span className="mr-2">{icons[level]}</span>
        {text}
      </div>
    );
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    return 'Needs Improvement';
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">ATS Compatibility Analysis</h3>
        <p className="text-gray-600 mb-6">
          How well your resume performs with Applicant Tracking Systems used by employers
        </p>
      </div>

      {/* Overall ATS Score */}
      {ats.available && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-lg font-semibold text-gray-900">Overall ATS Score</h4>
              <p className="text-gray-600">Compatibility level: <span className="font-medium">{ats.compatibility_level}</span></p>
            </div>
            <div className="text-right">
              <div className={`text-4xl font-bold ${getScoreColor(ats.score)} mb-1`}>
                {ats.score}%
              </div>
              <div className={`text-sm font-medium ${getScoreColor(ats.score)}`}>
                {getScoreLabel(ats.score)}
              </div>
            </div>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all duration-1000 ${
                ats.score >= 80 ? 'bg-green-500' : 
                ats.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${ats.score}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Detailed Score Breakdown */}
      {atsDetailed.available && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* File Format Analysis */}
          {atsDetailed.file_format_analysis && (
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-4">File Format</h4>
              <div className={`text-2xl font-bold ${getScoreColor(atsDetailed.file_format_analysis.format_score)} mb-2`}>
                {atsDetailed.file_format_analysis.format_score}%
              </div>
              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                    atsDetailed.file_format_analysis.is_preferred_format ? 'bg-green-500' : 'bg-red-500'
                  }`}></span>
                  {atsDetailed.file_format_analysis.is_preferred_format ? 'Preferred format' : 'Non-preferred format'}
                </div>
                <div className="flex items-center text-sm">
                  <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                    !atsDetailed.file_format_analysis.is_scanned_pdf ? 'bg-green-500' : 'bg-red-500'
                  }`}></span>
                  {!atsDetailed.file_format_analysis.is_scanned_pdf ? 'Text-searchable' : 'Scanned PDF'}
                </div>
              </div>
            </div>
          )}

          {/* Layout Analysis */}
          {atsDetailed.layout_analysis && (
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-4">Layout Structure</h4>
              <div className={`text-2xl font-bold ${getScoreColor(atsDetailed.layout_analysis.layout_score)} mb-2`}>
                {atsDetailed.layout_analysis.layout_score}%
              </div>
              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                    !atsDetailed.layout_analysis.has_multi_column ? 'bg-green-500' : 'bg-red-500'
                  }`}></span>
                  {!atsDetailed.layout_analysis.has_multi_column ? 'Single column' : 'Multi-column'}
                </div>
                <div className="flex items-center text-sm">
                  <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                    !atsDetailed.layout_analysis.excessive_tables ? 'bg-green-500' : 'bg-red-500'
                  }`}></span>
                  {!atsDetailed.layout_analysis.excessive_tables ? 'Minimal tables' : 'Excessive tables'}
                </div>
                <div className="flex items-center text-sm">
                  <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                    !atsDetailed.layout_analysis.excessive_images ? 'bg-green-500' : 'bg-red-500'
                  }`}></span>
                  {!atsDetailed.layout_analysis.excessive_images ? 'Minimal images' : 'Excessive images'}
                </div>
              </div>
            </div>
          )}

          {/* Content Analysis */}
          {atsDetailed.content_analysis && (
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-4">Content Quality</h4>
              <div className={`text-2xl font-bold ${getScoreColor(atsDetailed.content_analysis.content_score)} mb-2`}>
                {atsDetailed.content_analysis.content_score}%
              </div>
              <div className="space-y-2">
                {atsDetailed.content_analysis.has_required_sections && 
                  Object.entries(atsDetailed.content_analysis.has_required_sections).map(([section, hasSection]: [string, any]) => (
                    <div key={section} className="flex items-center text-sm">
                      <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                        hasSection ? 'bg-green-500' : 'bg-red-500'
                      }`}></span>
                      {section.charAt(0).toUpperCase() + section.slice(1)} section {hasSection ? 'present' : 'missing'}
                    </div>
                  ))
                }
              </div>
            </div>
          )}
        </div>
      )}

      {/* Priority Issues */}
      {ats.priority_issues && ats.priority_issues.length > 0 && (
        <div className="bg-red-50 rounded-xl p-6 border border-red-100">
          <h4 className="font-semibold text-red-900 mb-4">Priority Issues</h4>
          <div className="space-y-2">
            {ats.priority_issues.map((issue: string, index: number) => (
              <div key={index} className="flex items-start">
                <span className="text-red-500 mr-2 mt-1">•</span>
                <span className="text-red-700">{issue}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ATS Recommendations by Priority */}
      {ats.recommendations && (
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-900">ATS Optimization Recommendations</h4>
          
          {/* Critical Issues */}
          {ats.recommendations.critical && ats.recommendations.critical.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h5 className="font-medium text-red-700 mb-3">Critical Issues</h5>
              <div className="space-y-2">
                {ats.recommendations.critical.map((rec: string, index: number) => (
                  <WarningBadge key={index} level="critical" text={rec} />
                ))}
              </div>
            </div>
          )}

          {/* High Priority */}
          {ats.recommendations.high_priority && ats.recommendations.high_priority.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h5 className="font-medium text-orange-700 mb-3">High Priority</h5>
              <div className="space-y-2">
                {ats.recommendations.high_priority.map((rec: string, index: number) => (
                  <WarningBadge key={index} level="high" text={rec} />
                ))}
              </div>
            </div>
          )}

          {/* Medium Priority */}
          {ats.recommendations.medium_priority && ats.recommendations.medium_priority.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h5 className="font-medium text-yellow-700 mb-3">Medium Priority</h5>
              <div className="space-y-2">
                {ats.recommendations.medium_priority.map((rec: string, index: number) => (
                  <WarningBadge key={index} level="medium" text={rec} />
                ))}
              </div>
            </div>
          )}

          {/* Low Priority */}
          {ats.recommendations.low_priority && ats.recommendations.low_priority.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-gray-200">
              <h5 className="font-medium text-blue-700 mb-3">Low Priority</h5>
              <div className="space-y-2">
                {ats.recommendations.low_priority.map((rec: string, index: number) => (
                  <WarningBadge key={index} level="low" text={rec} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Best Practices Guide */}
      <div className="bg-green-50 rounded-xl p-6 border border-green-100">
        <h4 className="font-semibold text-green-900 mb-4">ATS Best Practices</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h5 className="font-medium text-green-800 mb-2">✅ Do:</h5>
            <ul className="space-y-1 text-sm text-green-700">
              <li>• Use standard fonts (Arial, Calibri, Times New Roman)</li>
              <li>• Include keywords from job descriptions</li>
              <li>• Use simple, single-column layout</li>
              <li>• Save as .docx or .pdf format</li>
              <li>• Include standard section headers</li>
            </ul>
          </div>
          <div>
            <h5 className="font-medium text-green-800 mb-2">❌ Avoid:</h5>
            <ul className="space-y-1 text-sm text-green-700">
              <li>• Complex tables and text boxes</li>
              <li>• Images and graphics</li>
              <li>• Headers and footers</li>
              <li>• Creative fonts and formatting</li>
              <li>• Multiple columns</li>
            </ul>
          </div>
        </div>
      </div>

      {/* ATS Scan Simulation */}
      <div className="bg-gray-50 rounded-xl p-6 border border-gray-100">
        <h4 className="font-semibold text-gray-900 mb-4">How ATS Systems See Your Resume</h4>
        <div className="bg-white rounded-lg p-4 border border-gray-200 font-mono text-sm text-gray-700">
          <div className="mb-2 font-semibold">ATS Parsing Preview:</div>
          <div className="space-y-1">
            <div>Contact: {data.contact_info?.email ? '✓ Found' : '✗ Missing'}</div>
            <div>Experience: {data.experience_summary?.total_positions > 0 ? '✓ Found' : '✗ Missing'}</div>
            <div>Education: {data.education?.length > 0 ? '✓ Found' : '✗ Missing'}</div>
            <div>Skills: {data.skills?.total_count > 0 ? `✓ ${data.skills.total_count} found` : '✗ Missing'}</div>
            <div>Keywords: {data.keywords?.total_unique_keywords || 0} detected</div>
          </div>
        </div>
      </div>
    </div>
  );
}
