// FILE: frontend/src/components/Applications/ApplicationCard.tsx

import React, { useState } from 'react';
import { ExternalLink, Calendar, MapPin, DollarSign, Clock, MoreVertical, Edit, Trash2 } from 'lucide-react';
import type { JobApplication, ApplicationStatus } from '../../types/application';
import { useAppDispatch } from '../../hooks/useAppDispatch';
import { updateApplicationStatus } from '../../store/slices/applicationsSlice';
import StatusBadge from './StatusBadge';

interface ApplicationCardProps {
  application: JobApplication;
}

const ApplicationCard: React.FC<ApplicationCardProps> = ({ application }) => {
  const dispatch = useAppDispatch();
  const [showActions, setShowActions] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getTimeAgo = (dateString: string) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}d ago`;
    }
  };

  const handleStatusChange = async (newStatus: ApplicationStatus) => {
    setIsUpdating(true);
    try {
      await dispatch(updateApplicationStatus({
        id: application.id,
        status: newStatus
      })).unwrap();
    } catch (error) {
      console.error('Error updating status:', error);
      // TODO: Show error toast
    } finally {
      setIsUpdating(false);
    }
  };

  const handleEdit = () => {
    // TODO: Open edit modal
    console.log('Edit application', application.id);
    setShowActions(false);
  };

  const handleDelete = () => {
    // TODO: Show delete confirmation
    console.log('Delete application', application.id);
    setShowActions(false);
  };

  const statusOptions: ApplicationStatus[] = ['applied', 'interview', 'assessment', 'rejected', 'offer'];

  return (
    <div className="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200 overflow-hidden">
      {/* Header */}
      <div className="p-6 pb-4">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {application.position}
            </h3>
            <p className="text-base text-gray-600 mt-1">
              {application.company}
            </p>
          </div>
          
          <div className="flex items-center space-x-2 ml-4">
            {application.job_url && (
              <a
                href={application.job_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                title="View job posting"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
            
            <div className="relative">
              <button
                onClick={() => setShowActions(!showActions)}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <MoreVertical className="w-4 h-4" />
              </button>
              
              {showActions && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border border-gray-200">
                  <div className="py-1">
                    <button
                      onClick={handleEdit}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Edit
                    </button>
                    <button
                      onClick={handleDelete}
                      className="flex items-center w-full px-4 py-2 text-sm text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="mt-3">
          <div className="relative">
            <select
              value={application.status}
              onChange={(e) => handleStatusChange(e.target.value as ApplicationStatus)}
              disabled={isUpdating}
              className="appearance-none bg-transparent border-0 p-0 text-sm font-medium focus:outline-none cursor-pointer disabled:cursor-not-allowed"
              style={{
                color: 'inherit',
                background: 'transparent'
              }}
            >
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </option>
              ))}
            </select>
            <StatusBadge status={application.status} />
          </div>
        </div>
      </div>

      {/* Details */}
      <div className="px-6 pb-4">
        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
          <div className="flex items-center">
            <Calendar className="w-4 h-4 mr-1" />
            <span>Applied {formatDate(application.application_date)}</span>
          </div>
          
          {application.location && (
            <div className="flex items-center">
              <MapPin className="w-4 h-4 mr-1" />
              <span>{application.location}</span>
            </div>
          )}
          
          <div className="flex items-center">
            <Clock className="w-4 h-4 mr-1" />
            <span>{getTimeAgo(application.created_at)}</span>
          </div>
        </div>

        {application.salary_range && (
          <div className="mt-3">
            <div className="flex items-center text-sm">
              <DollarSign className="w-4 h-4 mr-1 text-green-600" />
              <span className="text-green-600 font-medium">{application.salary_range}</span>
            </div>
          </div>
        )}
      </div>

      {/* Description */}
      {application.job_description && (
        <div className="px-6 pb-4">
          <p className="text-sm text-gray-600 line-clamp-3">
            {application.job_description.length > 200
              ? `${application.job_description.substring(0, 200)}...`
              : application.job_description
            }
          </p>
        </div>
      )}

      {/* Notes */}
      {application.notes && (
        <div className="px-6 pb-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
            <p className="text-sm text-yellow-800">
              <strong>Notes:</strong> {application.notes}
            </p>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>ID: {application.id}</span>
          {application.email_sender && (
            <span>From: {application.email_sender}</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ApplicationCard;