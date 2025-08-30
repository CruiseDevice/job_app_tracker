// frontend/src/components/Applications/ApplicationsDashboard.tsx

import React, { useState, useEffect } from 'react';
import { Search, Filter, RotateCcw, AlertTriangle, CheckCircle } from 'lucide-react';
import { JobApplicationCard } from './JobApplicationCard';
import { ApplicationTimeline } from './ApplicationTimeline';
import { useAppDispatch, useAppSelector } from '../../hooks';

interface ApplicationsDashboardProps {
  onStatusUpdate?: (id: number, status: string, notes?: string) => void;
}

export const ApplicationsDashboard: React.FC<ApplicationsDashboardProps> = ({
  onStatusUpdate
}) => {
  const dispatch = useAppDispatch();
  const { applications, loading, statistics } = useAppSelector(state => state.applications);
  
  // Local state
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [showTimeline, setShowTimeline] = useState(false);
  const [selectedApplicationId, setSelectedApplicationId] = useState<number | null>(null);
  const [duplicatesFound, setDuplicatesFound] = useState<any[]>([]);
  const [showDuplicates, setShowDuplicates] = useState(false);

  useEffect(() => {
    // Load applications and check for duplicates on mount
    loadApplications();
    checkForDuplicates();
  }, []);

  const loadApplications = async () => {
    try {
      // Fetch applications with your existing Redux action
      // dispatch(fetchApplications());
    } catch (error) {
      console.error('Failed to load applications:', error);
    }
  };

  const checkForDuplicates = async () => {
    try {
      const response = await fetch('/api/applications/duplicates');
      const data = await response.json();
      
      if (data.success && data.duplicate_groups.length > 0) {
        setDuplicatesFound(data.duplicate_groups);
        console.log(`Found ${data.duplicate_groups.length} potential duplicate groups`);
      }
    } catch (error) {
      console.error('Failed to check for duplicates:', error);
    }
  };

  const handleStatusUpdate = async (id: number, status: string, notes?: string) => {
    try {
      const response = await fetch(`/api/applications/${id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, notes })
      });
      
      if (!response.ok) throw new Error('Failed to update status');
      
      const data = await response.json();
      console.log(`✅ Status updated: ${data.message}`);
      
      // Call parent callback if provided
      if (onStatusUpdate) {
        onStatusUpdate(id, status, notes);
      }
      
      // Reload applications to reflect changes
      loadApplications();
      
    } catch (error) {
      console.error('Failed to update application status:', error);
      alert('Failed to update application status. Please try again.');
    }
  };

  const handleViewHistory = (id: number) => {
    setSelectedApplicationId(id);
    setShowTimeline(true);
  };

  const handleMergeDuplicates = async (primaryId: number, duplicateIds: number[]) => {
    try {
      const response = await fetch('/api/applications/merge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          primary_application_id: primaryId,
          duplicate_application_ids: duplicateIds
        })
      });
      
      if (!response.ok) throw new Error('Failed to merge applications');
      
      const data = await response.json();
      console.log(`✅ Merged applications: ${data.message}`);
      
      // Refresh data
      loadApplications();
      checkForDuplicates();
      
    } catch (error) {
      console.error('Failed to merge applications:', error);
      alert('Failed to merge duplicate applications. Please try again.');
    }
  };

  // Filter and sort applications
  const filteredApplications = applications
    .filter(app => {
      // Search filter
      if (searchTerm) {
        const search = searchTerm.toLowerCase();
        return (
          app.company.toLowerCase().includes(search) ||
          app.position.toLowerCase().includes(search) ||
          (app.location && app.location.toLowerCase().includes(search))
        );
      }
      return true;
    })
    .filter(app => {
      // Status filter
      if (statusFilter === 'all') return true;
      if (statusFilter === 'active') return !['rejected', 'withdrawn', 'accepted'].includes(app.status);
      return app.status === statusFilter;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.application_date).getTime() - new Date(a.application_date).getTime();
        case 'company':
          return a.company.localeCompare(b.company);
        case 'status':
          return a.status.localeCompare(b.status);
        default:
          return 0;
      }
    });

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Job Applications</h1>
        
        {/* Status Overview */}
        <div className="flex gap-4 text-sm">
          <div className="text-center">
            <div className="font-semibold text-blue-600">{statistics?.thisMonth || 0}</div>
            <div className="text-gray-500">This Month</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-green-600">{statistics?.byStatus?.interview || 0}</div>
            <div className="text-gray-500">Interviews</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-purple-600">{statistics?.byStatus?.offer || 0}</div>
            <div className="text-gray-500">Offers</div>
          </div>
        </div>
      </div>

      {/* Duplicates Alert */}
      {duplicatesFound.length > 0 && !showDuplicates && (
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
              <span className="font-medium text-yellow-800">
                {duplicatesFound.length} duplicate application group(s) detected
              </span>
            </div>
            <button
              onClick={() => setShowDuplicates(true)}
              className="px-3 py-1 bg-yellow-200 text-yellow-800 rounded-md hover:bg-yellow-300 text-sm"
            >
              Review Duplicates
            </button>
          </div>
        </div>
      )}

      {/* Duplicates Management */}
      {showDuplicates && (
        <div className="mb-6 p-4 bg-white border border-gray-200 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900">Duplicate Applications</h3>
            <button
              onClick={() => setShowDuplicates(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {duplicatesFound.map((group, index) => (
            <div key={index} className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
              <h4 className="font-medium text-red-900 mb-2">
                {group.company} - {group.position} ({group.count} duplicates)
              </h4>
              
              <div className="space-y-2">
                {group.applications.map((app: any) => (
                  <div key={app.id} className="flex items-center justify-between p-2 bg-white rounded border">
                    <div className="text-sm">
                      <span className="font-medium">ID {app.id}</span>
                      <span className="text-gray-500 ml-2">
                        Applied: {new Date(app.application_date).toLocaleDateString()}
                      </span>
                      <span className="text-gray-500 ml-2 capitalize">
                        Status: {app.status}
                      </span>
                    </div>
                    <button
                      onClick={() => {
                        const otherIds = group.applications
                          .filter((other: any) => other.id !== app.id)
                          .map((other: any) => other.id);
                        handleMergeDuplicates(app.id, otherIds);
                      }}
                      className="px-2 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600"
                    >
                      Keep This One
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Filters and Search */}
      <div className="flex gap-4 mb-6">
        {/* Search */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search by company, position, or location..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="captured">Captured</option>
          <option value="applied">Applied</option>
          <option value="assessment">Assessment</option>
          <option value="interview">Interview</option>
          <option value="offer">Offer</option>
          <option value="accepted">Accepted</option>
          <option value="rejected">Rejected</option>
        </select>

        {/* Sort By */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2"
        >
          <option value="date">Date Applied</option>
          <option value="company">Company</option>
          <option value="status">Status</option>
        </select>

        {/* Refresh */}
        <button
          onClick={loadApplications}
          className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 flex items-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Results Summary */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-600">
          Showing {filteredApplications.length} of {applications.length} applications
        </p>
        
        {searchTerm && (
          <button
            onClick={() => setSearchTerm('')}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Clear search
          </button>
        )}
      </div>

      {/* Applications Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600">Loading applications...</span>
        </div>
      ) : filteredApplications.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">
            {searchTerm ? 'No applications match your search' : 'No job applications found'}
          </p>
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="mt-2 text-blue-600 hover:text-blue-800"
            >
              Clear search to see all applications
            </button>
          )}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredApplications.map(application => (
            <JobApplicationCard
              key={application.id}
              application={application}
              onStatusUpdate={handleStatusUpdate}
              onViewHistory={handleViewHistory}
            />
          ))}
        </div>
      )}

      {/* Application Timeline Modal */}
      <ApplicationTimeline
        applicationId={selectedApplicationId || 0}
        isOpen={showTimeline}
        onClose={() => {
          setShowTimeline(false);
          setSelectedApplicationId(null);
        }}
        application={applications.find(app => app.id === selectedApplicationId)}
      />

      {/* Success Messages for Email Matching */}
      <div className="fixed bottom-4 right-4 space-y-2">
        {/* These would be triggered by WebSocket events */}
        {/* Example success notification */}
        {false && ( // Replace with actual notification state
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="font-medium text-green-900">
                Email matched to existing application!
              </span>
            </div>
            <p className="text-sm text-green-700 mt-1">
              Interview email for "Software Engineer at Google" was automatically linked.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};