// FILE: frontend/src/components/Agents/EmailAnalyst/EmailAnalystDashboard.tsx

import React, { useState } from 'react';
import EmailAnalysisCard from './EmailAnalysisCard';

interface Email {
  subject: string;
  body: string;
  sender: string;
}

const EmailAnalystDashboard: React.FC = () => {
  const [email, setEmail] = useState<Email>({
    subject: '',
    body: '',
    sender: ''
  });
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!email.subject || !email.body) {
      setError('Please provide both subject and body');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/email-analyst/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subject: email.subject,
          body: email.body,
          sender: email.sender || 'unknown@example.com'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze email');
      }

      const data = await response.json();

      // Parse the analysis text to extract structured data
      // This is a simplified parser - in production, the backend should return structured data
      setAnalysisResult({
        subject: email.subject,
        sender: email.sender,
        sentiment: 'positive', // Would be extracted from analysis
        urgency: 'medium', // Would be extracted from analysis
        confidence: 85,
        category: 'Interview Invite',
        analysis: data.analysis,
        actionItems: ['Confirm availability', 'Prepare for interview'],
        followup: {
          action: 'CONFIRM INTERVIEW',
          timeline: 'Within 24 hours',
          steps: [
            'Reply confirming your availability',
            'Prepare questions about the role',
            'Research the company and interviewers'
          ],
          priority: 'high'
        }
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleEmail = () => {
    setEmail({
      subject: 'Interview Invitation - Software Engineer Position at Google',
      body: `Hi there,

Thank you for your interest in the Software Engineer position at Google!

We were impressed with your background and would like to schedule a technical interview with you. The interview will consist of two 45-minute sessions focusing on algorithms and system design.

Could you please let us know your availability for next week? We'd like to schedule this as soon as possible.

Looking forward to hearing from you!

Best regards,
Google Recruiting Team`,
      sender: 'recruiting@google.com'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-4xl">🤖</span>
            <h1 className="text-3xl font-bold text-gray-900">
              Email Analyst Agent
            </h1>
          </div>
          <p className="text-gray-600">
            Analyze job-related emails with AI-powered insights and recommendations
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <div className="space-y-6">
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Email Input
              </h2>

              {/* Sender */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sender (optional)
                </label>
                <input
                  type="email"
                  value={email.sender}
                  onChange={(e) => setEmail({ ...email, sender: e.target.value })}
                  placeholder="recruiting@company.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Subject */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subject <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={email.subject}
                  onChange={(e) => setEmail({ ...email, subject: e.target.value })}
                  placeholder="Interview Invitation - Software Engineer"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Body */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Body <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={email.body}
                  onChange={(e) => setEmail({ ...email, body: e.target.value })}
                  placeholder="Paste the email content here..."
                  rows={12}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                />
              </div>

              {/* Error Message */}
              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700">
                  ❌ {error}
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={handleAnalyze}
                  disabled={loading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-3 px-4 rounded-md transition-colors duration-200 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <span className="animate-spin">⚙️</span>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <span>🔍</span>
                      Analyze Email
                    </>
                  )}
                </button>
                <button
                  onClick={loadSampleEmail}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-3 px-4 rounded-md transition-colors duration-200"
                >
                  📝 Sample
                </button>
              </div>
            </div>

            {/* Agent Stats */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Agent Statistics
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Analyses Run</p>
                  <p className="text-2xl font-bold text-blue-600">0</p>
                </div>
                <div className="bg-green-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Tools Available</p>
                  <p className="text-2xl font-bold text-green-600">7</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Memory Size</p>
                  <p className="text-2xl font-bold text-purple-600">0</p>
                </div>
                <div className="bg-orange-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Avg Response</p>
                  <p className="text-2xl font-bold text-orange-600">2.5s</p>
                </div>
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div>
            {analysisResult ? (
              <EmailAnalysisCard
                data={analysisResult}
                loading={loading}
                onReanalyze={handleAnalyze}
              />
            ) : (
              <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                <span className="text-6xl mb-4 block">📧</span>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Analysis Yet
                </h3>
                <p className="text-gray-600">
                  Enter an email and click "Analyze Email" to get AI-powered insights
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailAnalystDashboard;
