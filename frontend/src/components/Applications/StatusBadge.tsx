// FILE: frontend/src/components/Applications/StatusBadge.tsx

import React from 'react';
import type { ApplicationStatus } from '../../types/application';

interface StatusBadgeProps {
  status: ApplicationStatus;
  size?: 'sm' | 'md' | 'lg';
  clickable?: boolean;
  onClick?: () => void;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  clickable = false,
  onClick
}) => {
  const getStatusConfig = (status: ApplicationStatus) => {
    switch (status) {
      case 'applied':
        return {
          text: 'Applied',
          className: 'bg-blue-100 text-blue-800 border-blue-200',
          icon: '📝'
        };
      case 'interview':
        return {
          text: 'Interview',
          className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          icon: '🗣️'
        };
      case 'assessment':
        return {
          text: 'Assessment',
          className: 'bg-purple-100 text-purple-800 border-purple-200',
          icon: '📋'
        };
      case 'rejected':
        return {
          text: 'Rejected',
          className: 'bg-red-100 text-red-800 border-red-200',
          icon: '❌'
        };
      case 'offer':
        return {
          text: 'Offer',
          className: 'bg-green-100 text-green-800 border-green-200',
          icon: '🎉'
        };
      default:
        return {
          text: 'Unknown',
          className: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '❓'
        };
    }
  };

  const getSizeClasses = (size: 'sm' | 'md' | 'lg') => {
    switch (size) {
      case 'sm':
        return 'px-2 py-0.5 text-xs';
      case 'md':
        return 'px-2.5 py-1 text-sm';
      case 'lg':
        return 'px-3 py-1.5 text-base';
      default:
        return 'px-2.5 py-1 text-sm';
    }
  };

  const config = getStatusConfig(status);
  const sizeClasses = getSizeClasses(size);
  
  const baseClasses = `inline-flex items-center rounded-full font-medium border ${sizeClasses} ${config.className}`;
  const interactiveClasses = clickable 
    ? 'cursor-pointer hover:shadow-sm transition-shadow' 
    : '';

  return (
    <span
      className={`${baseClasses} ${interactiveClasses}`}
      onClick={clickable ? onClick : undefined}
      title={clickable ? 'Click to change status' : undefined}
    >
      <span className="mr-1" role="img" aria-label={config.text}>
        {config.icon}
      </span>
      {config.text}
    </span>
  );
};

export default StatusBadge;