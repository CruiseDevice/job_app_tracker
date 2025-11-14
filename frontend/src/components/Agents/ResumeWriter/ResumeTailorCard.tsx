// FILE: frontend/src/components/Agents/ResumeWriter/ResumeTailorCard.tsx

import React, { useState } from 'react';

interface JobListing {
  jobId: number;
  company: string;
  position: string;
  requirements: string;
  keywords: string[];
}

interface ResumeTailorCardProps {
  resumeText: string;
  selectedJob: JobListing | null;
  setResumeText: (text: string) => void;
}

const ResumeTailorCard: React.FC<ResumeTailorCardProps> = ({ resumeText, selectedJob, setResumeText }) => {
  const [tailoring, setTailoring] = useState(false);
  const [recommendations, setRecommendations] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [candidateExperience, setCandidateExperience] = useState('');

  const tailorResume = async () => {
    if (!selectedJob) {
      setError('Please select a job listing first');
      return;
    }

    if (!candidateExperience.trim()) {
      setError('Please describe your relevant experience');
      return;
    }

    setTailoring(true);
    setError('');
    setRecommendations('');

    try {
      const response = await fetch('http://localhost:8000/api/agents/resume-writer/tailor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_title: selectedJob.position,
          job_requirements: selectedJob.requirements,
          candidate_experience: candidateExperience,
          keywords: selectedJob.keywords.join(', '),
          metadata: { job_id: selectedJob.jobId, company: selectedJob.company }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setRecommendations(data.output);
      } else {
        setError(data.error || 'Failed to generate tailoring recommendations');
      }
    } catch (err) {
      setError(`Error tailoring resume: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setTailoring(false);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Tailor Resume to Job</h2>
      <p className="text-gray-600 mb-6">
        Get AI-powered recommendations to optimize your resume for a specific job posting, including keyword matching and content optimization.
      </p>

      {/* Selected Job Info */}
      {selectedJob ? (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">Selected Position</h3>
          <div className="text-sm text-blue-800">
            <p><strong>{selectedJob.position}</strong> at <strong>{selectedJob.company}</strong></p>
            <p className="mt-2">{selectedJob.requirements}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {selectedJob.keywords.map((keyword, i) => (
                <span key={i} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            ⚠️ Please select a job listing from the Quick Start section above to get tailored recommendations.
          </p>
        </div>
      )}

      {/* Candidate Experience Input */}
      <div className="mb-6">
        <label htmlFor="experience-input" className="block text-sm font-medium text-gray-700 mb-2">
          Your Relevant Experience
        </label>
        <textarea
          id="experience-input"
          value={candidateExperience}
          onChange={(e) => setCandidateExperience(e.target.value)}
          placeholder="Describe your relevant experience, skills, and achievements that match this role..."
          className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
        />
        <p className="mt-2 text-sm text-gray-500">
          Example: "6 years full-stack development with Python and React. Led teams of 4-5 engineers. Expertise in AWS and microservices architecture."
        </p>
      </div>

      {/* Tailor Button */}
      <button
        onClick={tailorResume}
        disabled={tailoring || !selectedJob || !candidateExperience.trim()}
        className={`px-6 py-3 rounded-lg font-medium transition-colors ${
          tailoring || !selectedJob || !candidateExperience.trim()
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {tailoring ? (
          <span className="flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Generating Recommendations...
          </span>
        ) : (
          '🎯 Get Tailoring Recommendations'
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

      {/* Recommendations */}
      {recommendations && (
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Tailoring Recommendations</h3>
            <button
              onClick={() => navigator.clipboard.writeText(recommendations)}
              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded hover:bg-blue-50 transition-colors"
            >
              📋 Copy Recommendations
            </button>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800 leading-relaxed">
              {recommendations}
            </pre>
          </div>

          {/* Action Items */}
          <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-6">
            <h4 className="font-semibold text-green-900 mb-3">✅ Implementation Checklist</h4>
            <ul className="text-sm text-green-800 space-y-2">
              <li>□ Update skills section with matching keywords</li>
              <li>□ Reorder experience bullets to highlight relevant projects</li>
              <li>□ Quantify achievements with specific metrics</li>
              <li>□ Add/modify summary to include key terms from job description</li>
              <li>□ Ensure exact terminology from job posting is used</li>
              <li>□ Run ATS compatibility check after making changes</li>
            </ul>
          </div>
        </div>
      )}

      {/* Sample Output Preview */}
      {!recommendations && !tailoring && !error && selectedJob && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">You'll receive:</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Keyword optimization strategy with placement recommendations</li>
            <li>• Experience highlighting suggestions (which projects to emphasize)</li>
            <li>• Skills section optimization (prioritization and additions)</li>
            <li>• Summary/objective optimization tailored to this role</li>
            <li>• Format and ATS compatibility tips</li>
            <li>• Specific example transformations for your content</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResumeTailorCard;
