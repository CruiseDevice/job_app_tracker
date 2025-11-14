// FILE: frontend/src/components/Agents/Analytics/SalaryAnalysisCard.tsx

import React, { useState } from 'react';
import axios from 'axios';

const SalaryAnalysisCard: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [salaryData, setSalaryData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    jobTitle: 'Software Engineer',
    location: 'San Francisco, CA',
    yearsExperience: 5,
    industry: 'Technology',
    companySize: 'Medium'
  });

  const analyzeSalary = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/agents/analytics/salary', formData);

      setSalaryData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze salary');
      console.error('Error analyzing salary:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Sample salary data for display
  const sampleSalary = {
    median: 180000,
    p10: 135000,
    p25: 153000,
    p75: 207000,
    p90: 243000,
    bonus: '18,000 - 36,000',
    equity: '27,000 - 54,000',
    total: '225,000 - 270,000'
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">Market Salary Analysis</h3>
        <span className="text-2xl">💰</span>
      </div>

      {/* Input Form */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Title
          </label>
          <input
            type="text"
            value={formData.jobTitle}
            onChange={(e) => setFormData({ ...formData, jobTitle: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., Software Engineer"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., San Francisco, CA or Remote"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Years of Experience
          </label>
          <input
            type="number"
            min="0"
            max="30"
            value={formData.yearsExperience}
            onChange={(e) => setFormData({ ...formData, yearsExperience: parseInt(e.target.value) })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Industry
          </label>
          <select
            value={formData.industry}
            onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="Technology">Technology</option>
            <option value="Finance">Finance</option>
            <option value="Healthcare">Healthcare</option>
            <option value="Retail">Retail</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company Size
          </label>
          <select
            value={formData.companySize}
            onChange={(e) => setFormData({ ...formData, companySize: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="Startup">Startup (1-50 employees)</option>
            <option value="Small">Small (51-200 employees)</option>
            <option value="Medium">Medium (201-1000 employees)</option>
            <option value="Large">Large (1000+ employees)</option>
          </select>
        </div>
      </div>

      {/* Salary Range Display */}
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Base Salary Range (USD)</h4>

        {/* Main Salary Display */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 mb-4">
          <div className="text-center mb-4">
            <div className="text-sm text-gray-600 mb-2">Competitive Salary (Median)</div>
            <div className="text-4xl font-bold text-blue-600">
              ${sampleSalary.median.toLocaleString()}
            </div>
          </div>
          <div className="text-center text-sm text-gray-500">
            Typical Range: ${sampleSalary.p25.toLocaleString()} - ${sampleSalary.p75.toLocaleString()}
          </div>
        </div>

        {/* Percentile Breakdown */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
          <div className="text-center p-3 bg-gray-50 rounded">
            <div className="text-xs text-gray-500 mb-1">10th %ile</div>
            <div className="text-lg font-semibold text-gray-700">
              ${(sampleSalary.p10 / 1000).toFixed(0)}K
            </div>
          </div>
          <div className="text-center p-3 bg-blue-50 rounded">
            <div className="text-xs text-blue-600 mb-1">25th %ile</div>
            <div className="text-lg font-semibold text-blue-700">
              ${(sampleSalary.p25 / 1000).toFixed(0)}K
            </div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded">
            <div className="text-xs text-green-600 mb-1">50th %ile</div>
            <div className="text-lg font-semibold text-green-700">
              ${(sampleSalary.median / 1000).toFixed(0)}K
            </div>
          </div>
          <div className="text-center p-3 bg-purple-50 rounded">
            <div className="text-xs text-purple-600 mb-1">75th %ile</div>
            <div className="text-lg font-semibold text-purple-700">
              ${(sampleSalary.p75 / 1000).toFixed(0)}K
            </div>
          </div>
          <div className="text-center p-3 bg-orange-50 rounded">
            <div className="text-xs text-orange-600 mb-1">90th %ile</div>
            <div className="text-lg font-semibold text-orange-700">
              ${(sampleSalary.p90 / 1000).toFixed(0)}K
            </div>
          </div>
        </div>

        {/* Salary Distribution Visualization */}
        <div className="relative h-8 bg-gray-200 rounded-full overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-300 via-green-300 to-purple-300"></div>
          <div className="absolute left-0 top-0 bottom-0 w-[10%] border-r-2 border-gray-400"></div>
          <div className="absolute left-[25%] top-0 bottom-0 border-r-2 border-blue-500"></div>
          <div className="absolute left-[50%] top-0 bottom-0 border-r-2 border-green-500"></div>
          <div className="absolute left-[75%] top-0 bottom-0 border-r-2 border-purple-500"></div>
          <div className="absolute right-0 top-0 bottom-0 w-[10%] border-l-2 border-gray-400"></div>
        </div>
      </div>

      {/* Total Compensation */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="text-sm text-blue-600 font-medium mb-1">Base Salary</div>
          <div className="text-xl font-bold text-blue-700">${(sampleSalary.median / 1000).toFixed(0)}K</div>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <div className="text-sm text-green-600 font-medium mb-1">Bonus Range</div>
          <div className="text-lg font-bold text-green-700">${sampleSalary.bonus}</div>
        </div>

        <div className="bg-purple-50 rounded-lg p-4">
          <div className="text-sm text-purple-600 font-medium mb-1">Equity Value</div>
          <div className="text-lg font-bold text-purple-700">${sampleSalary.equity}</div>
        </div>
      </div>

      {/* Total Compensation Range */}
      <div className="bg-gradient-to-r from-purple-100 to-blue-100 rounded-lg p-4 mb-6">
        <div className="text-sm text-gray-700 mb-1">Total Compensation Range</div>
        <div className="text-2xl font-bold text-purple-700">${sampleSalary.total}</div>
        <div className="text-xs text-gray-600 mt-1">Including base + bonus + equity</div>
      </div>

      {/* Market Insights */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Market Insights</h4>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">📊</span>
            <span>Median salary for {formData.jobTitle} in {formData.location}: ${sampleSalary.median.toLocaleString()}</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-500 mt-0.5">📈</span>
            <span>Location factor: {formData.location.includes('San Francisco') ? '+40%' : '+15%'} vs national average</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-purple-500 mt-0.5">🏢</span>
            <span>Company size factor: {formData.companySize} companies pay {formData.companySize === 'Large' ? '+15%' : '0%'} vs average</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-orange-500 mt-0.5">⭐</span>
            <span>Top 25% earn above ${sampleSalary.p75.toLocaleString()}</span>
          </li>
        </ul>
      </div>

      {/* Negotiation Tips */}
      <div className="bg-blue-50 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-medium text-blue-900 mb-3">💡 Negotiation Tips</h4>
        <ul className="space-y-2 text-sm text-blue-800">
          <li>• Target salary range: ${sampleSalary.p75.toLocaleString()} - ${sampleSalary.p90.toLocaleString()} for strong candidates</li>
          <li>• Research company-specific compensation on Glassdoor and Levels.fyi</li>
          <li>• Factor in total compensation (base + bonus + equity + benefits)</li>
          <li>• Don't disclose current salary - focus on market rate</li>
          <li>• Ask for 10-20% above your target to leave negotiation room</li>
        </ul>
      </div>

      {/* Benefits to Consider */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Benefits to Consider</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {[
            '🏥 Health Insurance',
            '💰 401(k) Matching',
            '📈 Stock Options',
            '🎁 Sign-on Bonus',
            '🏡 Remote Work',
            '📚 Learning Budget',
            '🌴 PTO Days',
            '👶 Parental Leave'
          ].map((benefit, index) => (
            <div
              key={index}
              className="text-xs text-gray-700 bg-gray-100 px-3 py-2 rounded-lg text-center"
            >
              {benefit}
            </div>
          ))}
        </div>
      </div>

      {/* Analyze Button */}
      <button
        onClick={analyzeSalary}
        disabled={isLoading}
        className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Analyzing...
          </span>
        ) : (
          '🤖 Analyze Market Salary'
        )}
      </button>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Salary Analysis Result */}
      {salaryData && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h4 className="font-medium text-green-900 mb-2">Salary Analysis Complete</h4>
          <pre className="text-sm text-green-800 whitespace-pre-wrap">{salaryData.salary_analysis}</pre>
        </div>
      )}
    </div>
  );
};

export default SalaryAnalysisCard;
