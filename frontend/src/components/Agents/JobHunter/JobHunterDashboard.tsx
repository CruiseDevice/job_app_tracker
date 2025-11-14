// FILE: frontend/src/components/Agents/JobHunter/JobHunterDashboard.tsx

import React, { useState } from 'react';
import JobCard from './JobCard';
import JobFilters from './JobFilters';
import { Loader2, Search, Briefcase } from 'lucide-react';

interface JobFiltersType {
  keywords: string;
  location: string;
  platforms: string[];
  experienceLevel: string;
  jobType: string;
  salaryMin: number;
}

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

const JobHunterDashboard: React.FC = () => {
  const [filters, setFilters] = useState<JobFiltersType>({
    keywords: '',
    location: '',
    platforms: ['LinkedIn', 'Indeed', 'Glassdoor'],
    experienceLevel: '',
    jobType: '',
    salaryMin: 0
  });
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchMode, setSearchMode] = useState<'search' | 'recommendations'>('search');

  const handleSearch = async () => {
    if (!filters.keywords) {
      setError('Please enter job keywords');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/job-hunter/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keywords: filters.keywords,
          location: filters.location,
          platforms: filters.platforms,
          filters: {
            experience_level: filters.experienceLevel,
            job_type: filters.jobType,
            salary_min: filters.salaryMin
          }
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to search jobs');
      }

      const data = await response.json();

      // Parse jobs from analysis response
      // In production, the backend should return structured job data
      const mockJobs: Job[] = [
        {
          id: '1',
          platform: 'LinkedIn',
          title: `${filters.keywords} - Mid-Senior level`,
          company: 'Tech Company',
          location: filters.location || 'San Francisco, CA',
          salary_range: '$120K - $180K',
          posted_date: '2 days ago',
          description: data.analysis,
          match_score: 85,
          match_level: 'Excellent'
        },
        {
          id: '2',
          platform: 'Indeed',
          title: `${filters.keywords} Position`,
          company: 'Innovative Startup',
          location: filters.location || 'Remote',
          salary_range: '$130K - $190K',
          posted_date: '1 day ago',
          description: 'Great opportunity at a fast-growing startup.',
          match_score: 78,
          match_level: 'Good'
        },
        {
          id: '3',
          platform: 'Glassdoor',
          title: `Senior ${filters.keywords}`,
          company: 'Enterprise Corp',
          location: filters.location || 'New York, NY',
          salary_range: '$140K - $200K',
          posted_date: '3 days ago',
          description: 'Join our team at a well-established company.',
          match_score: 72,
          match_level: 'Good'
        }
      ];

      setJobs(mockJobs);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleGetRecommendations = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/agents/job-hunter/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 1,
          limit: 10
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get recommendations');
      }

      const data = await response.json();

      // Parse recommendations from analysis response
      const mockJobs: Job[] = [
        {
          id: 'rec-1',
          platform: 'LinkedIn',
          title: 'Software Engineer - Backend',
          company: 'Top Rated Tech Co',
          location: 'San Francisco, CA',
          salary_range: '$150K - $200K',
          posted_date: '1 day ago',
          description: 'Perfect match based on your profile and preferences.',
          match_score: 92,
          match_level: 'Excellent'
        },
        {
          id: 'rec-2',
          platform: 'Indeed',
          title: 'Full Stack Developer',
          company: 'Fast Growing Startup',
          location: 'Remote',
          salary_range: '$140K - $180K',
          posted_date: '2 days ago',
          description: 'Great culture and benefits matching your preferences.',
          match_score: 88,
          match_level: 'Excellent'
        }
      ];

      setJobs(mockJobs);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleSearch = () => {
    setFilters({
      keywords: 'Software Engineer',
      location: 'San Francisco, CA',
      platforms: ['LinkedIn', 'Indeed', 'Glassdoor'],
      experienceLevel: 'Mid-Senior level',
      jobType: 'Full-time',
      salaryMin: 120
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
          <div className="flex items-center gap-3 mb-2">
            <Briefcase className="h-8 w-8" />
            <h1 className="text-3xl font-bold">Job Hunter Agent</h1>
          </div>
          <p className="text-blue-100">
            AI-powered job search and personalized recommendations
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sidebar - Search Filters */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setSearchMode('search')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                  searchMode === 'search'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Search className="h-4 w-4 inline mr-2" />
                Search
              </button>
              <button
                onClick={() => setSearchMode('recommendations')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                  searchMode === 'recommendations'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Briefcase className="h-4 w-4 inline mr-2" />
                Recommendations
              </button>
            </div>

            {searchMode === 'search' ? (
              <>
                <JobFilters filters={filters} onChange={setFilters} />

                <div className="space-y-3 mt-6">
                  <button
                    onClick={handleSearch}
                    disabled={loading}
                    className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        Searching...
                      </>
                    ) : (
                      <>
                        <Search className="h-5 w-5" />
                        Search Jobs
                      </>
                    )}
                  </button>

                  <button
                    onClick={loadSampleSearch}
                    className="w-full bg-gray-200 text-gray-700 py-2 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                  >
                    Load Sample Search
                  </button>
                </div>
              </>
            ) : (
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">
                    Personalized Recommendations
                  </h3>
                  <p className="text-sm text-blue-700">
                    Get AI-curated job recommendations based on your profile, preferences, and past applications.
                  </p>
                </div>

                <button
                  onClick={handleGetRecommendations}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Getting Recommendations...
                    </>
                  ) : (
                    <>
                      <Briefcase className="h-5 w-5" />
                      Get Recommendations
                    </>
                  )}
                </button>
              </div>
            )}

            {error && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
          </div>
        </div>

        {/* Main Content - Job Results */}
        <div className="lg:col-span-2">
          {jobs.length === 0 && !loading && (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <Briefcase className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-600 mb-2">
                No jobs yet
              </h3>
              <p className="text-gray-500">
                {searchMode === 'search'
                  ? 'Use the search filters to find jobs that match your criteria'
                  : 'Click "Get Recommendations" to see personalized job matches'}
              </p>
            </div>
          )}

          {loading && (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <Loader2 className="h-16 w-16 text-blue-600 mx-auto mb-4 animate-spin" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                {searchMode === 'search' ? 'Searching jobs...' : 'Generating recommendations...'}
              </h3>
              <p className="text-gray-500">
                AI is analyzing job postings and matching them to your preferences
              </p>
            </div>
          )}

          {jobs.length > 0 && !loading && (
            <div className="space-y-4">
              <div className="bg-white rounded-lg shadow-md p-4 mb-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-800">
                    Found {jobs.length} job{jobs.length !== 1 ? 's' : ''}
                  </h2>
                  <div className="text-sm text-gray-600">
                    Sorted by match score
                  </div>
                </div>
              </div>

              {jobs.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobHunterDashboard;
