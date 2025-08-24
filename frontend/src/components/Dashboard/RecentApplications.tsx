// FILE: frontend/src/components/Dashboard/RecentApplications.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import { ExternalLink, Calendar, MapPin } from 'lucide-react';
import type { JobApplication } from '../../types/application';
import StatusBadge from '../Applications/StatusBadge';
import Loading from '../common/Loading';

interface RecentApplicationsProps {
  applications: JobApplication[];
  loading: boolean;
}

const RecentApplications: React.FC<RecentApplicationsProps> = ({
  applications,
  loading
}) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Applications</h2>
        </div>
        <div className="p-6">
          <Loading text="Loading applications..." />
        </div>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getTimeAgo = (dateString: string) => {
    const now = new Date();
    // Treat the dateString as UTC if no timezone is specified
    const date = new Date(dateString + (dateString.includes('Z') || dateString.includes('+') ? '' : 'Z'));
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

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-lg font-medium text-gray-900">Recent Applications</h2>
        <Link
          to="/applications"
          className="text-sm text-blue-600 hover:text-blue-500 font-medium"
        >
          View all
        </Link>
      </div>
      <div className="divide-y divide-gray-200">
        {applications.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-gray-500">No applications yet</p>
            <p className="text-sm text-gray-400 mt-1">
              Applications will appear here once the monitoring system detects them
            </p>
          </div>
        ) : (
          applications.map((application) => (
            <div key={application.id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-medium text-gray-900 truncate">
                      {application.position}
                    </h3>
                    <StatusBadge status={application.status} />
                  </div>
                  
                  <p className="text-base text-gray-600 mt-1">
                    {application.company}
                  </p>
                  
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
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
                    
                    <span className="text-gray-400">
                      {getTimeAgo(application.created_at)}
                    </span>
                  </div>

                  {application.salary_range && (
                    <div className="mt-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {application.salary_range}
                      </span>
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  {application.job_url && (
                    <a
                      href={application.job_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                      title="View job posting"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>

              {application.job_description && (
                <div className="mt-3">
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {application.job_description.length > 150
                      ? `${application.job_description.substring(0, 150)}...`
                      : application.job_description
                    }
                  </p>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default RecentApplications;