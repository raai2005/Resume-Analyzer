import React, { useState } from 'react';

interface DetailedInsightsProps {
  data: any;
}

export function DetailedInsights({ data }: DetailedInsightsProps) {
  const [activeInsightTab, setActiveInsightTab] = useState("content");

  const insightTabs = [
    { id: "content", label: "Content Analysis", icon: "📝" },
    { id: "industry", label: "Industry Insights", icon: "🏢" },
    { id: "competitive", label: "Market Position", icon: "📊" },
    { id: "readability", label: "Readability", icon: "👁️" },
    { id: "career", label: "Career Analysis", icon: "🚀" },
    { id: "technical", label: "Technical Details", icon: "⚙️" },
  ];

  const MetricCard = ({ title, value, description, color = "blue" }: {
    title: string;
    value: string | number;
    description: string;
    color?: string;
  }) => (
    <div className="bg-white rounded-lg p-4 border border-gray-200">
      <div className={`text-2xl font-bold text-${color}-600 mb-1`}>
        {value}
      </div>
      <div className="font-medium text-gray-900 mb-1">{title}</div>
      <div className="text-sm text-gray-600">{description}</div>
    </div>
  );

  const InsightSection = ({ title, children }: { title: string; children: React.ReactNode }) => (
    <div className="bg-gray-50 rounded-xl p-6 border border-gray-100">
      <h4 className="font-semibold text-gray-900 mb-4">{title}</h4>
      {children}
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Detailed Insights</h3>
        <p className="text-gray-600 mb-6">
          Comprehensive analysis and deep insights into your resume's performance
        </p>
      </div>

      {/* Insight Navigation */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex flex-wrap px-4">
            {insightTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveInsightTab(tab.id)}
                className={`py-3 px-4 border-b-2 font-medium text-sm transition-colors ${
                  activeInsightTab === tab.id
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

        <div className="p-6">
          {/* Content Analysis Tab */}
          {activeInsightTab === "content" && (
            <div className="space-y-6">
              {/* Content Metrics */}
              {data.content_analysis && (
                <InsightSection title="Content Quality Metrics">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <MetricCard 
                      title="Word Count"
                      value={data.content_analysis.word_count || 0}
                      description="Total words in resume"
                      color="blue"
                    />
                    <MetricCard 
                      title="Vocabulary Richness"
                      value={`${((data.content_analysis.vocabulary_richness || 0) * 100).toFixed(1)}%`}
                      description="Unique word usage"
                      color="green"
                    />
                    <MetricCard 
                      title="Action Verb Density"
                      value={`${((data.content_analysis.action_verb_density || 0) * 100).toFixed(1)}%`}
                      description="Strong action words"
                      color="purple"
                    />
                    <MetricCard 
                      title="Quantification Rate"
                      value={`${((data.content_analysis.quantification_rate || 0) * 100).toFixed(1)}%`}
                      description="Statements with metrics"
                      color="orange"
                    />
                  </div>
                </InsightSection>
              )}

              {/* Section Analysis */}
              {data.section_analysis && (
                <InsightSection title="Section Structure Analysis">
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <MetricCard 
                        title="Sections Found"
                        value={data.section_analysis.total_sections || 0}
                        description="Resume sections detected"
                      />
                      <MetricCard 
                        title="Section Quality"
                        value={data.section_analysis.section_quality || "N/A"}
                        description="Overall structure rating"
                      />
                      <MetricCard 
                        title="Bullet Points"
                        value={data.section_analysis.bullet_points_total || 0}
                        description="Total bullet points"
                      />
                      <MetricCard 
                        title="Format Consistency"
                        value={data.section_analysis.formatting_consistency || "Unknown"}
                        description="Formatting uniformity"
                      />
                    </div>
                    
                    {data.section_analysis.sections_found && (
                      <div className="mt-4">
                        <h5 className="font-medium text-gray-900 mb-3">Detected Sections:</h5>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {data.section_analysis.sections_found.map((section: any, index: number) => (
                            <div key={index} className="bg-white rounded-lg p-3 border border-gray-200">
                              <div className="flex justify-between items-center mb-2">
                                <span className="font-medium text-gray-900">{section.title}</span>
                                <span className="text-sm text-gray-500">{section.word_count} words</span>
                              </div>
                              <div className="text-sm text-gray-600 mb-2">
                                Confidence: {(section.confidence * 100).toFixed(1)}%
                              </div>
                              {section.keywords_found && section.keywords_found.length > 0 && (
                                <div className="text-xs text-gray-500">
                                  Keywords: {section.keywords_found.join(', ')}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </InsightSection>
              )}

              {/* Formatting Analysis */}
              {data.formatting_analysis && (
                <InsightSection title="Formatting Quality">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <MetricCard 
                      title="Consistency Score"
                      value={`${data.formatting_analysis.formatting_consistency?.consistency_score || 0}%`}
                      description="Format uniformity"
                    />
                    <MetricCard 
                      title="Professional Score"
                      value={`${data.formatting_analysis.professional_appearance?.professional_score || 0}%`}
                      description="Professional appearance"
                    />
                    <MetricCard 
                      title="White Space"
                      value={`${data.formatting_analysis.white_space_usage?.density_score || 0}%`}
                      description="Space optimization"
                    />
                    <MetricCard 
                      title="Visual Hierarchy"
                      value={data.formatting_analysis.visual_hierarchy?.hierarchy_clarity || "N/A"}
                      description="Content organization"
                    />
                  </div>
                </InsightSection>
              )}
            </div>
          )}

          {/* Industry Insights Tab */}
          {activeInsightTab === "industry" && (
            <div className="space-y-6">
              {data.industry_analysis && (
                <InsightSection title="Industry Alignment">
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <MetricCard 
                        title="Industry Alignment"
                        value={`${data.industry_analysis.industry_standards_alignment?.alignment_score || 0}%`}
                        description="Standards compliance"
                      />
                      <MetricCard 
                        title="Trend Alignment"
                        value={`${data.industry_analysis.industry_trends_alignment?.trend_score || 0}%`}
                        description="Current trends match"
                      />
                      <MetricCard 
                        title="Transferability"
                        value={`${data.industry_analysis.cross_industry_transferability?.transferability_score || 0}%`}
                        description="Cross-industry potential"
                      />
                    </div>
                    
                    {data.industry_analysis.industry_identification && (
                      <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <h5 className="font-medium text-gray-900 mb-3">Identified Industries:</h5>
                        <div className="flex flex-wrap gap-2">
                          {data.industry_analysis.industry_identification.map((industry: string, index: number) => (
                            <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                              {industry}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {data.industry_analysis.industry_keywords && (
                      <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <h5 className="font-medium text-gray-900 mb-3">Industry Keywords Found:</h5>
                        <div className="flex flex-wrap gap-2">
                          {data.industry_analysis.industry_keywords.map((keyword: string, index: number) => (
                            <span key={index} className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </InsightSection>
              )}
            </div>
          )}

          {/* Competitive Analysis Tab */}
          {activeInsightTab === "competitive" && (
            <div className="space-y-6">
              {data.competitive_analysis && (
                <InsightSection title="Market Positioning">
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <MetricCard 
                        title="Market Tier"
                        value={data.competitive_analysis.market_positioning?.market_tier || "N/A"}
                        description="Position in market"
                      />
                      <MetricCard 
                        title="Positioning Strength"
                        value={`${data.competitive_analysis.market_positioning?.positioning_strength || 0}%`}
                        description="Competitive strength"
                      />
                      <MetricCard 
                        title="Market Demand"
                        value={`${data.competitive_analysis.market_demand_alignment?.demand_alignment || 0}%`}
                        description="Demand alignment"
                      />
                      <MetricCard 
                        title="Skill Value"
                        value={data.competitive_analysis.skill_market_value?.market_value || "N/A"}
                        description="Skills market value"
                      />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {data.competitive_analysis.competitive_strengths && (
                        <div className="bg-white rounded-lg p-4 border border-gray-200">
                          <h5 className="font-medium text-gray-900 mb-3">Competitive Strengths:</h5>
                          <ul className="space-y-2">
                            {data.competitive_analysis.competitive_strengths.map((strength: string, index: number) => (
                              <li key={index} className="text-sm text-gray-700 flex items-start">
                                <span className="text-green-500 mr-2">✓</span>
                                {strength}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {data.competitive_analysis.differentiation_factors && (
                        <div className="bg-white rounded-lg p-4 border border-gray-200">
                          <h5 className="font-medium text-gray-900 mb-3">Differentiation Factors:</h5>
                          <ul className="space-y-2">
                            {data.competitive_analysis.differentiation_factors.map((factor: string, index: number) => (
                              <li key={index} className="text-sm text-gray-700 flex items-start">
                                <span className="text-blue-500 mr-2">★</span>
                                {factor}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                    
                    {data.competitive_analysis.unique_value_proposition && (
                      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-4 border border-purple-200">
                        <h5 className="font-medium text-purple-900 mb-3">Unique Value Proposition:</h5>
                        <ul className="space-y-2">
                          {data.competitive_analysis.unique_value_proposition.map((prop: string, index: number) => (
                            <li key={index} className="text-sm text-purple-700 flex items-start">
                              <span className="text-purple-500 mr-2">💎</span>
                              {prop}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </InsightSection>
              )}
            </div>
          )}

          {/* Readability Tab */}
          {activeInsightTab === "readability" && (
            <div className="space-y-6">
              {data.readability_metrics && (
                <InsightSection title="Readability Analysis">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <MetricCard 
                      title="Reading Ease"
                      value={data.readability_metrics.flesch_reading_ease?.toFixed(1) || "N/A"}
                      description="Flesch Reading Ease score"
                    />
                    <MetricCard 
                      title="Grade Level"
                      value={data.readability_metrics.flesch_kincaid_grade?.toFixed(1) || "N/A"}
                      description="Required education level"
                    />
                    <MetricCard 
                      title="Clarity Score"
                      value={`${data.readability_metrics.clarity_score || 0}%`}
                      description="Content clarity"
                    />
                    <MetricCard 
                      title="Reading Time"
                      value={data.readability_metrics.reading_time_estimate || "N/A"}
                      description="Estimated reading time"
                    />
                  </div>
                </InsightSection>
              )}
            </div>
          )}

          {/* Career Analysis Tab */}
          {activeInsightTab === "career" && (
            <div className="space-y-6">
              {data.career_progression && (
                <InsightSection title="Career Development Analysis">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <MetricCard 
                      title="Trajectory"
                      value={data.career_progression.progression_trajectory?.trajectory || "N/A"}
                      description="Career direction"
                    />
                    <MetricCard 
                      title="Advancement"
                      value={data.career_progression.role_advancement?.advancement_rate || "N/A"}
                      description="Role progression rate"
                    />
                    <MetricCard 
                      title="Stability"
                      value={`${data.career_progression.career_stability?.stability_score || 0}%`}
                      description="Career stability"
                    />
                    <MetricCard 
                      title="Growth Potential"
                      value={data.career_progression.growth_potential?.growth_potential || "N/A"}
                      description="Future growth outlook"
                    />
                  </div>
                </InsightSection>
              )}

              {data.experience_summary && (
                <InsightSection title="Experience Summary">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <MetricCard 
                      title="Total Experience"
                      value={`${data.experience_summary.total_years || 0} years`}
                      description="Total work experience"
                    />
                    <MetricCard 
                      title="Career Level"
                      value={data.experience_summary.career_level || "N/A"}
                      description="Current career stage"
                    />
                    <MetricCard 
                      title="Positions"
                      value={data.experience_summary.total_positions || 0}
                      description="Total positions held"
                    />
                    <MetricCard 
                      title="Recent Role"
                      value={data.experience_summary.most_recent_role || "N/A"}
                      description="Latest position title"
                    />
                  </div>
                </InsightSection>
              )}
            </div>
          )}

          {/* Technical Details Tab */}
          {activeInsightTab === "technical" && (
            <div className="space-y-6">
              {data.text_extraction_details && (
                <InsightSection title="Document Processing">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <MetricCard 
                      title="Extraction Method"
                      value={data.text_extraction_details.extraction_method || "N/A"}
                      description="Processing method used"
                    />
                    <MetricCard 
                      title="Text Length"
                      value={data.text_extraction_details.text_length || 0}
                      description="Total characters"
                    />
                    <MetricCard 
                      title="Language"
                      value={data.text_extraction_details.language_detected || "N/A"}
                      description="Detected language"
                    />
                    <MetricCard 
                      title="Pages"
                      value={data.text_extraction_details.pages_detected || 0}
                      description="Document pages"
                    />
                  </div>
                </InsightSection>
              )}

              {data.parsing_metadata && (
                <InsightSection title="Processing Statistics">
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <MetricCard 
                        title="Processing Confidence"
                        value={`${data.parsing_metadata.confidence_scores?.overall_parsing_confidence || 0}%`}
                        description="Analysis confidence"
                      />
                      <MetricCard 
                        title="Sections Processed"
                        value={data.parsing_metadata.processing_statistics?.sections_processed || 0}
                        description="Resume sections analyzed"
                      />
                      <MetricCard 
                        title="Skills Extracted"
                        value={data.parsing_metadata.processing_statistics?.skills_extracted || 0}
                        description="Skills identified"
                      />
                      <MetricCard 
                        title="Data Completeness"
                        value={`${data.parsing_metadata.warnings_and_issues?.data_completeness?.completeness_score || 0}%`}
                        description="Data extraction completeness"
                      />
                    </div>
                    
                    {data.parsing_metadata.processing_steps && (
                      <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <h5 className="font-medium text-gray-900 mb-3">Processing Steps Completed:</h5>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                          {Object.entries(data.parsing_metadata.processing_steps).map(([step, completed]: [string, any]) => (
                            <div key={step} className="flex items-center">
                              <span className={`inline-block w-3 h-3 rounded-full mr-2 ${completed ? 'bg-green-500' : 'bg-red-500'}`}></span>
                              <span className="text-sm text-gray-700 capitalize">{step.replace('_', ' ')}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </InsightSection>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
