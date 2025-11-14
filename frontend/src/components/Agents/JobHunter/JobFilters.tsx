// FILE: frontend/src/components/Agents/JobHunter/JobFilters.tsx

import React from 'react';
import { Search, MapPin, DollarSign, Briefcase, Award } from 'lucide-react';

interface JobFiltersType {
  keywords: string;
  location: string;
  platforms: string[];
  experienceLevel: string;
  jobType: string;
  salaryMin: number;
}

interface JobFiltersProps {
  filters: JobFiltersType;
  onChange: (filters: JobFiltersType) => void;
}

const JobFilters: React.FC<JobFiltersProps> = ({ filters, onChange }) => {
  const handleChange = (field: keyof JobFiltersType, value: any) => {
    onChange({ ...filters, [field]: value });
  };

  const togglePlatform = (platform: string) => {
    const platforms = filters.platforms.includes(platform)
      ? filters.platforms.filter((p) => p !== platform)
      : [...filters.platforms, platform];
    handleChange('platforms', platforms);
  };

  return (
    <div className="space-y-4">
      {/* Keywords */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <Search className="h-4 w-4 inline mr-2" />
          Job Title / Keywords
        </label>
        <input
          type="text"
          value={filters.keywords}
          onChange={(e) => handleChange('keywords', e.target.value)}
          placeholder="e.g., Software Engineer"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Location */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <MapPin className="h-4 w-4 inline mr-2" />
          Location
        </label>
        <input
          type="text"
          value={filters.location}
          onChange={(e) => handleChange('location', e.target.value)}
          placeholder="e.g., San Francisco, CA or Remote"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Platforms */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Job Boards
        </label>
        <div className="space-y-2">
          {['LinkedIn', 'Indeed', 'Glassdoor'].map((platform) => (
            <label key={platform} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.platforms.includes(platform)}
                onChange={() => togglePlatform(platform)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{platform}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Experience Level */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <Award className="h-4 w-4 inline mr-2" />
          Experience Level
        </label>
        <select
          value={filters.experienceLevel}
          onChange={(e) => handleChange('experienceLevel', e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Any</option>
          <option value="Entry level">Entry level</option>
          <option value="Mid-Senior level">Mid-Senior level</option>
          <option value="Director">Director</option>
          <option value="Executive">Executive</option>
        </select>
      </div>

      {/* Job Type */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <Briefcase className="h-4 w-4 inline mr-2" />
          Job Type
        </label>
        <select
          value={filters.jobType}
          onChange={(e) => handleChange('jobType', e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Any</option>
          <option value="Full-time">Full-time</option>
          <option value="Part-time">Part-time</option>
          <option value="Contract">Contract</option>
          <option value="Internship">Internship</option>
        </select>
      </div>

      {/* Minimum Salary */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <DollarSign className="h-4 w-4 inline mr-2" />
          Minimum Salary (in thousands)
        </label>
        <input
          type="number"
          value={filters.salaryMin || ''}
          onChange={(e) => handleChange('salaryMin', parseInt(e.target.value) || 0)}
          placeholder="e.g., 120"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {filters.salaryMin > 0 && (
          <p className="text-xs text-gray-500 mt-1">
            ${filters.salaryMin}K+ per year
          </p>
        )}
      </div>
    </div>
  );
};

export default JobFilters;
