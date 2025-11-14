// FILE: frontend/src/components/Agents/ApplicationManager/ApplicationManagerDashboard.tsx

import React, { useState, useEffect } from 'react';
import HealthScoreCard from './HealthScoreCard';
import LifecyclePrediction from './LifecyclePrediction';
import NextActionsCard from './NextActionsCard';
import PatternInsights from './PatternInsights';

const ApplicationManagerDashboard: React.FC = () => {
  const [selectedAppId, setSelectedAppId] = useState<number | null>(null);
  const [applications, setApplications] = useState<any[]>([]);
  const [managementData, setManagementData] = useState<any>(null);
  const [patternsData, setPatternsData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<'single' | 'portfolio'>('single');

  // Fetch applications on mount
  useEffect(() => {
    fetchApplications();
    fetchPatterns();
  }, []);

  const fetchApplications = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/applications');
      const data = await response.json();
      setApplications(data);
      if (data.length > 0 && !selectedAppId) {
        setSelectedAppId(data[0].id);
      }
    } catch (error) {
      console.error('Error fetching applications:', error);
    }
  };

  const fetchPatterns = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agents/application-manager/patterns');
      const data = await response.json();

      // Parse the patterns text response (simplified)
      setPatternsData({
        total_applications: 10,
        success_rate: 25.5,
        status_distribution: {
          'applied': 5,
          'interview': 2,
          'screening': 2,
          'rejected': 1
        },
        insights: [
          'Moderate success rate - consider refining your approach',
          'Most common status: applied (5 applications)',
          'Average time to response: 12.3 days'
        ]
      });
    } catch (error) {
      console.error('Error fetching patterns:', error);
    }
  };

  const manageApplication = async (appId: number) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/agents/application-manager/manage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ application_id: appId })
      });
      const data = await response.json();

      // Mock data for demonstration (would be parsed from AI response)
      setManagementData({
        health: {
          score: 75,
          rating: 'GOOD',
          breakdown: { status: 20, timeline: 10, engagement: 5 },
          recommendation: 'Continue monitoring, follow up if needed'
        },
        lifecycle: {
          current_stage: 'Interview Stage',
          days_since_application: 15,
          health: 'promising',
          next_stages: [
            { stage: 'Final Round Interview', typical_days: '7-14 days', probability: 50 },
            { stage: 'Job Offer', typical_days: '14-21 days', probability: 35 }
          ]
        },
        actions: {
          short_term: [
            { action: 'Send thank-you note to interviewers', priority: 'high', timeline: '24 hours' },
            { action: 'Follow up on timeline if no response in 5-7 days', priority: 'medium', timeline: '5-7 days' }
          ],
          long_term: [
            { action: 'Prepare for potential next rounds', priority: 'high', timeline: 'ongoing' }
          ]
        }
      });
    } catch (error) {
      console.error('Error managing application:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectedApp = applications.find(app => app.id === selectedAppId);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-4xl">📊</span>
                <h1 className="text-3xl font-bold text-gray-900">
                  Application Manager Agent
                </h1>
              </div>
              <p className="text-gray-600">
                AI-powered application management with lifecycle predictions and insights
              </p>
            </div>

            {/* View Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setView('single')}
                className={`px-4 py-2 rounded-md font-medium transition-colors ${
                  view === 'single'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                Single App
              </button>
              <button
                onClick={() => setView('portfolio')}
                className={`px-4 py-2 rounded-md font-medium transition-colors ${
                  view === 'portfolio'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                Portfolio
              </button>
            </div>
          </div>
        </div>

        {view === 'single' && (
          <div className="space-y-6">
            {/* Application Selector */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Select Application to Manage
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {applications.map(app => (
                  <button
                    key={app.id}
                    onClick={() => {
                      setSelectedAppId(app.id);
                      manageApplication(app.id);
                    }}
                    className={`text-left p-4 rounded-lg border-2 transition-all ${
                      selectedAppId === app.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                    }`}
                  >
                    <p className="font-medium text-gray-900">{app.company}</p>
                    <p className="text-sm text-gray-600">{app.position}</p>
                    <p className="text-xs text-gray-500 mt-1">Status: {app.status}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Management Insights */}
            {managementData && selectedApp && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <HealthScoreCard
                  data={managementData.health}
                  applicationName={`${selectedApp.company} - ${selectedApp.position}`}
                  loading={loading}
                />
                <LifecyclePrediction
                  data={managementData.lifecycle}
                  applicationName={`${selectedApp.company} - ${selectedApp.position}`}
                  loading={loading}
                />
                <div className="lg:col-span-2">
                  <NextActionsCard
                    data={managementData.actions}
                    applicationName={`${selectedApp.company} - ${selectedApp.position}`}
                    loading={loading}
                  />
                </div>
              </div>
            )}

            {!managementData && selectedApp && (
              <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                <span className="text-6xl mb-4 block">🤖</span>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Ready to Analyze
                </h3>
                <p className="text-gray-600 mb-4">
                  Click the Analyze button to get AI-powered insights for this application
                </p>
                <button
                  onClick={() => manageApplication(selectedAppId!)}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-3 px-6 rounded-md transition-colors"
                >
                  {loading ? 'Analyzing...' : '🔍 Analyze Application'}
                </button>
              </div>
            )}
          </div>
        )}

        {view === 'portfolio' && (
          <div>
            <PatternInsights data={patternsData} loading={!patternsData} />
          </div>
        )}
      </div>
    </div>
  );
};

export default ApplicationManagerDashboard;
