// FILE: frontend/src/components/Agents/ResumeWriter/ATSCheckerCard.tsx

import React, { useState } from 'react';

interface ATSCheckerCardProps {
  resumeText: string;
  setResumeText: (text: string) => void;
}

const ATSCheckerCard: React.FC<ATSCheckerCardProps> = ({ resumeText, setResumeText }) => {
  const [checking, setChecking] = useState(false);
  const [atsReport, setAtsReport] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [score, setScore] = useState<number | null>(null);

  const checkATS = async () => {
    if (!resumeText.trim()) {
      setError('Please provide resume text to check');
      return;
    }

    setChecking(true);
    setError('');
    setAtsReport('');
    setScore(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/resume-writer/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_text: resumeText,
          metadata: { check_type: 'ats' }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setAtsReport(data.output);

        // Extract score from output (assuming format includes "SCORE: XX/100")
        const scoreMatch = data.output.match(/(\d+)\/100/);
        if (scoreMatch) {
          setScore(parseInt(scoreMatch[1]));
        }
      } else {
        setError(data.error || 'Failed to check ATS compatibility');
      }
    } catch (err) {
      setError(`Error checking ATS compatibility: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setChecking(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 85) return 'bg-green-50 border-green-200';
    if (score >= 70) return 'bg-yellow-50 border-yellow-200';
    if (score >= 50) return 'bg-orange-50 border-orange-200';
    return 'bg-red-50 border-red-200';
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">ATS Compatibility Checker</h2>
      <p className="text-gray-600 mb-6">
        Check if your resume is compatible with Applicant Tracking Systems (ATS). Get a detailed score and specific recommendations for improvement.
      </p>

      {/* What is ATS Info */}
      <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">🤖 What is ATS?</h3>
        <p className="text-sm text-blue-800">
          Applicant Tracking Systems (ATS) are software used by 75%+ of companies to filter resumes before human review.
          An ATS-incompatible resume may be rejected automatically, even if you're qualified. This tool checks formatting,
          keywords, and structure to ensure your resume passes ATS screening.
        </p>
      </div>

      {/* Input Section */}
      <div className="mb-6">
        <label htmlFor="ats-resume-input" className="block text-sm font-medium text-gray-700 mb-2">
          Resume Content
        </label>
        <textarea
          id="ats-resume-input"
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
          placeholder="Paste your resume text here for ATS compatibility check..."
          className="w-full h-48 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y font-mono text-sm"
        />
      </div>

      {/* Check Button */}
      <button
        onClick={checkATS}
        disabled={checking || !resumeText.trim()}
        className={`px-6 py-3 rounded-lg font-medium transition-colors ${
          checking || !resumeText.trim()
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {checking ? (
          <span className="flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Checking ATS Compatibility...
          </span>
        ) : (
          '🤖 Check ATS Compatibility'
        )}
      </button>

      {/* Error Message */}
      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start">
            <span className="text-red-600 mr-2">❌</span>
            <div>
              <h4 className="text-sm font-semibold text-red-800">Error</h4>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* ATS Score Display */}
      {score !== null && (
        <div className="mt-8">
          <div className={`p-6 border-2 rounded-lg ${getScoreBgColor(score)}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">ATS Compatibility Score</h3>
                <p className="text-sm text-gray-600">
                  {score >= 85 && '✅ Excellent - Highly ATS-compatible'}
                  {score >= 70 && score < 85 && '⚠️ Good - Minor improvements recommended'}
                  {score >= 50 && score < 70 && '⚠️ Fair - Several issues to address'}
                  {score < 50 && '❌ Poor - Significant improvements needed'}
                </p>
              </div>
              <div className={`text-6xl font-bold ${getScoreColor(score)}`}>
                {score}
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mt-4 w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${
                  score >= 85 ? 'bg-green-600' :
                  score >= 70 ? 'bg-yellow-500' :
                  score >= 50 ? 'bg-orange-500' :
                  'bg-red-500'
                }`}
                style={{ width: `${score}%` }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {/* Detailed ATS Report */}
      {atsReport && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Detailed ATS Report</h3>
            <button
              onClick={() => navigator.clipboard.writeText(atsReport)}
              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded hover:bg-blue-50 transition-colors"
            >
              📋 Copy Report
            </button>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800 leading-relaxed">
              {atsReport}
            </pre>
          </div>

          {/* Key Issues Summary */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-2">✅ Passed Checks</h4>
              <p className="text-sm text-green-800">
                Review which ATS requirements your resume meets
              </p>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-semibold text-yellow-900 mb-2">⚠️ Warnings</h4>
              <p className="text-sm text-yellow-800">
                Minor issues that could be improved
              </p>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h4 className="font-semibold text-red-900 mb-2">❌ Critical Issues</h4>
              <p className="text-sm text-red-800">
                Must-fix problems that block ATS parsing
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ATS Best Practices Guide */}
      {!atsReport && !checking && !error && (
        <div className="mt-8">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">ATS Best Practices</h3>

            <div className="space-y-6">
              {/* Formatting */}
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">📐 Formatting</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>✓ Use standard fonts (Arial, Calibri, Times New Roman)</li>
                  <li>✓ Avoid tables, text boxes, headers/footers</li>
                  <li>✓ Use simple bullet points (-, •)</li>
                  <li>✓ Maintain consistent formatting throughout</li>
                  <li>✗ Don't use images, graphics, or logos</li>
                  <li>✗ Avoid fancy fonts or unusual characters</li>
                </ul>
              </div>

              {/* Section Headers */}
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">📋 Section Headers</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>✓ Use standard headers: "Work Experience", "Education", "Skills"</li>
                  <li>✓ Keep headers clear and recognizable</li>
                  <li>✗ Avoid creative headers like "My Journey" or "What I Bring"</li>
                </ul>
              </div>

              {/* Keywords */}
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">🔑 Keywords</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>✓ Include exact keywords from job description</li>
                  <li>✓ Spell out acronyms: "Application Programming Interface (API)"</li>
                  <li>✓ Use both spelled-out and abbreviated forms</li>
                  <li>✓ Place keywords naturally in context</li>
                </ul>
              </div>

              {/* File Format */}
              <div>
                <h4 className="font-semibold text-gray-800 mb-2">💾 File Format</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>✓ Save as .docx (preferred) or text-based PDF</li>
                  <li>✗ Avoid image-based PDFs or scanned documents</li>
                  <li>✓ Use simple file names: "FirstName_LastName_Resume.docx"</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ATSCheckerCard;
