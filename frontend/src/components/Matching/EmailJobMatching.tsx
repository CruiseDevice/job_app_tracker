import React, { useState, useEffect } from 'react';
import { Link, Mail, CheckCircle, X, AlertCircle, BarChart3, Zap, Settings, RefreshCw } from 'lucide-react';
import { EmailJobLink, MatchSuggestion, MatchingStatistics, BulkMatchingResult } from '../../types/matching';
import type { JobApplication } from '../../types/application';

interface EmailJobMatchingProps {}

// Mock API data - replace with actual API calls
const mockMatchingData = {
  linkedEmails: [
    {
      id: 1,
      email_id: "email_1",
      job_id: 1,
      confidence_score: 95.5,
      match_methods: ["company_exact", "position_match", "domain_match"],
      match_details: {},
      match_explanation: "Company name exactly matches, job position mentioned, email domain matches company",
      link_type: "auto" as const,
      created_at: "2024-12-20T10:35:00Z",
      created_by: "system",
      is_verified: true,
      is_rejected: false,
      updated_at: "2024-12-20T10:35:00Z"
    },
    {
      id: 2,
      email_id: "email_2", 
      job_id: 1,
      confidence_score: 87.2,
      match_methods: ["company_exact", "keyword_match"],
      match_details: {},
      match_explanation: "Company name exactly matches, job-related keywords found",
      link_type: "auto" as const,
      created_at: "2024-12-21T14:20:00Z",
      created_by: "system",
      is_verified: false,
      is_rejected: false,
      updated_at: "2024-12-21T14:20:00Z"
    },
    {
      id: 3,
      email_id: "email_3",
      job_id: 2,
      confidence_score: 72.8,
      match_methods: ["company_fuzzy", "time_proximity"],
      match_details: {},
      match_explanation: "Company name closely matches, email and job close in time",
      link_type: "manual" as const,
      created_at: "2024-12-22T09:05:00Z",
      created_by: "user",
      is_verified: true,
      is_rejected: false,
      updated_at: "2024-12-22T09:05:00Z"
    }
  ] as EmailJobLink[],

  suggestions: [
    {
      email_id: "email_4",
      job_id: 3,
      confidence_score: 68.4,
      match_methods: ["domain_match", "keyword_match"],
      match_explanation: "Email domain matches company, job-related keywords found",
      email_details: {
        email_id: "email_4",
        subject: "Follow up on your application",
        sender: "recruiting@netflix.com",
        date: "2024-12-23T11:00:00Z"
      },
      job_details: { company: "Netflix", position: "Backend Engineer" },
      created_at: "2024-12-23T11:05:00Z",
      is_auto_linkable: false
    }
  ] as MatchSuggestion[],

  statistics: {
    period: { days: 30, start_date: "2024-11-23", end_date: "2024-12-23" },
    totals: { total_links: 15, verified_links: 12, rejected_links: 2, auto_links: 10, manual_links: 5 },
    rates: { verification_rate: 80.0, rejection_rate: 13.3, auto_link_rate: 66.7 },
    confidence_distribution: { very_low: 1, low: 2, medium: 4, high: 6, very_high: 2 },
    quality_metrics: { average_confidence: 78.3, high_confidence_percentage: 53.3 }
  } as MatchingStatistics
};

