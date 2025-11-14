// FILE: frontend/src/components/Agents/Analytics/OfferPredictionCard.tsx

import React, { useState } from 'react';
import axios from 'axios';

const OfferPredictionCard: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    jobTitle: 'Software Engineer',
    companySize: 'Medium',
    industry: 'Technology',
    skillsMatch: 75,
    hasReferral: false,
    hasCoverLetter: true,
    yearsExperience: 5,
    applicationQuality: 8.0
  });

  const predictOffer = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/agents/analytics/predict-offer', {
        job_details: {
          title: formData.jobTitle,
          company_size: formData.companySize,
          industry: formData.industry
        },
        user_profile: {
          skills_match_percent: formData.skillsMatch,
          has_referral: formData.hasReferral,
          has_cover_letter: formData.hasCoverLetter,
          years_experience: formData.yearsExperience,
          application_quality_score: formData.applicationQuality
        }
      });

      setPrediction(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to predict offer likelihood');
      console.error('Error predicting offer:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Sample prediction for display
  const sampleLikelihood = 68;
  const sampleConfidence = 'high';

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">Job Offer Likelihood Predictor</h3>
        <span className="text-2xl">🎯</span>
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
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company Size
          </label>
          <select
            value={formData.companySize}
            onChange={(e) => setFormData({ ...formData, companySize: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="Startup">Startup (1-50)</option>
            <option value="Small">Small (51-200)</option>
            <option value="Medium">Medium (201-1000)</option>
            <option value="Large">Large (1000+)</option>
          </select>
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

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Skills Match: {formData.skillsMatch}%
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={formData.skillsMatch}
            onChange={(e) => setFormData({ ...formData, skillsMatch: parseInt(e.target.value) })}
            className="w-full"
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
            Application Quality: {formData.applicationQuality}/10
          </label>
          <input
            type="range"
            min="1"
            max="10"
            step="0.5"
            value={formData.applicationQuality}
            onChange={(e) => setFormData({ ...formData, applicationQuality: parseFloat(e.target.value) })}
            className="w-full"
          />
        </div>

        <div className="md:col-span-2 flex gap-6">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.hasReferral}
              onChange={(e) => setFormData({ ...formData, hasReferral: e.target.checked })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Has Employee Referral</span>
          </label>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.hasCoverLetter}
              onChange={(e) => setFormData({ ...formData, hasCoverLetter: e.target.checked })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Has Personalized Cover Letter</span>
          </label>
        </div>
      </div>

      {/* Prediction Result */}
      <div className="mb-6">
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-6">
          <div className="text-center mb-4">
            <div className="text-sm text-gray-600 mb-2">Predicted Offer Likelihood</div>
            <div className="relative w-40 h-40 mx-auto">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="80"
                  cy="80"
                  r="70"
                  stroke="#E5E7EB"
                  strokeWidth="12"
                  fill="none"
                />
                <circle
                  cx="80"
                  cy="80"
                  r="70"
                  stroke="#3B82F6"
                  strokeWidth="12"
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 70}`}
                  strokeDashoffset={`${2 * Math.PI * 70 * (1 - sampleLikelihood / 100)}`}
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-600">{sampleLikelihood}%</div>
                  <div className="text-xs text-gray-500 uppercase">{sampleConfidence}</div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-sm text-gray-600 mb-1">Screening</div>
              <div className="text-lg font-bold text-green-600">83%</div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Interview</div>
              <div className="text-lg font-bold text-blue-600">68%</div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Offer</div>
              <div className="text-lg font-bold text-purple-600">48%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Strengths and Improvements */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-green-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-green-900 mb-3">✓ Strengths</h4>
          <ul className="space-y-2 text-sm text-green-800">
            <li>• Strong skills alignment ({formData.skillsMatch}%)</li>
            {formData.applicationQuality >= 8 && <li>• High-quality application</li>}
            {formData.yearsExperience >= 5 && <li>• Solid experience level</li>}
            {formData.hasReferral && <li>• Employee referral (+20% boost)</li>}
          </ul>
        </div>

        <div className="bg-orange-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-orange-900 mb-3">⚠ Areas for Improvement</h4>
          <ul className="space-y-2 text-sm text-orange-800">
            {formData.skillsMatch < 70 && <li>• Skills match below 70%</li>}
            {!formData.hasReferral && <li>• Seek employee referral (+20%)</li>}
            {formData.applicationQuality < 8 && <li>• Improve application quality</li>}
            {formData.yearsExperience < 3 && <li>• Limited experience for role</li>}
          </ul>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-blue-50 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-medium text-blue-900 mb-3">💡 Recommendations</h4>
        <ul className="space-y-2 text-sm text-blue-800">
          {!formData.hasReferral && (
            <li>• <strong>Seek employee referral</strong> - can increase chances by 20%</li>
          )}
          {formData.skillsMatch < 70 && (
            <li>• <strong>Tailor resume</strong> to better match job requirements</li>
          )}
          {formData.applicationQuality < 8 && (
            <li>• <strong>Improve application quality</strong> - current: {formData.applicationQuality}/10</li>
          )}
          <li>• <strong>Network</strong> with employees at target company</li>
          <li>• <strong>Follow up</strong> 7-10 days after applying</li>
        </ul>
      </div>

      {/* Predict Button */}
      <button
        onClick={predictOffer}
        disabled={isLoading}
        className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Predicting...
          </span>
        ) : (
          '🤖 Predict Offer Likelihood'
        )}
      </button>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Prediction Result */}
      {prediction && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <h4 className="font-medium text-green-900 mb-2">Prediction Complete</h4>
          <pre className="text-sm text-green-800 whitespace-pre-wrap">{prediction.prediction}</pre>
        </div>
      )}
    </div>
  );
};

export default OfferPredictionCard;
