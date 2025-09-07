import React from 'react';

interface SkillsAnalysisProps {
  data: any;
}

export function SkillsAnalysis({ data }: SkillsAnalysisProps) {
  const skills = data.skills || {};
  const matchAnalysis = data.match_analysis || {};

  // Skill chip component
  const SkillChip = ({ skill, type }: { skill: string; type: 'matched' | 'missing' | 'bonus' }) => {
    const colors = {
      matched: 'bg-green-100 text-green-800 border-green-200',
      missing: 'bg-red-100 text-red-800 border-red-200',
      bonus: 'bg-blue-100 text-blue-800 border-blue-200'
    };

    const icons = {
      matched: '✓',
      missing: '×',
      bonus: '+'
    };

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${colors[type]} mr-2 mb-2`}>
        <span className="mr-1">{icons[type]}</span>
        {skill}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Skills Analysis</h3>
        <p className="text-gray-600 mb-6">
          Comprehensive breakdown of your skills and their alignment with target requirements
        </p>
      </div>

      {/* Skills Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-green-50 rounded-xl p-6 border border-green-100">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-green-900">Matched Skills</h4>
            <span className="text-2xl font-bold text-green-600">{skills.matched?.length || 0}</span>
          </div>
          <div className="text-sm text-green-700">
            Skills that align with requirements
          </div>
          <div className="mt-2">
            <div className="w-full bg-green-200 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full transition-all duration-1000"
                style={{ width: `${skills.match_percentage || 0}%` }}
              ></div>
            </div>
            <div className="text-xs text-green-600 mt-1">{skills.match_percentage?.toFixed(1) || 0}% match</div>
          </div>
        </div>

        <div className="bg-red-50 rounded-xl p-6 border border-red-100">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-red-900">Missing Skills</h4>
            <span className="text-2xl font-bold text-red-600">{skills.missing?.length || 0}</span>
          </div>
          <div className="text-sm text-red-700">
            Skills to consider adding
          </div>
          {skills.coverage_analysis?.gap_level && (
            <div className="mt-2">
              <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                skills.coverage_analysis.gap_level === 'excellent' ? 'bg-green-100 text-green-800' :
                skills.coverage_analysis.gap_level === 'good' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {skills.coverage_analysis.gap_level} coverage
              </span>
            </div>
          )}
        </div>

        <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-blue-900">Bonus Skills</h4>
            <span className="text-2xl font-bold text-blue-600">{skills.bonus?.length || 0}</span>
          </div>
          <div className="text-sm text-blue-700">
            Additional valuable skills
          </div>
          <div className="mt-2">
            <span className="inline-block px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
              Competitive advantage
            </span>
          </div>
        </div>
      </div>

      {/* Skills Breakdown */}
      <div className="space-y-6">
        {/* Matched Skills */}
        {skills.matched && skills.matched.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
              <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
              Matched Skills ({skills.matched.length})
            </h4>
            <div className="flex flex-wrap">
              {skills.matched.map((skill: string, index: number) => (
                <SkillChip key={index} skill={skill} type="matched" />
              ))}
            </div>
          </div>
        )}

        {/* Missing Skills */}
        {skills.missing && skills.missing.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
              <span className="w-3 h-3 bg-red-500 rounded-full mr-2"></span>
              Missing Skills ({skills.missing.length})
            </h4>
            <div className="flex flex-wrap">
              {skills.missing.map((skill: string, index: number) => (
                <SkillChip key={index} skill={skill} type="missing" />
              ))}
            </div>
            {matchAnalysis.gap_analysis?.priority_skills_to_add && (
              <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="font-medium text-yellow-800 mb-2">Priority Skills to Add:</div>
                <div className="flex flex-wrap">
                  {matchAnalysis.gap_analysis.priority_skills_to_add.map((skill: string, index: number) => (
                    <span key={index} className="inline-block px-2 py-1 bg-yellow-200 text-yellow-800 rounded text-sm mr-2 mb-1">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Bonus Skills */}
        {skills.bonus && skills.bonus.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
              <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
              Bonus Skills ({skills.bonus.length})
            </h4>
            <div className="flex flex-wrap">
              {skills.bonus.map((skill: string, index: number) => (
                <SkillChip key={index} skill={skill} type="bonus" />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Categorized Skills */}
      {skills.categorized && (
        <div className="bg-gray-50 rounded-xl p-6 border border-gray-100">
          <h4 className="font-semibold text-gray-900 mb-4">Skills by Category</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(skills.categorized).map(([category, skillList]: [string, any]) => (
              skillList && skillList.length > 0 && (
                <div key={category} className="bg-white rounded-lg p-4 border border-gray-200">
                  <h5 className="font-medium text-gray-900 mb-2 capitalize">
                    {category.replace('_', ' ')} ({skillList.length})
                  </h5>
                  <div className="space-y-1">
                    {skillList.map((skill: string, index: number) => (
                      <div key={index} className="text-sm text-gray-700 bg-gray-100 rounded px-2 py-1">
                        {skill}
                      </div>
                    ))}
                  </div>
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* Gap Analysis Recommendations */}
      {matchAnalysis.gap_analysis?.recommendations && (
        <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
          <h4 className="font-semibold text-blue-900 mb-4">Skill Development Recommendations</h4>
          <div className="space-y-4">
            {matchAnalysis.gap_analysis.recommendations.immediate_priority?.length > 0 && (
              <div>
                <h5 className="font-medium text-red-700 mb-2">Immediate Priority:</h5>
                <ul className="space-y-1">
                  {matchAnalysis.gap_analysis.recommendations.immediate_priority.map((rec: string, index: number) => (
                    <li key={index} className="text-sm text-red-600 flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {matchAnalysis.gap_analysis.recommendations.medium_priority?.length > 0 && (
              <div>
                <h5 className="font-medium text-yellow-700 mb-2">Medium Priority:</h5>
                <ul className="space-y-1">
                  {matchAnalysis.gap_analysis.recommendations.medium_priority.map((rec: string, index: number) => (
                    <li key={index} className="text-sm text-yellow-600 flex items-start">
                      <span className="text-yellow-500 mr-2">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {matchAnalysis.gap_analysis.recommendations.leverage_existing?.length > 0 && (
              <div>
                <h5 className="font-medium text-green-700 mb-2">Leverage Existing:</h5>
                <ul className="space-y-1">
                  {matchAnalysis.gap_analysis.recommendations.leverage_existing.map((rec: string, index: number) => (
                    <li key={index} className="text-sm text-green-600 flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Coverage Breakdown */}
      {matchAnalysis.gap_analysis?.coverage_breakdown && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Coverage Analysis</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {matchAnalysis.gap_analysis.coverage_breakdown.required_coverage?.toFixed(1) || 0}%
              </div>
              <div className="text-sm text-gray-600">Required Coverage</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {matchAnalysis.gap_analysis.coverage_breakdown.preferred_coverage?.toFixed(1) || 0}%
              </div>
              <div className="text-sm text-gray-600">Preferred Coverage</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {matchAnalysis.gap_analysis.coverage_breakdown.total_target_skills || 0}
              </div>
              <div className="text-sm text-gray-600">Target Skills</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-indigo-600">
                {matchAnalysis.gap_analysis.coverage_breakdown.total_resume_skills || 0}
              </div>
              <div className="text-sm text-gray-600">Resume Skills</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
