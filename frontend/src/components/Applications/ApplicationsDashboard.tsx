// frontend/src/components/Applications/ApplicationsDashboard.tsx

import React, { useState, useEffect, useCallback } from 'react';
import { Search, RotateCcw, AlertTriangle, X, FileText } from 'lucide-react';
import { JobApplicationCard } from './JobApplicationCard';
import { ApplicationTimeline } from './ApplicationTimeline';
import { Pagination } from '../common/Pagination';
import { useAppDispatch } from '../../hooks/useAppDispatch';
import { useAppSelector } from '../../hooks/useAppSelector';
import { fetchApplications, setPage, setPageSize } from '../../store/slices/applicationsSlice';
import { fetchStatistics } from '../../store/slices/statisticsSlice';
import type { JobApplication } from '../../types/application';
import type { RootState } from '../../store';

interface ApplicationsDashboardProps {
  onStatusUpdate?: (id: number, status: string, notes?: string) => void;
}

export const ApplicationsDashboard: React.FC<ApplicationsDashboardProps> = ({
  onStatusUpdate
}) => {
  const dispatch = useAppDispatch();
  const { applications, loading, pagination } = useAppSelector((state: RootState) => state.applications);
  const { stats: statistics } = useAppSelector((state: RootState) => state.statistics);
  
  // Local state
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showTimeline, setShowTimeline] = useState(false);
  const [selectedApplicationId, setSelectedApplicationId] = useState<number | null>(null);
  const [duplicatesFound, setDuplicatesFound] = useState<Array<{
    company: string;
    position: string;
    count: number;
    applications: JobApplication[];
  }>>([]);
  const [showDuplicates, setShowDuplicates] = useState(false);

  const loadApplications = useCallback(() => {
    try {
      const skip = (pagination.currentPage - 1) * pagination.pageSize;
      // Fetch applications with pagination parameters
      dispatch(fetchApplications({
        skip,
        limit: pagination.pageSize,
        status: statusFilter !== 'all' ? statusFilter as any : undefined,
        search: searchTerm || undefined,
      }));
      dispatch(fetchStatistics());
    } catch (error) {
      console.error('Failed to load applications:', error);
    }
  }, [dispatch, pagination.currentPage, pagination.pageSize, statusFilter, searchTerm]);

  useEffect(() => {
    // Load applications and check for duplicates when page or filters change
    loadApplications();
    checkForDuplicates();
  }, [loadApplications]);

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

  const handleDeleteApplication = async (id: number) => {
    try {
      const response = await fetch(`/api/applications/${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Failed to delete application');
      
      const data = await response.json();
      console.log(`✅ Application deleted: ${data.message}`);
      
      // Reload applications to reflect changes
      loadApplications();
      
    } catch (error) {
      console.error('Failed to delete application:', error);
      alert('Failed to delete application. Please try again.');
    }
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

  const handlePageChange = (page: number) => {
    dispatch(setPage(page));
  };

  const handlePageSizeChange = (pageSize: number) => {
    dispatch(setPageSize(pageSize));
  };

  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    // Reset to first page when search changes
    dispatch(setPage(1));
  };

  const handleStatusFilterChange = (value: string) => {
    setStatusFilter(value);
    // Reset to first page when filter changes
    dispatch(setPage(1));
  };

  // Calculate total pages
  const totalPages = Math.ceil(pagination.total / pagination.pageSize);

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
                {group.applications.map((app: JobApplication) => (
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
                          .filter((other: JobApplication) => other.id !== app.id)
                          .map((other: JobApplication) => other.id);
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
            onChange={(e) => handleSearchChange(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => handleStatusFilterChange(e.target.value)}
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
          {pagination.total > 0 ? (
            <>
              Showing {(pagination.currentPage - 1) * pagination.pageSize + 1} to{' '}
              {Math.min(pagination.currentPage * pagination.pageSize, pagination.total)} of{' '}
              {pagination.total} applications
            </>
          ) : (
            'No applications found'
          )}
        </p>
        
        {searchTerm && (
          <button
            onClick={() => handleSearchChange('')}
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
      ) : applications.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">
            {searchTerm ? 'No applications match your search' : 'No job applications found'}
          </p>
          {searchTerm && (
            <button
              onClick={() => handleSearchChange('')}
              className="mt-2 text-blue-600 hover:text-blue-800"
            >
              Clear search to see all applications
            </button>
          )}
        </div>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {applications.map((application: JobApplication) => (
              <JobApplicationCard
                key={application.id}
                application={application}
                onStatusUpdate={handleStatusUpdate}
                onViewHistory={handleViewHistory}
                onDelete={handleDeleteApplication}
              />
            ))}
          </div>

          {/* Pagination */}
          <Pagination
            currentPage={pagination.currentPage}
            totalPages={totalPages}
            totalItems={pagination.total}
            pageSize={pagination.pageSize}
            onPageChange={handlePageChange}
            onPageSizeChange={handlePageSizeChange}
          />
        </>
      )}

      {/* Application Timeline Modal */}
      <ApplicationTimeline
        applicationId={selectedApplicationId || 0}
        isOpen={showTimeline}
        onClose={() => {
          setShowTimeline(false);
          setSelectedApplicationId(null);
        }}
        application={applications.find((app: JobApplication) => app.id === selectedApplicationId)}
      />

      {/* Success Messages for Email Matching */}
      <div className="fixed bottom-4 right-4 space-y-2">
        {/* These would be triggered by WebSocket events */}
        {/* Example success notification */}
        {/* Replace with actual notification state when needed */}
        {/* Example notification - uncomment and connect to real state when needed
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
        */}
      </div>
    </div>
  );
};