"""
Analytics & Strategy Agent - Data Analysis and Success Prediction

This agent handles:
- Application data analysis and insights
- Success pattern recognition across applications
- Job offer likelihood prediction
- Strategy recommendations for job search optimization
- Market salary analysis and benchmarking
"""

import json
import re
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from langchain.tools import tool
from langchain_core.messages import SystemMessage

from ..core.base_agent import BaseAgent, AgentConfig, AgentResponse
from ...database import DatabaseManager


class AnalyticsAgent(BaseAgent):
    """
    Analytics & Strategy Agent for data-driven insights and predictions.

    Uses ReAct pattern to:
    1. Analyze application data and identify trends
    2. Recognize success patterns in job searches
    3. Predict job offer likelihood based on multiple factors
    4. Recommend optimization strategies
    5. Provide market salary insights
    """

    def __init__(
        self,
        db_manager: DatabaseManager,
        config: Optional[AgentConfig] = None
    ):
        """Initialize Analytics & Strategy Agent."""
        self.db_manager = db_manager
        super().__init__(config or AgentConfig(
            name="Analytics & Strategy Agent",
            description="AI agent for data analysis, pattern recognition, and strategic recommendations",
            model="gpt-4o-mini",
            temperature=0.2,  # Lower temperature for more deterministic analysis
            max_iterations=15,
            enable_memory=True
        ))

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Analytics Agent."""
        return """You are an expert Analytics & Strategy Agent specializing in job search data analysis and optimization.

Your responsibilities:
1. Analyze job application data to extract meaningful insights
2. Identify patterns that lead to successful outcomes (interviews, offers)
3. Predict job offer likelihood based on application characteristics
4. Recommend data-driven strategies to improve job search success
5. Provide market salary analysis and compensation insights

When analyzing data:
- Use statistical methods to identify trends and patterns
- Consider multiple factors (application quality, timing, company type, industry)
- Provide confidence scores for predictions
- Base recommendations on concrete data insights
- Compare individual performance against benchmarks

Use the available tools to:
- Analyze application statistics and trends
- Identify success patterns from historical data
- Calculate job offer likelihood scores
- Generate strategic recommendations
- Provide salary market analysis
- Track key performance metrics

Always provide:
- Clear, actionable insights
- Data-driven recommendations
- Confidence levels for predictions
- Specific next steps for improvement
- Visual data representations when helpful"""

    def _register_tools(self) -> List:
        """Register tools for the Analytics Agent."""

        @tool
        def analyze_application_stats(
            user_id: int = 1,
            time_period_days: int = 90
        ) -> str:
            """
            Analyze application statistics over a time period.

            Args:
                user_id: User ID to analyze (default: 1)
                time_period_days: Number of days to analyze (default: 90)

            Returns:
                JSON string with comprehensive application statistics
            """
            # Simulated analytics data
            # In production, this would query the database

            start_date = datetime.now() - timedelta(days=time_period_days)

            stats = {
                "user_id": user_id,
                "time_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": datetime.now().isoformat(),
                    "days": time_period_days
                },
                "applications": {
                    "total": 45,
                    "by_status": {
                        "applied": 15,
                        "screening": 8,
                        "interview": 12,
                        "offer": 3,
                        "rejected": 7
                    },
                    "by_month": {
                        "month_1": 12,
                        "month_2": 18,
                        "month_3": 15
                    }
                },
                "conversion_rates": {
                    "application_to_screening": 0.378,  # 38%
                    "screening_to_interview": 0.615,   # 62%
                    "interview_to_offer": 0.25,        # 25%
                    "overall_success_rate": 0.067      # 6.7%
                },
                "response_metrics": {
                    "avg_first_response_days": 5.2,
                    "avg_interview_scheduling_days": 8.4,
                    "avg_time_to_offer_days": 28.3,
                    "response_rate": 0.733             # 73%
                },
                "industry_breakdown": {
                    "Technology": 25,
                    "Finance": 10,
                    "Healthcare": 5,
                    "Retail": 3,
                    "Other": 2
                },
                "company_size_breakdown": {
                    "Startup (1-50)": 8,
                    "Small (51-200)": 12,
                    "Medium (201-1000)": 15,
                    "Large (1000+)": 10
                },
                "application_quality_score": {
                    "average": 7.8,
                    "min": 5.2,
                    "max": 9.5,
                    "trend": "improving"
                },
                "insights": [
                    "Application volume increased 50% in the last month",
                    "Highest conversion rate with Medium-sized companies (20%)",
                    "Technology sector shows 40% higher response rate",
                    "Applications sent on Tuesday-Thursday get 25% more responses",
                    "Average time to first response improved by 2 days"
                ]
            }

            return json.dumps(stats, indent=2)

        @tool
        def identify_success_patterns(
            user_id: int = 1,
            min_confidence: float = 0.7
        ) -> str:
            """
            Identify patterns that correlate with successful outcomes.

            Args:
                user_id: User ID to analyze (default: 1)
                min_confidence: Minimum confidence threshold (0.0-1.0)

            Returns:
                JSON string with identified success patterns
            """
            # Simulated pattern recognition
            # In production, this would use ML/statistical analysis on real data

            patterns = {
                "user_id": user_id,
                "analysis_date": datetime.now().isoformat(),
                "patterns_found": [
                    {
                        "pattern_id": 1,
                        "name": "Optimal Application Timing",
                        "description": "Applications submitted on Tuesday-Thursday between 9-11 AM",
                        "confidence": 0.85,
                        "impact": "high",
                        "data": {
                            "success_rate_with_pattern": 0.32,
                            "success_rate_without_pattern": 0.18,
                            "improvement": "+77%"
                        },
                        "recommendation": "Schedule applications for Tuesday-Thursday mornings"
                    },
                    {
                        "pattern_id": 2,
                        "name": "Personalized Cover Letter Effect",
                        "description": "Applications with customized cover letters mentioning specific projects",
                        "confidence": 0.92,
                        "impact": "very_high",
                        "data": {
                            "success_rate_with_pattern": 0.45,
                            "success_rate_without_pattern": 0.15,
                            "improvement": "+200%"
                        },
                        "recommendation": "Always include personalized cover letters with specific company research"
                    },
                    {
                        "pattern_id": 3,
                        "name": "Company Size Sweet Spot",
                        "description": "Medium-sized companies (201-1000 employees) show highest conversion",
                        "confidence": 0.78,
                        "impact": "high",
                        "data": {
                            "success_rate_with_pattern": 0.28,
                            "success_rate_without_pattern": 0.12,
                            "improvement": "+133%"
                        },
                        "recommendation": "Prioritize medium-sized companies in target industry"
                    },
                    {
                        "pattern_id": 4,
                        "name": "Follow-up Timing Optimization",
                        "description": "Following up 7-10 days after application doubles response rate",
                        "confidence": 0.89,
                        "impact": "high",
                        "data": {
                            "success_rate_with_pattern": 0.36,
                            "success_rate_without_pattern": 0.18,
                            "improvement": "+100%"
                        },
                        "recommendation": "Set automatic follow-up reminders for 7-10 days post-application"
                    },
                    {
                        "pattern_id": 5,
                        "name": "Referral Impact",
                        "description": "Applications with employee referrals",
                        "confidence": 0.95,
                        "impact": "very_high",
                        "data": {
                            "success_rate_with_pattern": 0.65,
                            "success_rate_without_pattern": 0.15,
                            "improvement": "+333%"
                        },
                        "recommendation": "Actively seek employee referrals through networking"
                    },
                    {
                        "pattern_id": 6,
                        "name": "Skills Alignment",
                        "description": "70%+ keyword match between resume and job description",
                        "confidence": 0.82,
                        "impact": "high",
                        "data": {
                            "success_rate_with_pattern": 0.38,
                            "success_rate_without_pattern": 0.14,
                            "improvement": "+171%"
                        },
                        "recommendation": "Tailor resume to match at least 70% of job requirements"
                    }
                ],
                "summary": {
                    "total_patterns": 6,
                    "high_confidence_patterns": 5,
                    "average_improvement": "+167%",
                    "top_recommendation": "Focus on referrals and personalized applications"
                }
            }

            # Filter by confidence
            patterns["patterns_found"] = [
                p for p in patterns["patterns_found"]
                if p["confidence"] >= min_confidence
            ]
            patterns["summary"]["total_patterns"] = len(patterns["patterns_found"])

            return json.dumps(patterns, indent=2)

        @tool
        def predict_offer_likelihood(
            job_title: str,
            company_size: str,
            industry: str,
            skills_match_percent: int,
            has_referral: bool = False,
            has_cover_letter: bool = True,
            years_experience: int = 5,
            application_quality_score: float = 7.5
        ) -> str:
            """
            Predict the likelihood of receiving a job offer.

            Args:
                job_title: Job title/role
                company_size: Company size (Startup, Small, Medium, Large)
                industry: Industry sector
                skills_match_percent: Percentage match of skills (0-100)
                has_referral: Whether applicant has employee referral
                has_cover_letter: Whether application includes cover letter
                years_experience: Years of relevant experience
                application_quality_score: Overall quality score (1-10)

            Returns:
                JSON string with offer likelihood prediction
            """
            # Simulated ML prediction model
            # In production, this would use a trained ML model

            # Base score calculation
            base_score = 30

            # Factor weights
            scores = {
                "skills_match": min(skills_match_percent * 0.3, 30),
                "referral_bonus": 20 if has_referral else 0,
                "cover_letter_bonus": 8 if has_cover_letter else 0,
                "quality_score": application_quality_score * 2,
                "experience_factor": min(years_experience * 2, 15)
            }

            # Company size factor
            company_multipliers = {
                "Startup": 0.9,
                "Small": 1.0,
                "Medium": 1.2,
                "Large": 0.95
            }
            company_factor = company_multipliers.get(company_size, 1.0)

            # Industry factor
            industry_multipliers = {
                "Technology": 1.1,
                "Finance": 1.0,
                "Healthcare": 0.95,
                "Retail": 0.85,
                "Other": 0.9
            }
            industry_factor = industry_multipliers.get(industry, 1.0)

            # Calculate total score
            raw_score = sum(scores.values()) * company_factor * industry_factor
            likelihood_percent = min(int(raw_score), 95)  # Cap at 95%

            # Determine confidence level
            if likelihood_percent >= 70:
                confidence_level = "very_high"
                recommendation = "Excellent opportunity - prioritize this application"
            elif likelihood_percent >= 50:
                confidence_level = "high"
                recommendation = "Strong candidate - good chance of success"
            elif likelihood_percent >= 30:
                confidence_level = "moderate"
                recommendation = "Competitive - enhance application with referral or networking"
            else:
                confidence_level = "low"
                recommendation = "Consider strengthening skills alignment or seeking referral"

            prediction = {
                "job_details": {
                    "title": job_title,
                    "company_size": company_size,
                    "industry": industry
                },
                "prediction": {
                    "offer_likelihood_percent": likelihood_percent,
                    "confidence_level": confidence_level,
                    "stage_probabilities": {
                        "screening_callback": min(likelihood_percent + 15, 95),
                        "interview_invitation": likelihood_percent,
                        "offer_received": max(likelihood_percent - 20, 5)
                    }
                },
                "contributing_factors": {
                    "scores": scores,
                    "company_factor": company_factor,
                    "industry_factor": industry_factor,
                    "strengths": [],
                    "areas_for_improvement": []
                },
                "recommendation": recommendation,
                "improvement_suggestions": []
            }

            # Identify strengths and improvements
            if skills_match_percent >= 70:
                prediction["contributing_factors"]["strengths"].append("Strong skills alignment")
            else:
                prediction["contributing_factors"]["areas_for_improvement"].append("Skills match below 70%")
                prediction["improvement_suggestions"].append("Tailor resume to better match job requirements")

            if has_referral:
                prediction["contributing_factors"]["strengths"].append("Employee referral (+20% likelihood)")
            else:
                prediction["improvement_suggestions"].append("Seek employee referral to increase chances by 20%")

            if application_quality_score >= 8:
                prediction["contributing_factors"]["strengths"].append("High-quality application")
            else:
                prediction["improvement_suggestions"].append("Improve application quality (current: {}/10)".format(application_quality_score))

            if years_experience >= 5:
                prediction["contributing_factors"]["strengths"].append("Solid experience level")
            else:
                prediction["contributing_factors"]["areas_for_improvement"].append("Limited experience for role")

            return json.dumps(prediction, indent=2)

        @tool
        def generate_strategy_recommendations(
            current_success_rate: float,
            applications_per_week: int,
            target_role: str,
            user_id: int = 1
        ) -> str:
            """
            Generate personalized strategy recommendations.

            Args:
                current_success_rate: Current offer success rate (0.0-1.0)
                applications_per_week: Average applications submitted per week
                target_role: Target job role/title
                user_id: User ID for personalized recommendations

            Returns:
                JSON string with strategic recommendations
            """
            # Calculate performance benchmarks
            industry_avg_success_rate = 0.15  # 15% industry average
            optimal_apps_per_week = 10

            performance_ratio = current_success_rate / industry_avg_success_rate if industry_avg_success_rate > 0 else 1.0

            recommendations = {
                "user_id": user_id,
                "target_role": target_role,
                "current_performance": {
                    "success_rate": current_success_rate,
                    "applications_per_week": applications_per_week,
                    "vs_industry_avg": f"{'+' if performance_ratio > 1 else ''}{((performance_ratio - 1) * 100):.1f}%"
                },
                "strategic_recommendations": [],
                "tactical_actions": [],
                "resource_allocation": {},
                "timeline": {},
                "expected_outcomes": {}
            }

            # Generate recommendations based on performance
            if current_success_rate < 0.10:
                recommendations["strategic_recommendations"].extend([
                    {
                        "priority": "critical",
                        "category": "application_quality",
                        "title": "Improve Application Quality",
                        "description": "Current success rate below 10% indicates quality issues",
                        "actions": [
                            "Get professional resume review",
                            "Customize each application to job description",
                            "Use Resume Writer Agent for tailoring",
                            "Improve cover letter personalization"
                        ],
                        "expected_impact": "+5-8% success rate"
                    },
                    {
                        "priority": "high",
                        "category": "targeting",
                        "title": "Refine Job Targeting",
                        "description": "Focus on roles that better match your profile",
                        "actions": [
                            "Apply only to positions with 70%+ skills match",
                            "Target companies with culture fit",
                            "Focus on medium-sized companies (higher conversion)",
                            "Leverage Job Hunter Agent for better matches"
                        ],
                        "expected_impact": "+3-5% success rate"
                    }
                ])

            if applications_per_week < 5:
                recommendations["strategic_recommendations"].append({
                    "priority": "high",
                    "category": "volume",
                    "title": "Increase Application Volume",
                    "description": "Low application volume limits opportunities",
                    "actions": [
                        "Set goal of 10-15 quality applications per week",
                        "Use Job Hunter Agent to find more opportunities",
                        "Block dedicated time for job searching (2 hrs/day)",
                        "Create application templates to improve efficiency"
                    ],
                    "expected_impact": "+50% interview opportunities"
                })
            elif applications_per_week > 20:
                recommendations["strategic_recommendations"].append({
                    "priority": "medium",
                    "category": "quality_over_quantity",
                    "title": "Focus on Quality Over Quantity",
                    "description": "High volume may indicate spray-and-pray approach",
                    "actions": [
                        "Reduce to 10-15 highly targeted applications per week",
                        "Spend more time on personalization",
                        "Research each company thoroughly",
                        "Seek referrals for top-choice companies"
                    ],
                    "expected_impact": "+10-15% success rate"
                })

            # Always include networking recommendation
            recommendations["strategic_recommendations"].append({
                "priority": "high",
                "category": "networking",
                "title": "Leverage Networking and Referrals",
                "description": "Referrals increase success rate by 300%",
                "actions": [
                    "Connect with employees at target companies on LinkedIn",
                    "Attend industry events and meetups",
                    "Engage in online communities related to target role",
                    "Request informational interviews",
                    "Join professional associations"
                ],
                "expected_impact": "+20-30% with referrals"
            })

            # Follow-up strategy
            recommendations["strategic_recommendations"].append({
                "priority": "medium",
                "category": "follow_up",
                "title": "Implement Systematic Follow-up",
                "description": "Follow-ups double response rates",
                "actions": [
                    "Follow up 7-10 days after each application",
                    "Use Follow-up Agent for optimal timing",
                    "Send personalized follow-up messages",
                    "Track all follow-up interactions"
                ],
                "expected_impact": "+100% response rate"
            })

            # Tactical actions
            recommendations["tactical_actions"] = [
                {
                    "timeframe": "This Week",
                    "action": "Review and optimize resume with Resume Writer Agent",
                    "effort": "2 hours"
                },
                {
                    "timeframe": "This Week",
                    "action": "Identify 5 target companies and research them thoroughly",
                    "effort": "3 hours"
                },
                {
                    "timeframe": "Next Week",
                    "action": "Submit 10 high-quality, personalized applications",
                    "effort": "5 hours"
                },
                {
                    "timeframe": "Next Week",
                    "action": "Connect with 10 employees at target companies",
                    "effort": "2 hours"
                },
                {
                    "timeframe": "Ongoing",
                    "action": "Follow up on all applications 7-10 days after submission",
                    "effort": "1 hour/week"
                }
            ]

            # Resource allocation
            recommendations["resource_allocation"] = {
                "application_preparation": "40%",
                "networking_and_referrals": "30%",
                "skill_development": "15%",
                "follow_up_and_tracking": "15%"
            }

            # Timeline and outcomes
            recommendations["timeline"] = {
                "week_1_4": "Foundation building - optimize materials, build network",
                "week_5_8": "Active application phase - 10-15 apps/week with follow-ups",
                "week_9_12": "Interview preparation and negotiation"
            }

            recommendations["expected_outcomes"] = {
                "4_weeks": "3-5 interview invitations",
                "8_weeks": "8-12 interview invitations, 1-2 offers",
                "12_weeks": "15-20 interview invitations, 3-5 offers"
            }

            return json.dumps(recommendations, indent=2)

        @tool
        def analyze_market_salary(
            job_title: str,
            location: str,
            years_experience: int,
            industry: str = "Technology",
            company_size: str = "Medium"
        ) -> str:
            """
            Analyze market salary data for a given role.

            Args:
                job_title: Job title/role
                location: Geographic location
                years_experience: Years of experience
                industry: Industry sector
                company_size: Company size category

            Returns:
                JSON string with salary market analysis
            """
            # Simulated salary data
            # In production, this would integrate with salary APIs (Glassdoor, Payscale, etc.)

            # Base salary calculation (simplified)
            base_salaries = {
                "Software Engineer": 120000,
                "Senior Software Engineer": 160000,
                "Staff Engineer": 200000,
                "Engineering Manager": 180000,
                "Product Manager": 140000,
                "Data Scientist": 135000,
                "Backend Developer": 125000,
                "Frontend Developer": 115000,
                "Full Stack Engineer": 130000
            }

            base_salary = base_salaries.get(job_title, 120000)

            # Experience multiplier
            exp_multiplier = 1.0 + (min(years_experience, 10) * 0.05)

            # Location adjustment
            location_multipliers = {
                "San Francisco": 1.4,
                "New York": 1.3,
                "Seattle": 1.25,
                "Austin": 1.1,
                "Remote": 1.15,
                "Boston": 1.2,
                "Denver": 1.05,
                "Other": 0.95
            }

            location_key = next((k for k in location_multipliers if k in location), "Other")
            location_mult = location_multipliers[location_key]

            # Company size adjustment
            size_multipliers = {
                "Startup": 0.9,
                "Small": 0.95,
                "Medium": 1.0,
                "Large": 1.15
            }
            size_mult = size_multipliers.get(company_size, 1.0)

            # Calculate salary range
            median_salary = int(base_salary * exp_multiplier * location_mult * size_mult)
            p10_salary = int(median_salary * 0.75)
            p25_salary = int(median_salary * 0.85)
            p75_salary = int(median_salary * 1.15)
            p90_salary = int(median_salary * 1.35)

            analysis = {
                "job_title": job_title,
                "location": location,
                "years_experience": years_experience,
                "industry": industry,
                "company_size": company_size,
                "salary_range": {
                    "currency": "USD",
                    "percentiles": {
                        "p10": p10_salary,
                        "p25": p25_salary,
                        "p50_median": median_salary,
                        "p75": p75_salary,
                        "p90": p90_salary
                    },
                    "typical_range": f"${p25_salary:,} - ${p75_salary:,}",
                    "competitive_salary": f"${median_salary:,}"
                },
                "total_compensation": {
                    "base_salary": median_salary,
                    "bonus_range": f"${int(median_salary * 0.1):,} - ${int(median_salary * 0.2):,}",
                    "equity_value": f"${int(median_salary * 0.15):,} - ${int(median_salary * 0.3):,}",
                    "total_range": f"${int(median_salary * 1.25):,} - ${int(median_salary * 1.5):,}"
                },
                "market_insights": [
                    f"Median salary for {job_title} in {location}: ${median_salary:,}",
                    f"Location factor: {location_key} pays {((location_mult - 1) * 100):+.0f}% vs national average",
                    f"Company size factor: {company_size} companies pay {((size_mult - 1) * 100):+.0f}% vs average",
                    f"Top 25% earn above ${p75_salary:,}",
                    "Consider negotiating for equity and sign-on bonus in addition to base"
                ],
                "negotiation_tips": [
                    f"Target salary range: ${p75_salary:,} - ${p90_salary:,} for strong candidates",
                    "Research company-specific compensation on Glassdoor and Levels.fyi",
                    "Factor in total compensation (base + bonus + equity + benefits)",
                    "Don't disclose current salary - focus on market rate",
                    "Ask for 10-20% above your target to leave negotiation room"
                ],
                "benefits_to_consider": [
                    "Health insurance (medical, dental, vision)",
                    "401(k) matching",
                    "Stock options or RSUs",
                    "Sign-on bonus",
                    "Remote work flexibility",
                    "Professional development budget",
                    "PTO and vacation days",
                    "Parental leave"
                ],
                "market_trends": {
                    "demand": "High",
                    "growth_rate": "+12% year-over-year",
                    "competition": "Moderate",
                    "outlook": "Positive - strong hiring market for next 12-18 months"
                }
            }

            return json.dumps(analysis, indent=2)

        @tool
        def calculate_performance_metrics(
            user_id: int = 1,
            benchmark_type: str = "industry"
        ) -> str:
            """
            Calculate key performance metrics and compare to benchmarks.

            Args:
                user_id: User ID to analyze
                benchmark_type: Type of benchmark (industry, role, experience_level)

            Returns:
                JSON string with performance metrics and comparisons
            """
            # Simulated metrics calculation

            metrics = {
                "user_id": user_id,
                "benchmark_type": benchmark_type,
                "calculated_at": datetime.now().isoformat(),
                "key_metrics": {
                    "application_velocity": {
                        "value": 12,
                        "unit": "applications/week",
                        "benchmark": 10,
                        "performance": "Above average",
                        "percentile": 65
                    },
                    "response_rate": {
                        "value": 0.73,
                        "unit": "percentage",
                        "benchmark": 0.60,
                        "performance": "Good",
                        "percentile": 70
                    },
                    "interview_conversion": {
                        "value": 0.27,
                        "unit": "percentage",
                        "benchmark": 0.22,
                        "performance": "Above average",
                        "percentile": 68
                    },
                    "offer_conversion": {
                        "value": 0.067,
                        "unit": "percentage",
                        "benchmark": 0.15,
                        "performance": "Below average",
                        "percentile": 35
                    },
                    "time_to_offer": {
                        "value": 28.3,
                        "unit": "days",
                        "benchmark": 24.0,
                        "performance": "Slightly slow",
                        "percentile": 45
                    },
                    "application_quality": {
                        "value": 7.8,
                        "unit": "score (1-10)",
                        "benchmark": 7.0,
                        "performance": "Good",
                        "percentile": 72
                    }
                },
                "strengths": [
                    "High application velocity - staying active",
                    "Strong response rate - good targeting",
                    "Above-average application quality"
                ],
                "areas_for_improvement": [
                    "Offer conversion rate below benchmark - focus on interview prep",
                    "Time to offer slightly high - may need to follow up more proactively"
                ],
                "recommendations": [
                    "Use Interview Prep Agent to improve offer conversion",
                    "Implement systematic follow-up strategy",
                    "Continue maintaining high application quality",
                    "Consider negotiation training to convert more offers"
                ],
                "overall_score": {
                    "value": 72,
                    "grade": "B",
                    "description": "Good performance with room for improvement"
                }
            }

            return json.dumps(metrics, indent=2)

        return [
            analyze_application_stats,
            identify_success_patterns,
            predict_offer_likelihood,
            generate_strategy_recommendations,
            analyze_market_salary,
            calculate_performance_metrics
        ]

    async def analyze_application_data(
        self,
        user_id: int = 1,
        time_period_days: int = 90
    ) -> Dict[str, Any]:
        """
        Analyze application data and provide insights.

        Args:
            user_id: User ID to analyze
            time_period_days: Number of days to analyze

        Returns:
            Dictionary with analysis results
        """
        query = f"""Analyze my job application data for the past {time_period_days} days.

Provide:
1. Overall statistics and trends
2. Conversion rates at each stage
3. Response time metrics
4. Industry and company size breakdown
5. Key insights and recommendations

User ID: {user_id}"""

        result = await self.run(query)

        return {
            "success": result.success,
            "analysis": result.output,
            "metadata": result.metadata,
            "error": result.error
        }

    async def get_success_patterns(
        self,
        user_id: int = 1,
        min_confidence: float = 0.7
    ) -> Dict[str, Any]:
        """
        Identify success patterns in job applications.

        Args:
            user_id: User ID to analyze
            min_confidence: Minimum confidence threshold

        Returns:
            Dictionary with identified patterns
        """
        query = f"""Identify patterns that lead to successful job application outcomes.

Analyze:
1. Application timing patterns
2. Application quality factors
3. Company characteristics
4. Follow-up strategies
5. Skills alignment impact

Minimum confidence: {min_confidence}
User ID: {user_id}

Provide actionable recommendations based on patterns found."""

        result = await self.run(query)

        return {
            "success": result.success,
            "patterns": result.output,
            "metadata": result.metadata,
            "error": result.error
        }

    async def predict_offer_success(
        self,
        job_details: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict likelihood of receiving a job offer.

        Args:
            job_details: Dictionary with job information
            user_profile: Dictionary with user profile information

        Returns:
            Dictionary with prediction results
        """
        job_title = job_details.get("title", "Software Engineer")
        company_size = job_details.get("company_size", "Medium")
        industry = job_details.get("industry", "Technology")

        skills_match = user_profile.get("skills_match_percent", 70)
        has_referral = user_profile.get("has_referral", False)
        has_cover_letter = user_profile.get("has_cover_letter", True)
        years_exp = user_profile.get("years_experience", 5)
        quality_score = user_profile.get("application_quality_score", 7.5)

        query = f"""Predict the likelihood of receiving a job offer for this application:

Job: {job_title} at a {company_size} {industry} company
Skills Match: {skills_match}%
Has Referral: {has_referral}
Has Cover Letter: {has_cover_letter}
Years Experience: {years_exp}
Application Quality: {quality_score}/10

Provide:
1. Offer likelihood percentage
2. Contributing factors analysis
3. Strengths and areas for improvement
4. Specific recommendations to increase chances"""

        result = await self.run(query)

        return {
            "success": result.success,
            "prediction": result.output,
            "metadata": result.metadata,
            "error": result.error
        }

    async def get_optimization_strategy(
        self,
        current_stats: Dict[str, Any],
        target_role: str
    ) -> Dict[str, Any]:
        """
        Generate optimization strategy recommendations.

        Args:
            current_stats: Dictionary with current performance statistics
            target_role: Target job role

        Returns:
            Dictionary with strategy recommendations
        """
        success_rate = current_stats.get("success_rate", 0.05)
        apps_per_week = current_stats.get("applications_per_week", 8)

        query = f"""Generate a personalized job search optimization strategy.

Current Performance:
- Success Rate: {success_rate * 100:.1f}%
- Applications per Week: {apps_per_week}
- Target Role: {target_role}

Provide:
1. Strategic recommendations prioritized by impact
2. Tactical actions with timelines
3. Resource allocation guidance
4. Expected outcomes and timeline
5. Key performance metrics to track"""

        result = await self.run(query)

        return {
            "success": result.success,
            "strategy": result.output,
            "metadata": result.metadata,
            "error": result.error
        }

    async def get_salary_insights(
        self,
        job_title: str,
        location: str,
        years_experience: int,
        industry: str = "Technology",
        company_size: str = "Medium"
    ) -> Dict[str, Any]:
        """
        Get market salary analysis and insights.

        Args:
            job_title: Job title/role
            location: Geographic location
            years_experience: Years of experience
            industry: Industry sector
            company_size: Company size category

        Returns:
            Dictionary with salary insights
        """
        query = f"""Provide comprehensive salary market analysis for:

Role: {job_title}
Location: {location}
Experience: {years_experience} years
Industry: {industry}
Company Size: {company_size}

Include:
1. Salary ranges (p10, p25, median, p75, p90)
2. Total compensation breakdown
3. Market insights and trends
4. Negotiation strategies
5. Benefits to consider"""

        result = await self.run(query)

        return {
            "success": result.success,
            "salary_analysis": result.output,
            "metadata": result.metadata,
            "error": result.error
        }


def create_analytics_agent(db_manager: DatabaseManager) -> AnalyticsAgent:
    """
    Factory function to create an Analytics Agent instance.

    Args:
        db_manager: Database manager instance

    Returns:
        Configured AnalyticsAgent instance
    """
    return AnalyticsAgent(db_manager=db_manager)
