// FILE: frontend/src/components/Agents/JobHunter/CompanyResearch.tsx

import React from 'react';
import { Building2, Star, Users, TrendingUp, DollarSign, Award } from 'lucide-react';

interface CompanyResearchProps {
  company: string;
}

const CompanyResearch: React.FC<CompanyResearchProps> = ({ company }) => {
  // Mock company data - in production, this would come from the API
  const companyData = {
    company_name: company,
    industry: 'Technology',
    size: '500-1000 employees',
    founded: '2015',
    headquarters: 'San Francisco, CA',
    rating: 4.2,
    total_reviews: 234,
    culture_values: ['Innovation', 'Collaboration', 'Work-life balance'],
    pros: [
      'Great benefits and compensation',
      'Talented team and learning opportunities',
      'Flexible work arrangements',
      'Cutting-edge technology stack'
    ],
    cons: [
      'Fast-paced environment can be demanding',
      'Some organizational changes recently',
      'Limited upward mobility in some teams'
    ],
    ceo_rating: 4.5,
    recommend_to_friend: '85%',
    business_outlook: 'Positive',
    funding: 'Series C - $150M raised',
    key_investors: ['Sequoia Capital', 'Andreessen Horowitz'],
    recent_news: [
      'Launched new product line in Q4 2024',
      'Expanded to European market',
      'Received industry award for innovation'
    ]
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h4 className="text-xl font-bold text-gray-900 mb-2 flex items-center gap-2">
            <Building2 className="h-6 w-6 text-blue-600" />
            {companyData.company_name}
          </h4>
          <p className="text-gray-600">{companyData.industry}</p>
        </div>
        <div className="flex items-center gap-2 bg-green-100 text-green-800 px-4 py-2 rounded-lg">
          <Star className="h-5 w-5 fill-current" />
          <span className="text-lg font-bold">{companyData.rating}</span>
          <span className="text-sm">({companyData.total_reviews} reviews)</span>
        </div>
      </div>

      {/* Company Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <Users className="h-4 w-4" />
            <span className="text-xs font-medium">Size</span>
          </div>
          <p className="text-sm font-semibold text-gray-900">{companyData.size}</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <Award className="h-4 w-4" />
            <span className="text-xs font-medium">Founded</span>
          </div>
          <p className="text-sm font-semibold text-gray-900">{companyData.founded}</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <DollarSign className="h-4 w-4" />
            <span className="text-xs font-medium">Funding</span>
          </div>
          <p className="text-sm font-semibold text-gray-900">{companyData.funding.split('-')[0].trim()}</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <TrendingUp className="h-4 w-4" />
            <span className="text-xs font-medium">Outlook</span>
          </div>
          <p className="text-sm font-semibold text-green-600">{companyData.business_outlook}</p>
        </div>
      </div>

      {/* Culture & Values */}
      <div>
        <h5 className="font-semibold text-gray-900 mb-3">Culture & Values</h5>
        <div className="flex flex-wrap gap-2">
          {companyData.culture_values.map((value, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
            >
              {value}
            </span>
          ))}
        </div>
      </div>

      {/* Pros & Cons */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h5 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500"></div>
            Pros
          </h5>
          <ul className="space-y-2">
            {companyData.pros.map((pro, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                <span className="text-green-500 mt-1">+</span>
                {pro}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h5 className="font-semibold text-orange-900 mb-3 flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-orange-500"></div>
            Cons
          </h5>
          <ul className="space-y-2">
            {companyData.cons.map((con, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                <span className="text-orange-500 mt-1">-</span>
                {con}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Recent News */}
      <div>
        <h5 className="font-semibold text-gray-900 mb-3">Recent News</h5>
        <ul className="space-y-2">
          {companyData.recent_news.map((news, index) => (
            <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-blue-500 mt-2"></div>
              {news}
            </li>
          ))}
        </ul>
      </div>

      {/* Employee Satisfaction */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">CEO Rating</p>
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5 text-yellow-500 fill-current" />
              <span className="text-lg font-bold text-gray-900">{companyData.ceo_rating}</span>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Would Recommend</p>
            <p className="text-lg font-bold text-green-600">{companyData.recommend_to_friend}</p>
          </div>
        </div>
      </div>

      {/* Investors */}
      <div>
        <h5 className="font-semibold text-gray-900 mb-3">Key Investors</h5>
        <div className="flex flex-wrap gap-2">
          {companyData.key_investors.map((investor, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-purple-100 text-purple-800 rounded-lg text-sm font-medium"
            >
              {investor}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CompanyResearch;
