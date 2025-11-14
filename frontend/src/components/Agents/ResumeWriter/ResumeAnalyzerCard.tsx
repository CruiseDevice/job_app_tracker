// FILE: frontend/src/components/Agents/ResumeWriter/ResumeAnalyzerCard.tsx

import React, { useState } from 'react';

interface ResumeAnalyzerCardProps {
  resumeText: string;
  setResumeText: (text: string) => void;
}

const ResumeAnalyzerCard: React.FC<ResumeAnalyzerCardProps> = ({ resumeText, setResumeText }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<string>('');
  const [error, setError] = useState<string>('');

  const analyzeResume = async () => {
    if (!resumeText.trim()) {
      setError('Please provide resume text to analyze');
      return;
    }

    setAnalyzing(true);
    setError('');
    setAnalysis('');

    try {
      const response = await fetch('http://localhost:8000/api/agents/resume-writer/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_text: resumeText,
          metadata: {}
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setAnalysis(data.output);
      } else {
        setError(data.error || 'Failed to analyze resume');
      }
    } catch (err) {
      setError(`Error analyzing resume: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Resume Analysis</h2>
      <p className="text-gray-600 mb-6">
        Upload or paste your resume to get comprehensive AI-powered analysis including structure, content metrics, and improvement suggestions.
      </p>

      {/* Input Section */}
      <div className="mb-6">
        <label htmlFor="resume-input" className="block text-sm font-medium text-gray-700 mb-2">
          Resume Content
        </label>
        <textarea
          id="resume-input"
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
          placeholder="Paste your resume text here..."
          className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y font-mono text-sm"
        />
        <p className="mt-2 text-sm text-gray-500">
          {resumeText.length} characters | {resumeText.split(/\s+/).filter(w => w).length} words
        </p>
      </div>

      {/* Analyze Button */}
      <button
        onClick={analyzeResume}
        disabled={analyzing || !resumeText.trim()}
        className={`px-6 py-3 rounded-lg font-medium transition-colors ${
          analyzing || !resumeText.trim()
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {analyzing ? (
          <span className="flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Analyzing Resume...
          </span>
        ) : (
          '📊 Analyze Resume'
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

      {/* Analysis Results */}
      {analysis && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Analysis Results</h3>
            <button
              onClick={() => navigator.clipboard.writeText(analysis)}
              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded hover:bg-blue-50 transition-colors"
            >
              📋 Copy Results
            </button>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800 leading-relaxed">
              {analysis}
            </pre>
          </div>

          {/* Key Insights Section */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">✅ Strengths</h4>
              <p className="text-sm text-blue-800">
                Check the analysis above for identified strengths in your resume
              </p>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-semibold text-yellow-900 mb-2">⚠️ Areas to Improve</h4>
              <p className="text-sm text-yellow-800">
                Review suggestions for enhancing your resume content
              </p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-2">💡 Next Steps</h4>
              <p className="text-sm text-green-800">
                Use the Tailor and ATS Check tabs to optimize further
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Sample Output Preview (when no analysis yet) */}
      {!analysis && !analyzing && !error && resumeText && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">What you'll get:</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Contact information verification</li>
            <li>• Content metrics (word count, bullet points, experience entries)</li>
            <li>• Detected skills and action verbs analysis</li>
            <li>• Overall assessment with specific improvement recommendations</li>
            <li>• Format and structure evaluation</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResumeAnalyzerCard;
