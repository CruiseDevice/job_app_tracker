// frontend/src/components/Applications/JobApplicationCard.tsx

import React, { useState } from 'react';
import { Calendar, Mail, MapPin, ExternalLink, Clock, TrendingUp, AlertCircle } from 'lucide-react';
import { JobApplication } from '../../types/application';

interface JobApplicationCardProps {
  application: JobApplication;
  onStatusUpdate: (id: number, status: string, notes?: string) => void;
  onViewHistory: (id: number) => void;
}

const STATUS_COLORS = {
  captured: 'bg-gray-100 text-gray-800 border-gray-300',
  applied: 'bg-blue-100 text-blue-800 border-blue-300',
  assessment: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  interview: 'bg-purple-100 text-purple-800 border-purple-300',
  offer: 'bg-green-100 text-green-800 border-green-300',
  accepted: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  rejected: 'bg-red-100 text-red-800 border-red-300',
  withdrawn: 'bg-gray-100 text-gray-600 border-gray-300'
};

const STATUS_PROGRESSION = ['captured', 'applied', 'assessment', 'interview', 'offer', 'accepted'];
const FINAL_STATUSES = ['rejected', 'withdrawn', 'accepted'];

export const JobApplicationCard: React.FC<JobApplicationCardProps> = ({
  application,
  onStatusUpdate,
  onViewHistory
}) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [showStatusUpdate, setShowStatusUpdate] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState(application.status);
  const [updateNotes, setUpdateNotes] = useState('');

  const handleStatusUpdate = async () => {
    if (selectedStatus === application.status) return;
    
    setIsUpdating(true);
    try {
      await onStatusUpdate(application.id, selectedStatus, updateNotes || undefined);
      setShowStatusUpdate(false);
      setUpdateNotes('');
    } catch (error) {
      console.error('Failed to update status:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const getNextStatus = () => {
    const currentIndex = STATUS_PROGRESSION.indexOf(application.status);
    if (currentIndex >= 0 && currentIndex < STATUS_PROGRESSION.length - 1) {
      return STATUS_PROGRESSION[currentIndex + 1];
    }
    return null;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'captured': return <ExternalLink className="w-4 h-4" />;
      case 'applied': return <Mail className="w-4 h-4" />;
      case 'assessment': return <Clock className="w-4 h-4" />;
      case 'interview': return <Calendar className="w-4 h-4" />;
      case 'offer': return <TrendingUp className="w-4 h-4" />;
      case 'accepted': return <TrendingUp className="w-4 h-4" />;
      case 'rejected': return <AlertCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {application.position}
          </h3>
          <p className="text-gray-600 font-medium">{application.company}</p>
        </div>
        
        {/* Status Badge */}
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full border text-sm font-medium ${STATUS_COLORS[application.status] || STATUS_COLORS.applied}`}>
          {getStatusIcon(application.status)}
          <span className="capitalize">{application.status}</span>
        </div>
      </div>

      {/* Details */}
      <div className="space-y-2 mb-4">
        {application.location && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <MapPin className="w-4 h-4" />
            <span>{application.location}</span>
          </div>
        )}
        
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="w-4 h-4" />
          <span>Applied: {formatDate(application.application_date)}</span>
        </div>

        {application.salary_range && (
          <div className="text-sm text-gray-600">
            <strong>Salary:</strong> {application.salary_range}
          </div>
        )}
      </div>

      {/* Status Progression Indicator */}
      <div className="mb-4">
        <div className="flex items-center gap-1 mb-2">
          <span className="text-xs font-medium text-gray-500">PROGRESS</span>
        </div>
        <div className="flex items-center gap-2">
          {STATUS_PROGRESSION.map((status, index) => {
            const currentIndex = STATUS_PROGRESSION.indexOf(application.status);
            const isActive = index <= currentIndex;
            const isCurrent = status === application.status;
            
            return (
              <div key={status} className="flex items-center">
                <div className={`w-2 h-2 rounded-full ${
                  isCurrent 
                    ? 'bg-blue-500 ring-2 ring-blue-200' 
                    : isActive 
                      ? 'bg-green-500' 
                      : 'bg-gray-300'
                }`} />
                {index < STATUS_PROGRESSION.length - 1 && (
                  <div className={`w-8 h-px ${isActive ? 'bg-green-300' : 'bg-gray-200'}`} />
                )}
              </div>
            );
          })}
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>Captured</span>
          <span>Applied</span>
          <span>Assessment</span>
          <span>Interview</span>
          <span>Offer</span>
          <span>Accepted</span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        {!FINAL_STATUSES.includes(application.status) && (
          <>
            {/* Quick Next Status Button */}
            {getNextStatus() && (
              <button
                onClick={() => onStatusUpdate(application.id, getNextStatus()!)}
                disabled={isUpdating}
                className="px-3 py-2 bg-blue-500 text-white text-sm rounded-md hover:bg-blue-600 disabled:opacity-50"
              >
                Mark as {getNextStatus()?.charAt(0).toUpperCase() + getNextStatus()?.slice(1)}
              </button>
            )}
            
            {/* Custom Status Update */}
            <button
              onClick={() => setShowStatusUpdate(!showStatusUpdate)}
              className="px-3 py-2 border border-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-50"
            >
              Update Status
            </button>
          </>
        )}
        
        {/* View History */}
        <button
          onClick={() => onViewHistory(application.id)}
          className="px-3 py-2 border border-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-50"
        >
          View Timeline
        </button>
        
        {/* Job URL */}
        {application.job_url && (
          <a
            href={application.job_url}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-2 border border-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-50 inline-flex items-center gap-1"
          >
            <ExternalLink className="w-4 h-4" />
            View Job
          </a>
        )}
      </div>

      {/* Status Update Panel */}
      {showStatusUpdate && (
        <div className="mt-4 p-4 bg-gray-50 rounded-md border">
          <h4 className="font-medium text-gray-900 mb-3">Update Application Status</h4>
          
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Status
              </label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              >
                {STATUS_PROGRESSION.map(status => (
                  <option key={status} value={status}>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </option>
                ))}
                <option value="rejected">Rejected</option>
                <option value="withdrawn">Withdrawn</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes (Optional)
              </label>
              <textarea
                value={updateNotes}
                onChange={(e) => setUpdateNotes(e.target.value)}
                placeholder="Add any notes about this status change..."
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                rows={2}
              />
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={handleStatusUpdate}
                disabled={isUpdating || selectedStatus === application.status}
                className="px-4 py-2 bg-blue-500 text-white text-sm rounded-md hover:bg-blue-600 disabled:opacity-50"
              >
                {isUpdating ? 'Updating...' : 'Update Status'}
              </button>
              <button
                onClick={() => {
                  setShowStatusUpdate(false);
                  setSelectedStatus(application.status);
                  setUpdateNotes('');
                }}
                className="px-4 py-2 border border-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Recent Notes Preview */}
      {application.notes && (
        <div className="mt-4 p-3 bg-blue-50 rounded-md border border-blue-200">
          <h5 className="text-sm font-medium text-blue-900 mb-1">Latest Notes:</h5>
          <p className="text-sm text-blue-800 line-clamp-2">
            {application.notes.split('\n').slice(-3).join('\n')}
          </p>
        </div>
      )}
    </div>
  );
};