// FILE: frontend/src/components/Applications/Applications.tsx

import React, { useEffect, useState } from 'react';
import { useAppDispatch } from '../../hooks/useAppDispatch';
import { useAppSelector } from '../../hooks/useAppSelector';
import { fetchApplications, setFilters } from '../../store/slices/applicationsSlice';
import type { ApplicationFilters } from '../../types/application';
import ApplicationCard from './ApplicationCard';
import Loading from '../common/Loading';
import { Search, Plus, Filter } from 'lucide-react';

const Applications: React.FC = () => {
  const dispatch = useAppDispatch();
  const { applications, loading, filters } = useAppSelector(state => state.applications);
  const [localFilters, setLocalFilters] = useState<ApplicationFilters>(filters);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    dispatch(fetchApplications(filters));
  }, [dispatch, filters]);

  const handleFiltersChange = (newFilters: ApplicationFilters) => {
    setLocalFilters(newFilters);
    dispatch(setFilters(newFilters));
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFilters = { ...localFilters, search: e.target.value };
    handleFiltersChange(newFilters);
  };

  const handleAddApplication = () => {
    // TODO: Open modal for adding manual application
    console.log('Add manual application');
  };

  if (loading) {
    return <Loading text="Loading applications..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Applications</h1>
          <p className="text-sm text-gray-600 mt-1">
            Manage and track your job applications
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex space-x-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 ${
              showFilters ? 'bg-gray-50' : ''
            }`}
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </button>
          <button
            onClick={handleAddApplication}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Application
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Search applications..."
          value={localFilters.search || ''}
          onChange={handleSearchChange}
        />
      </div>

      {/* Filters */}
      {showFilters && (
        <ApplicationFilters 
          filters={localFilters} 
          onChange={handleFiltersChange} 
        />
      )}

      {/* Results Summary */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-700">
          Showing <span className="font-medium">{applications.length}</span> applications
        </p>
        
        {Object.keys(filters).length > 0 && (
          <button
            onClick={() => handleFiltersChange({})}
            className="text-sm text-blue-600 hover:text-blue-500"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Applications Grid */}
      {applications.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto h-24 w-24 text-gray-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No applications found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {Object.keys(filters).length > 0 
              ? 'Try adjusting your filters or search terms.'
              : 'Get started by adding your first application.'
            }
          </p>
          <div className="mt-6">
            <button
              onClick={handleAddApplication}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Application
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {applications.map((application) => (
            <ApplicationCard 
              key={application.id} 
              application={application} 
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Applications;