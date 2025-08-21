import React, { useEffect, useState } from 'react';
import { useAppSelector } from '../../hooks/useAppSelector';
import ApplicationCard from './ApplicationCard';


export const RealTimeApplicationList: React.FC = () => {
  const { applications, loading } = useAppSelector(state => state.applications);
  const [newApplicationIds, setNewApplicationIds] = useState<Set<number>>(new Set());

  // Track new applications for highlighting
  useEffect(() => {
    if (applications.length > 0) {
      const currentIds = new Set(applications.map(app => app.id));
      const newIds = new Set<number>();
      
      currentIds.forEach(id => {
        // If this is a new application (not in previous render)
        if (!newApplicationIds.has(id)) {
          newIds.add(id);
          // Remove highlight after 5 seconds
          setTimeout(() => {
            setNewApplicationIds(prev => {
              const updated = new Set(prev);
              updated.delete(id);
              return updated;
            });
          }, 5000);
        }
      });
      
      if (newIds.size > 0) {
        setNewApplicationIds(prev => new Set([...prev, ...newIds]));
      }
    }
  }, [applications, newApplicationIds]);

  const sortedApplications = [...applications].sort((a, b) => 
    new Date(b.application_date).getTime() - new Date(a.application_date).getTime()
  );

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="animate-pulse">
            <div className="bg-gray-200 h-48 rounded-lg"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Recent Applications</h2>
        <span className="text-sm text-gray-500">
          {applications.length} total applications
        </span>
      </div>

      {/* Applications Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedApplications.map((application) => (
          <div
            key={application.id}
            className={`transition-all duration-500 ${
              newApplicationIds.has(application.id)
                ? 'ring-2 ring-green-500 ring-opacity-75 animate-pulse'
                : ''
            }`}
          >
            <ApplicationCard 
              application={application}
            />
          </div>
        ))}
      </div>

      {/* Empty State */}
      {applications.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📋</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No applications yet</h3>
          <p className="text-gray-500 mb-6">
            Start email monitoring to automatically track your job applications
          </p>
        </div>
      )}
    </div>
  );
};