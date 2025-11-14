// FILE: frontend/src/components/Agents/ResumeWriter/ResumeWriterDashboard.tsx

import React, { useState } from 'react';
import ResumeAnalyzerCard from './ResumeAnalyzerCard';
import ResumeTailorCard from './ResumeTailorCard';
import CoverLetterCard from './CoverLetterCard';
import ATSCheckerCard from './ATSCheckerCard';

interface JobListing {
  jobId: number;
  company: string;
  position: string;
  requirements: string;
  keywords: string[];
}

const ResumeWriterDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'analyze' | 'tailor' | 'cover-letter' | 'ats-check'>('analyze');
  const [resumeText, setResumeText] = useState('');
  const [selectedJob, setSelectedJob] = useState<JobListing | null>(null);

  // Sample job listings (in production, this would come from API)
  const sampleJobs: JobListing[] = [
    {
      jobId: 1,
      company: 'Google',
      position: 'Senior Software Engineer',
      requirements: '5+ years Python, React, AWS experience. Strong system design skills. Team leadership.',
      keywords: ['Python', 'React', 'AWS', 'System Design', 'Agile', 'Microservices']
    },
    {
      jobId: 2,
      company: 'Meta',
      position: 'Frontend Developer',
      requirements: '3+ years React, TypeScript, GraphQL. Strong UI/UX skills.',
      keywords: ['React', 'TypeScript', 'GraphQL', 'UI/UX', 'Jest', 'Webpack']
    },
    {
      jobId: 3,
      company: 'Amazon',
      position: 'Backend Engineer',
      requirements: '4+ years Java or Python. Distributed systems. Database design.',
      keywords: ['Java', 'Python', 'SQL', 'NoSQL', 'Distributed Systems', 'API Design']
    }
  ];

  const loadSampleResume = () => {
    const sampleResume = `JOHN DOE
Software Engineer
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

SUMMARY
Experienced software engineer with 6+ years building scalable web applications using Python, JavaScript, and cloud technologies.

EXPERIENCE
Senior Software Engineer | TechCorp Inc. | 2021 - Present
• Developed microservices architecture serving 2M+ daily users
• Reduced API response time by 40% through optimization
• Led team of 4 engineers on critical infrastructure projects
• Implemented CI/CD pipelines reducing deployment time by 60%

Software Engineer | StartupXYZ | 2018 - 2021
• Built full-stack web applications using React and Python
• Designed and implemented RESTful APIs
• Collaborated with cross-functional teams on product features
• Mentored junior developers and conducted code reviews

EDUCATION
Bachelor of Science in Computer Science | State University | 2018
GPA: 3.7/4.0

SKILLS
Languages: Python, JavaScript, TypeScript, Java
Frameworks: React, Node.js, Django, FastAPI
Cloud: AWS, Docker, Kubernetes
Databases: PostgreSQL, MongoDB, Redis`;

    setResumeText(sampleResume);
  };

  const loadSampleJob = (index: number) => {
    setSelectedJob(sampleJobs[index]);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Resume Writer Agent Dashboard
          </h1>
          <p className="text-gray-600">
            AI-powered resume optimization, ATS checking, and cover letter generation
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Resumes Analyzed</div>
            <div className="text-3xl font-bold text-blue-600">24</div>
            <div className="text-xs text-gray-500 mt-1">This month</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Avg. ATS Score</div>
            <div className="text-3xl font-bold text-green-600">87%</div>
            <div className="text-xs text-green-500 mt-1">↑ 12% improvement</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Cover Letters</div>
            <div className="text-3xl font-bold text-purple-600">15</div>
            <div className="text-xs text-gray-500 mt-1">Generated</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Applications Tailored</div>
            <div className="text-3xl font-bold text-orange-600">31</div>
            <div className="text-xs text-gray-500 mt-1">For specific roles</div>
          </div>
        </div>

        {/* Sample Data Loaders */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Quick Start</h3>

          {/* Load Sample Resume */}
          <div className="mb-4">
            <button
              onClick={loadSampleResume}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              📄 Load Sample Resume
            </button>
            <span className="ml-3 text-sm text-gray-600">
              {resumeText ? '✓ Resume loaded' : 'Load a sample resume to get started'}
            </span>
          </div>

          {/* Select Job for Tailoring */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Select Job for Tailoring:</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {sampleJobs.map((job, index) => (
                <button
                  key={job.jobId}
                  onClick={() => loadSampleJob(index)}
                  className={`p-4 border-2 rounded-lg text-left transition-all ${
                    selectedJob?.jobId === job.jobId
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300'
                  }`}
                >
                  <div className="font-semibold text-gray-900">{job.company}</div>
                  <div className="text-sm text-gray-600">{job.position}</div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {job.keywords.slice(0, 3).map((keyword, i) => (
                      <span key={i} className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-t-lg shadow">
          <div className="flex border-b overflow-x-auto">
            <button
              onClick={() => setActiveTab('analyze')}
              className={`flex-1 min-w-[150px] px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'analyze'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              📊 Analyze Resume
            </button>
            <button
              onClick={() => setActiveTab('tailor')}
              className={`flex-1 min-w-[150px] px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'tailor'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              🎯 Tailor to Job
            </button>
            <button
              onClick={() => setActiveTab('cover-letter')}
              className={`flex-1 min-w-[150px] px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'cover-letter'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              ✉️ Cover Letter
            </button>
            <button
              onClick={() => setActiveTab('ats-check')}
              className={`flex-1 min-w-[150px] px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'ats-check'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              🤖 ATS Check
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-b-lg shadow p-6">
          {activeTab === 'analyze' && (
            <ResumeAnalyzerCard resumeText={resumeText} setResumeText={setResumeText} />
          )}
          {activeTab === 'tailor' && (
            <ResumeTailorCard
              resumeText={resumeText}
              selectedJob={selectedJob}
              setResumeText={setResumeText}
            />
          )}
          {activeTab === 'cover-letter' && (
            <CoverLetterCard selectedJob={selectedJob} />
          )}
          {activeTab === 'ats-check' && (
            <ATSCheckerCard resumeText={resumeText} setResumeText={setResumeText} />
          )}
        </div>

        {/* Tips Section */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 Pro Tips</h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li>• <strong>Quantify achievements:</strong> Use numbers, percentages, and metrics (e.g., "Increased efficiency by 40%")</li>
            <li>• <strong>Use action verbs:</strong> Start bullet points with strong verbs (Led, Developed, Achieved, Optimized)</li>
            <li>• <strong>Tailor for each job:</strong> Match keywords and requirements from the job description</li>
            <li>• <strong>Keep it concise:</strong> 1 page for entry-level, 2 pages max for senior positions</li>
            <li>• <strong>ATS-friendly format:</strong> Use standard fonts, avoid tables/images, use simple bullet points</li>
            <li>• <strong>Proofread carefully:</strong> Zero tolerance for typos and grammatical errors</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ResumeWriterDashboard;
