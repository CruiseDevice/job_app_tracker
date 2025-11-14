// FILE: frontend/src/components/Agents/JobHunter/JobCard.tsx

import React, { useState } from 'react';
import { MapPin, Building2, DollarSign, Clock, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import MatchScoreBadge from './MatchScoreBadge';
import CompanyResearch from './CompanyResearch';

interface Job {
  id: string;
  platform: string;
  title: string;
  company: string;
  location: string;
  salary_range: string;
  posted_date: string;
  description: string;
  match_score?: number;
  match_level?: string;
  company_research?: any;
}

interface JobCardProps {
  job: Job;
}

const JobCard: React.FC<JobCardProps> = ({ job }) => {
  const [expanded, setExpanded] = useState(false);
  const [showCompanyResearch, setShowCompanyResearch] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-start gap-3">
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {job.title}
                </h3>
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <Building2 className="h-4 w-4" />
                  <span className="font-medium">{job.company}</span>
                  <span className="text-gray-400">•</span>
                  <span className="text-sm text-gray-500">{job.platform}</span>
                </div>
              </div>
              {job.match_score !== undefined && (
                <MatchScoreBadge score={job.match_score} level={job.match_level} />
              )}
            </div>
          </div>
        </div>

        {/* Job Details */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="flex items-center gap-2 text-gray-600">
            <MapPin className="h-4 w-4 text-gray-400" />
            <span className="text-sm">{job.location}</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600">
            <DollarSign className="h-4 w-4 text-gray-400" />
            <span className="text-sm">{job.salary_range}</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600">
            <Clock className="h-4 w-4 text-gray-400" />
            <span className="text-sm">{job.posted_date}</span>
          </div>
        </div>

        {/* Description Preview */}
        <div className="mb-4">
          <p className="text-gray-700 text-sm line-clamp-2">
            {job.description}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            {expanded ? (
              <>
                <ChevronUp className="h-4 w-4" />
                Show Less
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4" />
                Show More
              </>
            )}
          </button>

          <button
            onClick={() => setShowCompanyResearch(!showCompanyResearch)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <Building2 className="h-4 w-4" />
            Company Research
          </button>

          <button
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors ml-auto"
          >
            <ExternalLink className="h-4 w-4" />
            View Job
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="border-t border-gray-200 p-6 bg-gray-50">
          <div className="mb-4">
            <h4 className="font-semibold text-gray-900 mb-2">Full Description</h4>
            <p className="text-gray-700 whitespace-pre-line">{job.description}</p>
          </div>

          {job.match_score !== undefined && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-900 mb-2">Why This Job Matches</h4>
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <p className="text-sm text-gray-700">
                  This job is a{' '}
                  <span className="font-semibold text-blue-600">
                    {job.match_score}% match
                  </span>{' '}
                  based on your preferences, skills, and experience level.
                </p>
                <div className="mt-3 space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500"></div>
                    <span className="text-sm text-gray-600">Matches your preferred role and experience level</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500"></div>
                    <span className="text-sm text-gray-600">Location aligns with your preferences</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500"></div>
                    <span className="text-sm text-gray-600">Salary range meets your expectations</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
              Save Job
            </button>
            <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Apply Now
            </button>
          </div>
        </div>
      )}

      {/* Company Research Panel */}
      {showCompanyResearch && (
        <div className="border-t border-gray-200 p-6 bg-gray-50">
          <CompanyResearch company={job.company} />
        </div>
      )}
    </div>
  );
};

export default JobCard;
