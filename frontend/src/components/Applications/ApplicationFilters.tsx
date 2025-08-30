// FILE: frontend/src/components/Applications/ApplicationFilters.tsx

import React from 'react';
import { ApplicationFilters as FilterType, ApplicationStatus } from '../../types/application';

interface ApplicationFiltersProps {
  filters: FilterType;
  onChange: (filters: FilterType) => void;
}

const ApplicationFilters: React.FC<ApplicationFiltersProps> = ({
  filters,
  onChange
}) => {
  const statuses: ApplicationStatus[] = ['applied', 'interview', 'assessment', 'rejected', 'offer', 'screening'];

  const handleStatusChange = (status: ApplicationStatus) => {
    onChange({
      ...filters,
      status: filters.status === status ? undefined : status
    });
  };

  const handleCompanyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({
      ...filters,
      company: e.target.value || undefined
    });
  };

  const handleDateRangeChange = (field: 'start' | 'end', value: string) => {
    const dateRange = filters.dateRange || { start: '', end: '' };
    onChange({
      ...filters,
      dateRange: {
        ...dateRange,
        [field]: value
      }
    });
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Status
          </label>
          <div className="space-y-2">
            {statuses.map((status) => (
              <label key={status} className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.status === status}
                  onChange={() => handleStatusChange(status)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700 capitalize">
                  {status}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Company Filter */}
        <div>
          <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
            Company
          </label>
          <input
            type="text"
            id="company"
            value={filters.company || ''}
            onChange={handleCompanyChange}
            placeholder="Filter by company"
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>

        {/* Date Range Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Application Date
          </label>
          <div className="space-y-2">
            <input
              type="date"
              value={filters.dateRange?.start || ''}
              onChange={(e) => handleDateRangeChange('start', e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Start date"
            />
            <input
              type="date"
              value={filters.dateRange?.end || ''}
              onChange={(e) => handleDateRangeChange('end', e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="End date"
            />
          </div>
        </div>
      </div>

      {/* Active Filters Summary */}
      {(filters.status || filters.company || filters.dateRange) && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            {filters.status && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                Status: {filters.status}
                <button
                  onClick={() => onChange({ ...filters, status: undefined })}
                  className="ml-1 text-blue-600 hover:text-blue-500"
                >
                  ×
                </button>
              </span>
            )}
            
            {filters.company && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Company: {filters.company}
                <button
                  onClick={() => onChange({ ...filters, company: undefined })}
                  className="ml-1 text-green-600 hover:text-green-500"
                >
                  ×
                </button>
              </span>
            )}
            
            {filters.dateRange && (filters.dateRange.start || filters.dateRange.end) && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                Date: {filters.dateRange.start || '...'} to {filters.dateRange.end || '...'}
                <button
                  onClick={() => onChange({ ...filters, dateRange: undefined })}
                  className="ml-1 text-purple-600 hover:text-purple-500"
                >
                  ×
                </button>
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ApplicationFilters;