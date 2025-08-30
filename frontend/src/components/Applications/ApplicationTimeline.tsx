// frontend/src/components/Applications/ApplicationTimeline.tsx

import React, { useState, useEffect } from 'react';
import { 
  X, Clock, Mail, Calendar, ExternalLink, TrendingUp, 
  AlertCircle, CheckCircle, FileText, User 
} from 'lucide-react';

interface TimelineEvent {
  date: string;
  event: string;
  status?: string;
  description?: string;
  source: 'application' | 'email' | 'manual' | 'system';
  confidence?: number;
}

interface ApplicationTimelineProps {
  applicationId: number;
  isOpen: boolean;
  onClose: () => void;
  application?: any;
}

export const ApplicationTimeline: React.FC<ApplicationTimelineProps> = ({
  applicationId,
  isOpen,
  onClose,
  application
}) => {
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && applicationId) {
      fetchApplicationHistory();
    }
  }, [isOpen, applicationId]);

  const fetchApplicationHistory = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/applications/${applicationId}/history`);
      if (!response.ok) throw new Error('Failed to fetch history');
      
      const data = await response.json();
      setTimeline(data.timeline || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load timeline');
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (event: TimelineEvent) => {
    switch (event.source) {
      case 'email':
        return <Mail className="w-5 h-5 text-blue-500" />;
      case 'application':
        return <FileText className="w-5 h-5 text-green-500" />;
      case 'manual':
        return <User className="w-5 h-5 text-purple-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'applied': return <Mail className="w-4 h-4" />;
      case 'assessment': return <FileText className="w-4 h-4" />;
      case 'interview': return <Calendar className="w-4 h-4" />;
      case 'offer': return <TrendingUp className="w-4 h-4" />;
      case 'accepted': return <CheckCircle className="w-4 h-4" />;
      case 'rejected': return <AlertCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      }),
      time: date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })
    };
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-2xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Application Timeline
            </h2>
            {application && (
              <p className="text-gray-600">
                {application.position} at {application.company}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <span className="ml-3 text-gray-600">Loading timeline...</span>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
              <p className="text-red-600">{error}</p>
              <button
                onClick={fetchApplicationHistory}
                className="mt-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
              >
                Retry
              </button>
            </div>
          ) : timeline.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No timeline events found</p>
            </div>
          ) : (
            <div className="space-y-6">
              {timeline.map((event, index) => {
                const { date, time } = formatDate(event.date);
                const isLast = index === timeline.length - 1;
                
                return (
                  <div key={index} className="relative">
                    {/* Vertical Line */}
                    {!isLast && (
                      <div className="absolute left-6 top-12 w-px h-16 bg-gray-200"></div>
                    )}
                    
                    <div className="flex gap-4">
                      {/* Icon */}
                      <div className="flex-shrink-0 w-12 h-12 bg-white border-2 border-gray-200 rounded-full flex items-center justify-center">
                        {getEventIcon(event)}
                      </div>
                      
                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="text-sm font-medium text-gray-900">
                              {event.event}
                            </h4>
                            
                            {event.status && (
                              <div className="flex items-center gap-2 mt-1">
                                {getStatusIcon(event.status)}
                                <span className="text-sm text-gray-600 capitalize">
                                  Status: {event.status}
                                </span>
                              </div>
                            )}
                            
                            {event.description && (
                              <p className="text-sm text-gray-600 mt-1">
                                {event.description}
                              </p>
                            )}
                            
                            {event.confidence && event.confidence < 100 && (
                              <div className="flex items-center gap-1 mt-1">
                                <span className="text-xs text-gray-500">
                                  Confidence: {event.confidence.toFixed(1)}%
                                </span>
                              </div>
                            )}
                          </div>
                          
                          {/* Date/Time */}
                          <div className="text-right text-xs text-gray-500 ml-4">
                            <div className="font-medium">{date}</div>
                            <div>{time}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer with Application Summary */}
        {application && (
          <div className="border-t p-6 bg-gray-50">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Applied:</span>
                <div className="font-medium">
                  {formatDate(application.application_date).date}
                </div>
              </div>
              
              <div>
                <span className="text-gray-500">Current Status:</span>
                <div className="font-medium capitalize">
                  {application.status}
                </div>
              </div>
              
              {application.interview_date && (
                <div>
                  <span className="text-gray-500">Interview:</span>
                  <div className="font-medium">
                    {formatDate(application.interview_date).date}
                  </div>
                </div>
              )}
              
              <div>
                <span className="text-gray-500">Days Since Applied:</span>
                <div className="font-medium">
                  {Math.floor((new Date().getTime() - new Date(application.application_date).getTime()) / (1000 * 60 * 60 * 24))}
                </div>
              </div>
            </div>
            
            {application.notes && (
              <div className="mt-4">
                <span className="text-gray-500 text-sm">Notes:</span>
                <div className="mt-1 text-sm text-gray-700 max-h-20 overflow-y-auto">
                  {application.notes}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};