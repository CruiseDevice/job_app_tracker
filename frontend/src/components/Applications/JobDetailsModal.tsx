import React, { useState, useEffect } from 'react';
import { X, Mail, Link, ExternalLink, Calendar, MapPin, DollarSign, AlertCircle, CheckCircle, Clock, Plus } from 'lucide-react';
import type { JobApplication } from '../../types/application';
import { EmailJobLink, MatchSuggestion } from '../../types/matching';

interface JobDetailsModalProps {
  application: JobApplication;
  isOpen: boolean;
  onClose: () => void;
}

interface LinkedEmail {
  email_id: string;
  subject: string;
  sender: string;
  date: string;
  link_info: EmailJobLink;
}

interface EmailJobMatchingAPI {
  getLinkedEmails: (jobId: number) => Promise<LinkedEmail[]>;
  getMatchSuggestions: (jobId: number) => Promise<MatchSuggestion[]>;
  createManualLink: (emailId: string, jobId: number) => Promise<void>;
  updateLink: (linkId: number, updates: any) => Promise<void>;
  deleteLink: (linkId: number) => Promise<void>;
}

// Mock API - replace with actual API calls
const mockEmailMatchingAPI: EmailJobMatchingAPI = {
  getLinkedEmails: async (jobId: number) => [
    {
      email_id: "email_1",
      subject: "Thank you for your application - Software Engineer",
      sender: "recruiting@google.com",
      date: "2024-12-20T10:30:00Z",
      link_info: {
        id: 1,
        email_id: "email_1",
        job_id: jobId,
        confidence_score: 95.5,
        match_methods: ["company_exact", "position_match", "domain_match"],
        match_explanation: "Company name exactly matches, job position mentioned, email domain matches company",
        link_type: "auto",
        is_verified: true,
        is_rejected: false,
        created_at: "2024-12-20T10:35:00Z"
      }
    },
    {
      email_id: "email_2", 
      subject: "Next steps in your application process",
      sender: "hr@google.com",
      date: "2024-12-21T14:15:00Z",
      link_info: {
        id: 2,
        email_id: "email_2",
        job_id: jobId,
        confidence_score: 87.2,
        match_methods: ["company_exact", "keyword_match"],
        match_explanation: "Company name exactly matches, job-related keywords found",
        link_type: "auto", 
        is_verified: false,
        is_rejected: false,
        created_at: "2024-12-21T14:20:00Z"
      }
    }
  ],
  
  getMatchSuggestions: async (jobId: number) => [
    {
      email_id: "email_3",
      job_id: jobId,
      confidence_score: 72.8,
      match_methods: ["company_fuzzy", "time_proximity"],
      match_explanation: "Company name closely matches, email and job close in time",
      email_details: {
        subject: "Interview scheduling - Engineering role",
        sender: "noreply@googl.com",
        date: "2024-12-22T09:00:00Z"
      },
      job_details: {},
      created_at: "2024-12-22T09:05:00Z",
      is_auto_linkable: false
    }
  ],

  createManualLink: async (emailId: string, jobId: number) => {
    console.log(`Creating manual link: ${emailId} → ${jobId}`);
  },

  updateLink: async (linkId: number, updates: any) => {
    console.log(`Updating link ${linkId}:`, updates);
  },

  deleteLink: async (linkId: number) => {
    console.log(`Deleting link ${linkId}`);
  }
};

const JobDetailsModal: React.FC<JobDetailsModalProps> = ({ 
  application, 
  isOpen, 
  onClose 
}) => {
  const [linkedEmails, setLinkedEmails] = useState<LinkedEmail[]>([]);
  const [matchSuggestions, setMatchSuggestions] = useState<MatchSuggestion[]>([]);
  const [activeTab, setActiveTab] = useState<'details' | 'emails' | 'suggestions'>('details');
  const [loading, setLoading] = useState(false);
  const [showLinkEmailForm, setShowLinkEmailForm] = useState(false);
  const [linkEmailId, setLinkEmailId] = useState('');

  useEffect(() => {
    if (isOpen && application) {
      loadEmailData();
    }
  }, [isOpen, application]);

  const loadEmailData = async () => {
    setLoading(true);
    try {
      const [emails, suggestions] = await Promise.all([
        mockEmailMatchingAPI.getLinkedEmails(application.id),
        mockEmailMatchingAPI.getMatchSuggestions(application.id)
      ]);
      setLinkedEmails(emails);
      setMatchSuggestions(suggestions);
    } catch (error) {
      console.error('Error loading email data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyLink = async (linkId: number) => {
    try {
      await mockEmailMatchingAPI.updateLink(linkId, { is_verified: true });
      setLinkedEmails(emails => 
        emails.map(email => 
          email.link_info.id === linkId 
            ? { ...email, link_info: { ...email.link_info, is_verified: true } }
            : email
        )
      );
    } catch (error) {
      console.error('Error verifying link:', error);
    }
  };

  const handleRejectLink = async (linkId: number) => {
    try {
      await mockEmailMatchingAPI.updateLink(linkId, { is_rejected: true });
      setLinkedEmails(emails => emails.filter(email => email.link_info.id !== linkId));
    } catch (error) {
      console.error('Error rejecting link:', error);
    }
  };

  const handleAcceptSuggestion = async (suggestion: MatchSuggestion) => {
    try {
      await mockEmailMatchingAPI.createManualLink(suggestion.email_id, suggestion.job_id);
      setMatchSuggestions(suggestions => 
        suggestions.filter(s => s.email_id !== suggestion.email_id)
      );
      await loadEmailData(); // Reload to show new link
    } catch (error) {
      console.error('Error accepting suggestion:', error);
    }
  };

  const handleRejectSuggestion = (suggestionEmailId: string) => {
    setMatchSuggestions(suggestions => 
      suggestions.filter(s => s.email_id !== suggestionEmailId)
    );
  };

  const handleManualLink = async () => {
    if (!linkEmailId.trim()) return;
    
    try {
      await mockEmailMatchingAPI.createManualLink(linkEmailId.trim(), application.id);
      setShowLinkEmailForm(false);
      setLinkEmailId('');
      await loadEmailData();
    } catch (error) {
      console.error('Error creating manual link:', error);
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 75) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    if (score >= 40) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 90) return 'Very High';
    if (score >= 75) return 'High';
    if (score >= 60) return 'Medium';
    if (score >= 40) return 'Low';
    return 'Very Low';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gray-50">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{application.position}</h2>
            <p className="text-gray-600">{application.company}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'details', label: 'Job Details', icon: ExternalLink },
              { id: 'emails', label: `Linked Emails (${linkedEmails.length})`, icon: Mail },
              { id: 'suggestions', label: `Suggestions (${matchSuggestions.length})`, icon: Link }
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

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'details' && (
            <div className="p-6 space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      application.status === 'captured' ? 'bg-blue-100 text-blue-800' :
                      application.status === 'applied' ? 'bg-green-100 text-green-800' :
                      application.status === 'interview' ? 'bg-yellow-100 text-yellow-800' :
                      application.status === 'offer' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {application.status.charAt(0).toUpperCase() + application.status.slice(1)}
                    </span>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Application Date</label>
                    <div className="flex items-center text-sm text-gray-900">
                      <Calendar className="w-4 h-4 mr-2 text-gray-400" />
                      {new Date(application.application_date).toLocaleDateString()}
                    </div>
                  </div>

                  {application.location && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                      <div className="flex items-center text-sm text-gray-900">
                        <MapPin className="w-4 h-4 mr-2 text-gray-400" />
                        {application.location}
                      </div>
                    </div>
                  )}

                  {application.salary_range && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Salary Range</label>
                      <div className="flex items-center text-sm text-gray-900">
                        <DollarSign className="w-4 h-4 mr-2 text-gray-400" />
                        {application.salary_range}
                      </div>
                    </div>
                  )}
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Source</label>
                    <span className="text-sm text-gray-900">
                      {application.is_extension_captured ? `Browser Extension (${application.job_board})` : 'Email Monitoring'}
                    </span>
                  </div>

                  {application.job_url && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Job URL</label>
                      <a
                        href={application.job_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-sm text-blue-600 hover:text-blue-500"
                      >
                        <ExternalLink className="w-4 h-4 mr-1" />
                        View Job Posting
                      </a>
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Created</label>
                    <span className="text-sm text-gray-500">
                      {new Date(application.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Description */}
              {application.job_description && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {application.job_description}
                    </p>
                  </div>
                </div>
              )}

              {/* Notes */}
              {application.notes && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-sm text-yellow-800">
                      {application.notes}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'emails' && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-medium text-gray-900">
                  Linked Emails ({linkedEmails.length})
                </h3>
                <button
                  onClick={() => setShowLinkEmailForm(true)}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Link Email
                </button>
              </div>

              {loading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="mt-2 text-sm text-gray-500">Loading linked emails...</p>
                </div>
              ) : linkedEmails.length === 0 ? (
                <div className="text-center py-8">
                  <Mail className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No linked emails</h3>
                  <p className="mt-1 text-sm text-gray-500">No emails have been linked to this job yet.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {linkedEmails.map((email) => (
                    <div key={email.email_id} className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900 mb-1">
                            {email.subject}
                          </h4>
                          <p className="text-sm text-gray-600 mb-2">
                            From: {email.sender}
                          </p>
                          <p className="text-xs text-gray-500">
                            {new Date(email.date).toLocaleString()}
                          </p>
                        </div>
                        
                        <div className="flex items-center space-x-2 ml-4">
                          {/* Confidence Score */}
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            getConfidenceColor(email.link_info.confidence_score)
                          }`}>
                            {email.link_info.confidence_score.toFixed(1)}% {getConfidenceLabel(email.link_info.confidence_score)}
                          </span>
                          
                          {/* Verification Status */}
                          {email.link_info.is_verified ? (
                            <span className="inline-flex items-center text-green-600">
                              <CheckCircle className="w-4 h-4" />
                            </span>
                          ) : (
                            <div className="flex space-x-1">
                              <button
                                onClick={() => handleVerifyLink(email.link_info.id)}
                                className="p-1 text-green-600 hover:bg-green-50 rounded"
                                title="Verify link"
                              >
                                <CheckCircle className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleRejectLink(email.link_info.id)}
                                className="p-1 text-red-600 hover:bg-red-50 rounded"
                                title="Reject link"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Match Details */}
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <p className="text-xs text-gray-500 mb-1">
                          <strong>Match reasons:</strong> {email.link_info.match_explanation}
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {email.link_info.match_methods.map((method) => (
                            <span key={method} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">
                              {method.replace('_', ' ')}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Manual Link Form */}
              {showLinkEmailForm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
                  <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Link Email Manually</h3>
                    <div className="mb-4">
                      <label htmlFor="emailId" className="block text-sm font-medium text-gray-700 mb-2">
                        Email ID
                      </label>
                      <input
                        type="text"
                        id="emailId"
                        value={linkEmailId}
                        onChange={(e) => setLinkEmailId(e.target.value)}
                        placeholder="Enter email ID or subject"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div className="flex justify-end space-x-3">
                      <button
                        onClick={() => setShowLinkEmailForm(false)}
                        className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleManualLink}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      >
                        Link Email
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'suggestions' && (
            <div className="p-6">
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Match Suggestions ({matchSuggestions.length})
                </h3>
                <p className="text-sm text-gray-600">
                  These emails might be related to this job application based on our analysis.
                </p>
              </div>

              {loading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="mt-2 text-sm text-gray-500">Finding suggestions...</p>
                </div>
              ) : matchSuggestions.length === 0 ? (
                <div className="text-center py-8">
                  <Link className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No suggestions</h3>
                  <p className="mt-1 text-sm text-gray-500">No potential email matches found for this job.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {matchSuggestions.map((suggestion) => (
                    <div key={suggestion.email_id} className="border border-yellow-200 bg-yellow-50 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900 mb-1">
                            {suggestion.email_details.subject}
                          </h4>
                          <p className="text-sm text-gray-600 mb-2">
                            From: {suggestion.email_details.sender}
                          </p>
                          <p className="text-xs text-gray-500 mb-3">
                            {new Date(suggestion.email_details.date).toLocaleString()}
                          </p>
                          
                          {/* Match Details */}
                          <div className="mb-3">
                            <p className="text-xs text-gray-600 mb-1">
                              <strong>Why this might match:</strong> {suggestion.match_explanation}
                            </p>
                            <div className="flex flex-wrap gap-1">
                              {suggestion.match_methods.map((method) => (
                                <span key={method} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-yellow-200 text-yellow-800">
                                  {method.replace('_', ' ')}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex flex-col items-end space-y-2 ml-4">
                          {/* Confidence Score */}
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            getConfidenceColor(suggestion.confidence_score)
                          }`}>
                            {suggestion.confidence_score.toFixed(1)}% {getConfidenceLabel(suggestion.confidence_score)}
                          </span>
                          
                          {/* Actions */}
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleAcceptSuggestion(suggestion)}
                              className="px-3 py-1 bg-green-600 text-white text-xs rounded-md hover:bg-green-700"
                            >
                              Accept
                            </button>
                            <button
                              onClick={() => handleRejectSuggestion(suggestion.email_id)}
                              className="px-3 py-1 bg-gray-600 text-white text-xs rounded-md hover:bg-gray-700"
                            >
                              Reject
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobDetailsModal;