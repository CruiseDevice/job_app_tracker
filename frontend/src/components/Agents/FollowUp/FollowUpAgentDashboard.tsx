// FILE: frontend/src/components/Agents/FollowUp/FollowUpAgentDashboard.tsx

import React, { useState } from 'react';
import TimingOptimizerCard from './TimingOptimizerCard';
import MessageDrafterCard from './MessageDrafterCard';
import StrategyPlannerCard from './StrategyPlannerCard';
import FollowUpScheduleCard from './FollowUpScheduleCard';

interface FollowUpJob {
  jobId: number;
  company: string;
  position: string;
  status: string;
  applicationDate: string;
  daysSinceContact: number;
}

const FollowUpAgentDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'timing' | 'draft' | 'strategy' | 'schedule'>('timing');
  const [selectedJob, setSelectedJob] = useState<FollowUpJob | null>(null);

  // Sample jobs (in production, this would come from API)
  const sampleJobs: FollowUpJob[] = [
    {
      jobId: 1,
      company: 'Google',
      position: 'Software Engineer',
      status: 'applied',
      applicationDate: '2025-11-01',
      daysSinceContact: 8
    },
    {
      jobId: 2,
      company: 'Meta',
      position: 'Frontend Developer',
      status: 'interview',
      applicationDate: '2025-10-25',
      daysSinceContact: 3
    },
    {
      jobId: 3,
      company: 'Amazon',
      position: 'Backend Engineer',
      status: 'applied',
      applicationDate: '2025-10-20',
      daysSinceContact: 15
    }
  ];

  const loadSampleJob = (index: number) => {
    setSelectedJob(sampleJobs[index]);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Follow-up Agent Dashboard
          </h1>
          <p className="text-gray-600">
            AI-powered follow-up management with timing optimization and personalized messaging
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Pending Follow-ups</div>
            <div className="text-3xl font-bold text-blue-600">7</div>
            <div className="text-xs text-gray-500 mt-1">2 overdue</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Response Rate</div>
            <div className="text-3xl font-bold text-green-600">29%</div>
            <div className="text-xs text-green-500 mt-1">↑ 5% from last month</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Sent This Week</div>
            <div className="text-3xl font-bold text-purple-600">12</div>
            <div className="text-xs text-gray-500 mt-1">3 responded</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Avg. Response Time</div>
            <div className="text-3xl font-bold text-orange-600">2.3d</div>
            <div className="text-xs text-gray-500 mt-1">Within 48 hours</div>
          </div>
        </div>

        {/* Sample Job Selector */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Select Application</h3>
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
                <div className="mt-2 flex items-center justify-between">
                  <span className={`text-xs px-2 py-1 rounded ${
                    job.status === 'interview'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {job.status}
                  </span>
                  <span className="text-xs text-gray-500">
                    {job.daysSinceContact}d ago
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-t-lg shadow">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('timing')}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'timing'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              ⏰ Timing Optimizer
            </button>
            <button
              onClick={() => setActiveTab('draft')}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'draft'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              ✉️ Message Drafter
            </button>
            <button
              onClick={() => setActiveTab('strategy')}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'strategy'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              🎯 Strategy Planner
            </button>
            <button
              onClick={() => setActiveTab('schedule')}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === 'schedule'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              📅 Schedule
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-b-lg shadow p-6">
          {activeTab === 'timing' && (
            <TimingOptimizerCard selectedJob={selectedJob} />
          )}
          {activeTab === 'draft' && (
            <MessageDrafterCard selectedJob={selectedJob} />
          )}
          {activeTab === 'strategy' && (
            <StrategyPlannerCard selectedJob={selectedJob} />
          )}
          {activeTab === 'schedule' && (
            <FollowUpScheduleCard />
          )}
        </div>

        {/* Tips Section */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">Follow-up Best Practices</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start">
              <div className="text-2xl mr-3">⏱️</div>
              <div>
                <div className="font-medium text-blue-900">Timing is Everything</div>
                <div className="text-sm text-blue-700">
                  Wait 7 days after application, 2 days after interview, respond to offers within 24 hours
                </div>
              </div>
            </div>
            <div className="flex items-start">
              <div className="text-2xl mr-3">✍️</div>
              <div>
                <div className="font-medium text-blue-900">Personalize Every Message</div>
                <div className="text-sm text-blue-700">
                  Reference specific details from the job posting or interview conversation
                </div>
              </div>
            </div>
            <div className="flex items-start">
              <div className="text-2xl mr-3">📊</div>
              <div>
                <div className="font-medium text-blue-900">Track and Learn</div>
                <div className="text-sm text-blue-700">
                  Monitor response rates and adjust your strategy based on what works
                </div>
              </div>
            </div>
            <div className="flex items-start">
              <div className="text-2xl mr-3">🎯</div>
              <div>
                <div className="font-medium text-blue-900">Know When to Stop</div>
                <div className="text-sm text-blue-700">
                  After 3-4 attempts without response, focus your energy elsewhere
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FollowUpAgentDashboard;