const EmailJobMatching: React.FC<EmailJobMatchingProps> = () => {
  const [linkedEmails, setLinkedEmails] = useState<EmailJobLink[]>([]);
  const [suggestions, setSuggestions] = useState<MatchSuggestion[]>([]);
  const [statistics, setStatistics] = useState<MatchingStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'links' | 'suggestions' | 'statistics'>('links');
  const [selectedLinks, setSelectedLinks] = useState<Set<number>>(new Set());
  const [bulkProcessing, setBulkProcessing] = useState(false);

  useEffect(() => {
    loadMatchingData();
  }, []);

  const loadMatchingData = async () => {
    setLoading(true);
    try {
      // Simulate API calls
      await new Promise(resolve => setTimeout(resolve, 1000));
      setLinkedEmails(mockMatchingData.linkedEmails);
      setSuggestions(mockMatchingData.suggestions);
      setStatistics(mockMatchingData.statistics);
    } catch (error) {
      console.error('Error loading matching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyLink = async (linkId: number) => {
    try {
      // Update local state optimistically
      setLinkedEmails(links =>
        links.map(link =>
          link.id === linkId
            ? { ...link, is_verified: true, verified_at: new Date().toISOString() }
            : link
        )
      );
      
      // TODO: Make API call
      console.log(`Verifying link ${linkId}`);
    } catch (error) {
      console.error('Error verifying link:', error);
    }
  };

  const handleRejectLink = async (linkId: number) => {
    try {
      setLinkedEmails(links => links.filter(link => link.id !== linkId));
      console.log(`Rejecting link ${linkId}`);
    } catch (error) {
      console.error('Error rejecting link:', error);
    }
  };

  const handleBulkVerify = async () => {
    if (selectedLinks.size === 0) return;
    
    setBulkProcessing(true);
    try {
      const linkIds = Array.from(selectedLinks);
      
      // Update all selected links
      setLinkedEmails(links =>
        links.map(link =>
          linkIds.includes(link.id)
            ? { ...link, is_verified: true, verified_at: new Date().toISOString() }
            : link
        )
      );
      
      setSelectedLinks(new Set());
      console.log(`Bulk verified ${linkIds.length} links`);
    } catch (error) {
      console.error('Error in bulk verify:', error);
    } finally {
      setBulkProcessing(false);
    }
  };

  const handleBulkReject = async () => {
    if (selectedLinks.size === 0) return;
    
    setBulkProcessing(true);
    try {
      const linkIds = Array.from(selectedLinks);
      setLinkedEmails(links => links.filter(link => !linkIds.includes(link.id)));
      setSelectedLinks(new Set());
      console.log(`Bulk rejected ${linkIds.length} links`);
    } catch (error) {
      console.error('Error in bulk reject:', error);
    } finally {
      setBulkProcessing(false);
    }
  };

  const handleAcceptSuggestion = async (suggestion: MatchSuggestion) => {
    try {
      // Remove from suggestions
      setSuggestions(prev => prev.filter(s => s.email_id !== suggestion.email_id));
      
      // Add to linked emails
      const newLink: EmailJobLink = {
        id: Date.now(), // Temporary ID
        email_id: suggestion.email_id,
        job_id: suggestion.job_id,
        confidence_score: suggestion.confidence_score,
        match_methods: suggestion.match_methods,
        match_details: {},
        match_explanation: suggestion.match_explanation,
        link_type: "manual",
        created_at: new Date().toISOString(),
        created_by: "user",
        is_verified: false,
        is_rejected: false,
        updated_at: new Date().toISOString()
      };
      
      setLinkedEmails(prev => [newLink, ...prev]);
      console.log(`Accepted suggestion: ${suggestion.email_id} → job ${suggestion.job_id}`);
    } catch (error) {
      console.error('Error accepting suggestion:', error);
    }
  };

  const handleRejectSuggestion = (emailId: string) => {
    setSuggestions(prev => prev.filter(s => s.email_id !== emailId));
    console.log(`Rejected suggestion: ${emailId}`);
  };

  const handleBulkMatching = async () => {
    setBulkProcessing(true);
    try {
      // TODO: Make API call for bulk matching
      const result: BulkMatchingResult = {
        jobs_processed: 25,
        matches_found: 8,
        auto_linked: 3,
        suggestions_created: 5,
        errors: []
      };
      
      await loadMatchingData(); // Refresh data
      console.log('Bulk matching result:', result);
    } catch (error) {
      console.error('Error in bulk matching:', error);
    } finally {
      setBulkProcessing(false);
    }
  };

  const getConfidenceColor = (score: number): string => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 75) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    if (score >= 40) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceLabel = (score: number): string => {
    if (score >= 90) return 'Very High';
    if (score >= 75) return 'High';
    if (score >= 60) return 'Medium';
    if (score >= 40) return 'Low';
    return 'Very Low';
  };

  const handleSelectLink = (linkId: number) => {
    setSelectedLinks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(linkId)) {
        newSet.delete(linkId);
      } else {
        newSet.add(linkId);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedLinks.size === linkedEmails.length) {
      setSelectedLinks(new Set());
    } else {
      setSelectedLinks(new Set(linkedEmails.map(link => link.id)));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading email-job matching data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Email-Job Matching</h1>
          <p className="text-gray-600 mt-1">
            Manage links between job applications and email communications
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => loadMatchingData()}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          <button
            onClick={handleBulkMatching}
            disabled={bulkProcessing}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <Zap className="w-4 h-4 mr-2" />
            {bulkProcessing ? 'Processing...' : 'Run Bulk Matching'}
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'links', label: `Linked Emails (${linkedEmails.length})`, icon: Link },
            { id: 'suggestions', label: `Suggestions (${suggestions.length})`, icon: Mail },
            { id: 'statistics', label: 'Statistics', icon: BarChart3 }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'links' && (
        <div>
          {/* Bulk Actions */}
          {selectedLinks.size > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-blue-900">
                  {selectedLinks.size} email{selectedLinks.size !== 1 ? 's' : ''} selected
                </span>
                <div className="flex space-x-2">
                  <button
                    onClick={handleBulkVerify}
                    disabled={bulkProcessing}
                    className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
                  >
                    Verify All
                  </button>
                  <button
                    onClick={handleBulkReject}
                    disabled={bulkProcessing}
                    className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 disabled:opacity-50"
                  >
                    Reject All
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Linked Emails List */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">
                  Email-Job Links ({linkedEmails.length})
                </h3>
                <div className="flex items-center space-x-4">
                  <label className="flex items-center text-sm">
                    <input
                      type="checkbox"
                      checked={selectedLinks.size === linkedEmails.length}
                      onChange={handleSelectAll}
                      className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    Select All
                  </label>
                </div>
              </div>
            </div>

            <div className="divide-y divide-gray-200">
              {linkedEmails.length === 0 ? (
                <div className="text-center py-12">
                  <Link className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No email links</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    No emails have been linked to job applications yet.
                  </p>
                </div>
              ) : (
                linkedEmails.map((link) => (
                  <div key={link.id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-start space-x-4">
                      <input
                        type="checkbox"
                        checked={selectedLinks.has(link.id)}
                        onChange={() => handleSelectLink(link.id)}
                        className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900">
                              Email {link.email_id} ↔ Job {link.job_id}
                            </h4>
                            <p className="text-sm text-gray-600 mt-1">
                              {link.match_explanation}
                            </p>
                            <div className="flex flex-wrap gap-1 mt-2">
                              {link.match_methods.map((method) => (
                                <span key={method} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">
                                  {method.replace('_', ' ')}
                                </span>
                              ))}
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2 ml-4">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              getConfidenceColor(link.confidence_score)
                            }`}>
                              {link.confidence_score.toFixed(1)}% {getConfidenceLabel(link.confidence_score)}
                            </span>
                            
                            {link.is_verified ? (
                              <span className="inline-flex items-center text-green-600">
                                <CheckCircle className="w-4 h-4 mr-1" />
                                <span className="text-xs">Verified</span>
                              </span>
                            ) : (
                              <div className="flex space-x-1">
                                <button
                                  onClick={() => handleVerifyLink(link.id)}
                                  className="p-1 text-green-600 hover:bg-green-50 rounded"
                                  title="Verify link"
                                >
                                  <CheckCircle className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => handleRejectLink(link.id)}
                                  className="p-1 text-red-600 hover:bg-red-50 rounded"
                                  title="Reject link"
                                >
                                  <X className="w-4 h-4" />
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                        
                        <div className="mt-2 text-xs text-gray-500 flex items-center space-x-4">
                          <span>Type: {link.link_type}</span>
                          <span>Created: {new Date(link.created_at).toLocaleDateString()}</span>
                          <span>By: {link.created_by}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'suggestions' && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Match Suggestions ({suggestions.length})
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Review potential matches between emails and job applications
            </p>
          </div>

          <div className="divide-y divide-gray-200">
            {suggestions.length === 0 ? (
              <div className="text-center py-12">
                <Mail className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No suggestions</h3>
                <p className="mt-1 text-sm text-gray-500">
                  No potential matches found. Try running bulk matching to find new suggestions.
                </p>
              </div>
            ) : (
              suggestions.map((suggestion) => (
                <div key={suggestion.email_id} className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-900 mb-1">
                        {suggestion.email_details.subject}
                      </h4>
                      <p className="text-sm text-gray-600 mb-2">
                        From: {suggestion.email_details.sender} → Job {suggestion.job_id}
                      </p>
                      <p className="text-sm text-gray-700 mb-3">
                        {suggestion.match_explanation}
                      </p>
                      
                      <div className="flex flex-wrap gap-1">
                        {suggestion.match_methods.map((method) => (
                          <span key={method} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-yellow-100 text-yellow-800">
                            {method.replace('_', ' ')}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex flex-col items-end space-y-2 ml-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        getConfidenceColor(suggestion.confidence_score)
                      }`}>
                        {suggestion.confidence_score.toFixed(1)}% {getConfidenceLabel(suggestion.confidence_score)}
                      </span>
                      
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleAcceptSuggestion(suggestion)}
                          className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => handleRejectSuggestion(suggestion.email_id)}
                          className="px-3 py-1 bg-gray-600 text-white text-xs rounded hover:bg-gray-700"
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === 'statistics' && statistics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Overview Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Overview</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Links:</span>
                <span className="text-sm font-medium text-gray-900">{statistics.totals.total_links}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Verified Links:</span>
                <span className="text-sm font-medium text-green-600">{statistics.totals.verified_links}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Auto Links:</span>
                <span className="text-sm font-medium text-blue-600">{statistics.totals.auto_links}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Manual Links:</span>
                <span className="text-sm font-medium text-purple-600">{statistics.totals.manual_links}</span>
              </div>
            </div>
          </div>

          {/* Quality Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quality Metrics</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Verification Rate:</span>
                <span className="text-sm font-medium text-gray-900">{statistics.rates.verification_rate}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Average Confidence:</span>
                <span className="text-sm font-medium text-gray-900">{statistics.quality_metrics.average_confidence}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">High Confidence:</span>
                <span className="text-sm font-medium text-gray-900">{statistics.quality_metrics.high_confidence_percentage}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Auto Link Rate:</span>
                <span className="text-sm font-medium text-gray-900">{statistics.rates.auto_link_rate}%</span>
              </div>
            </div>
          </div>

          {/* Confidence Distribution */}
          <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Confidence Distribution</h3>
            <div className="grid grid-cols-5 gap-4">
              {Object.entries(statistics.confidence_distribution).map(([level, count]) => (
                <div key={level} className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{count}</div>
                  <div className="text-xs text-gray-600 capitalize">{level.replace('_', ' ')}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailJobMatching;