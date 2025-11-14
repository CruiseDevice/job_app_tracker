// FILE: frontend/src/components/Agents/FollowUp/FollowUpScheduleCard.tsx

import React, { useState } from 'react';

interface FollowUpItem {
  id: number;
  company: string;
  position: string;
  type: string;
  scheduledDate: string;
  status: 'scheduled' | 'sent' | 'responded' | 'overdue';
  priority: 'high' | 'medium' | 'low';
}

const FollowUpScheduleCard: React.FC = () => {
  const [filter, setFilter] = useState<'all' | 'scheduled' | 'overdue'>('all');

  // Sample follow-up schedule (in production, this would come from API)
  const followUps: FollowUpItem[] = [
    {
      id: 1,
      company: 'Google',
      position: 'Software Engineer',
      type: 'Initial Application',
      scheduledDate: '2025-11-15',
      status: 'overdue',
      priority: 'high'
    },
    {
      id: 2,
      company: 'Meta',
      position: 'Frontend Developer',
      type: 'Post-Interview Thank You',
      scheduledDate: '2025-11-16',
      status: 'scheduled',
      priority: 'high'
    },
    {
      id: 3,
      company: 'Amazon',
      position: 'Backend Engineer',
      type: 'Checking In',
      scheduledDate: '2025-11-18',
      status: 'scheduled',
      priority: 'medium'
    },
    {
      id: 4,
      company: 'Netflix',
      position: 'Full Stack Developer',
      type: 'Status Update',
      scheduledDate: '2025-11-14',
      status: 'sent',
      priority: 'medium'
    },
    {
      id: 5,
      company: 'Apple',
      position: 'iOS Developer',
      type: 'Initial Application',
      scheduledDate: '2025-11-20',
      status: 'scheduled',
      priority: 'low'
    }
  ];

  const filteredFollowUps = followUps.filter(f => {
    if (filter === 'all') return true;
    if (filter === 'scheduled') return f.status === 'scheduled';
    if (filter === 'overdue') return f.status === 'overdue';
    return true;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'overdue':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'scheduled':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'sent':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'responded':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Follow-up Schedule
        </h3>
        <p className="text-gray-600">
          View and manage all scheduled follow-ups
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All ({followUps.length})
        </button>
        <button
          onClick={() => setFilter('scheduled')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'scheduled'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Scheduled ({followUps.filter(f => f.status === 'scheduled').length})
        </button>
        <button
          onClick={() => setFilter('overdue')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'overdue'
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Overdue ({followUps.filter(f => f.status === 'overdue').length})
        </button>
      </div>

      {/* Schedule List */}
      <div className="space-y-3">
        {filteredFollowUps.map((followUp) => (
          <div
            key={followUp.id}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="font-semibold text-gray-900">
                    {followUp.company}
                  </h4>
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(followUp.status)}`}>
                    {followUp.status.charAt(0).toUpperCase() + followUp.status.slice(1)}
                  </span>
                  <span className={`text-sm font-medium ${getPriorityColor(followUp.priority)}`}>
                    {followUp.priority === 'high' ? '🔴' : followUp.priority === 'medium' ? '🟡' : '⚪'}
                  </span>
                </div>
                <div className="text-sm text-gray-600 mb-1">
                  {followUp.position}
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>📧 {followUp.type}</span>
                  <span>📅 {followUp.scheduledDate}</span>
                </div>
              </div>
              <div className="flex gap-2">
                {followUp.status === 'scheduled' || followUp.status === 'overdue' ? (
                  <>
                    <button className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors">
                      Send Now
                    </button>
                    <button className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300 transition-colors">
                      Edit
                    </button>
                  </>
                ) : (
                  <button className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded">
                    View
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredFollowUps.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="text-4xl mb-2">📭</div>
          <div className="text-gray-600">No follow-ups found</div>
        </div>
      )}

      {/* Add Follow-up Button */}
      <button className="w-full mt-6 bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition-colors">
        + Schedule New Follow-up
      </button>

      {/* Calendar View Toggle */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-semibold text-blue-900">Calendar View</div>
            <div className="text-sm text-blue-700">View follow-ups in a calendar layout</div>
          </div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Open Calendar
          </button>
        </div>
      </div>
    </div>
  );
};

export default FollowUpScheduleCard;
