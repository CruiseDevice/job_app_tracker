// FILE: frontend/src/components/Dashboard/StatisticsCard.tsx

import React from 'react';
import { Calendar, Clock, BarChart3, TrendingUp, TrendingDown } from 'lucide-react';

interface StatisticsCardProps {
  title: string;
  value: number;
  icon: 'calendar' | 'week' | 'month' | 'total';
  color: 'blue' | 'green' | 'purple' | 'orange';
  subtitle?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

const StatisticsCard: React.FC<StatisticsCardProps> = ({
  title,
  value,
  icon,
  color,
  subtitle,
  trend
}) => {
  const getIcon = () => {
    switch (icon) {
      case 'calendar':
        return <Calendar className="w-6 h-6" />;
      case 'week':
        return <Clock className="w-6 h-6" />;
      case 'month':
        return <BarChart3 className="w-6 h-6" />;
      case 'total':
        return <BarChart3 className="w-6 h-6" />;
      default:
        return <BarChart3 className="w-6 h-6" />;
    }
  };

  const getColorClasses = () => {
    switch (color) {
      case 'blue':
        return {
          bg: 'bg-blue-50',
          icon: 'text-blue-600',
          text: 'text-blue-600'
        };
      case 'green':
        return {
          bg: 'bg-green-50',
          icon: 'text-green-600',
          text: 'text-green-600'
        };
      case 'purple':
        return {
          bg: 'bg-purple-50',
          icon: 'text-purple-600',
          text: 'text-purple-600'
        };
      case 'orange':
        return {
          bg: 'bg-orange-50',
          icon: 'text-orange-600',
          text: 'text-orange-600'
        };
      default:
        return {
          bg: 'bg-gray-50',
          icon: 'text-gray-600',
          text: 'text-gray-600'
        };
    }
  };

  const colorClasses = getColorClasses();

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`${colorClasses.bg} rounded-lg p-2`}>
          <div className={colorClasses.icon}>
            {getIcon()}
          </div>
        </div>
        <div className="ml-4 flex-1">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <div className="flex items-baseline">
            <p className={`text-2xl font-bold ${colorClasses.text}`}>
              {value.toLocaleString()}
            </p>
            {trend && (
              <div className={`ml-2 flex items-center text-sm ${
                trend.isPositive ? 'text-green-600' : 'text-red-600'
              }`}>
                {trend.isPositive ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                <span className="ml-1">{Math.abs(trend.value)}%</span>
              </div>
            )}
          </div>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatisticsCard;