// FILE: frontend/src/components/Agents/EmailAnalyst/ActionItemsList.tsx

import React from 'react';

interface ActionItem {
  text: string;
  completed?: boolean;
  deadline?: string;
}

interface ActionItemsListProps {
  items: string[] | ActionItem[];
  title?: string;
  onToggle?: (index: number) => void;
}

const ActionItemsList: React.FC<ActionItemsListProps> = ({
  items,
  title = "Action Items",
  onToggle
}) => {
  if (!items || items.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-2">
          📋 {title}
        </h3>
        <p className="text-sm text-gray-500">No action items found.</p>
      </div>
    );
  }

  const normalizedItems: ActionItem[] = items.map(item =>
    typeof item === 'string' ? { text: item, completed: false } : item
  );

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <h3 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
        <span className="mr-2">📋</span>
        {title}
        <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
          {normalizedItems.length}
        </span>
      </h3>

      <ul className="space-y-2">
        {normalizedItems.map((item, index) => (
          <li
            key={index}
            className={`flex items-start gap-3 p-2 rounded transition-colors ${
              onToggle ? 'hover:bg-gray-50 cursor-pointer' : ''
            }`}
            onClick={() => onToggle?.(index)}
          >
            {/* Checkbox/Indicator */}
            <div className="flex-shrink-0 mt-0.5">
              {onToggle ? (
                <input
                  type="checkbox"
                  checked={item.completed || false}
                  onChange={() => onToggle(index)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  onClick={(e) => e.stopPropagation()}
                />
              ) : (
                <span className="text-blue-600">•</span>
              )}
            </div>

            {/* Action Text */}
            <div className="flex-1 min-w-0">
              <p
                className={`text-sm ${
                  item.completed
                    ? 'text-gray-500 line-through'
                    : 'text-gray-900'
                }`}
              >
                {item.text}
              </p>

              {/* Deadline */}
              {item.deadline && (
                <p className="text-xs text-gray-500 mt-1">
                  <span className="mr-1">⏰</span>
                  Due: {item.deadline}
                </p>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ActionItemsList;
