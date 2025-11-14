"""
Cost tracking system for agent API calls.

Tracks:
- Token usage per agent and model
- Cost per execution
- Budget alerts
- Cost optimization recommendations
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """OpenAI model types with pricing."""
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_35_TURBO = "gpt-3.5-turbo"


# Pricing per 1M tokens (as of 2024)
MODEL_PRICING = {
    ModelType.GPT_4O: {
        'input': 2.50,  # $2.50 per 1M input tokens
        'output': 10.00  # $10.00 per 1M output tokens
    },
    ModelType.GPT_4O_MINI: {
        'input': 0.150,  # $0.15 per 1M input tokens
        'output': 0.600  # $0.60 per 1M output tokens
    },
    ModelType.GPT_4_TURBO: {
        'input': 10.00,
        'output': 30.00
    },
    ModelType.GPT_35_TURBO: {
        'input': 0.50,
        'output': 1.50
    }
}


@dataclass
class TokenUsage:
    """Token usage for a single API call."""
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class AgentCostSummary:
    """Cost summary for an agent."""
    agent_name: str
    period_start: datetime
    period_end: datetime
    total_calls: int
    total_tokens: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost: float
    avg_cost_per_call: float
    avg_tokens_per_call: float
    model_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['period_start'] = self.period_start.isoformat()
        data['period_end'] = self.period_end.isoformat()
        return data


class CostTracker:
    """
    Cost tracking system for monitoring agent API usage.

    Features:
    - Accurate token and cost tracking
    - Per-agent and per-model analytics
    - Budget monitoring and alerts
    - Cost optimization recommendations
    - Historical cost data
    """

    def __init__(self, daily_budget: Optional[float] = None):
        """
        Initialize cost tracker.

        Args:
            daily_budget: Optional daily budget limit in USD
        """
        self.daily_budget = daily_budget
        self.usage_history: Dict[str, List[TokenUsage]] = defaultdict(list)
        self.max_history = 10000
        logger.info(f"💰 Cost Tracker initialized (daily_budget=${daily_budget or 'unlimited'})")

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> TokenUsage:
        """
        Calculate cost for token usage.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            TokenUsage object with cost breakdown
        """
        # Get pricing for model (default to GPT-4O-MINI if not found)
        pricing = MODEL_PRICING.get(model, MODEL_PRICING[ModelType.GPT_4O_MINI])

        # Calculate costs (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        total_cost = input_cost + output_cost

        return TokenUsage(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost
        )

    def track_usage(
        self,
        agent_name: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> TokenUsage:
        """
        Track token usage for an agent.

        Args:
            agent_name: Name of the agent
            model: Model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            TokenUsage object
        """
        usage = self.calculate_cost(model, input_tokens, output_tokens)

        # Store usage
        self.usage_history[agent_name].append(usage)

        # Trim history if needed
        if len(self.usage_history[agent_name]) > self.max_history:
            self.usage_history[agent_name] = self.usage_history[agent_name][-self.max_history:]

        logger.info(
            f"💰 {agent_name}: {input_tokens + output_tokens} tokens "
            f"(${usage.total_cost:.4f}) - Model: {model}"
        )

        return usage

    def get_agent_summary(
        self,
        agent_name: str,
        period_hours: int = 24
    ) -> Optional[AgentCostSummary]:
        """
        Get cost summary for an agent.

        Args:
            agent_name: Name of the agent
            period_hours: Time period in hours

        Returns:
            AgentCostSummary or None if no data
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=period_hours)

        # Filter usage by time period
        usage_list = [
            u for u in self.usage_history.get(agent_name, [])
            if start_time <= u.timestamp <= end_time
        ]

        if not usage_list:
            return None

        # Calculate aggregates
        total_calls = len(usage_list)
        total_tokens = sum(u.total_tokens for u in usage_list)
        total_input_tokens = sum(u.input_tokens for u in usage_list)
        total_output_tokens = sum(u.output_tokens for u in usage_list)
        total_cost = sum(u.total_cost for u in usage_list)

        # Model breakdown
        model_breakdown = defaultdict(lambda: {
            'calls': 0,
            'tokens': 0,
            'cost': 0.0
        })

        for usage in usage_list:
            model_breakdown[usage.model]['calls'] += 1
            model_breakdown[usage.model]['tokens'] += usage.total_tokens
            model_breakdown[usage.model]['cost'] += usage.total_cost

        return AgentCostSummary(
            agent_name=agent_name,
            period_start=start_time,
            period_end=end_time,
            total_calls=total_calls,
            total_tokens=total_tokens,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_cost=total_cost,
            avg_cost_per_call=total_cost / total_calls,
            avg_tokens_per_call=total_tokens / total_calls,
            model_breakdown=dict(model_breakdown)
        )

    def get_all_agents_summary(self, period_hours: int = 24) -> Dict[str, AgentCostSummary]:
        """
        Get cost summary for all agents.

        Args:
            period_hours: Time period in hours

        Returns:
            Dictionary mapping agent names to their cost summaries
        """
        summary = {}
        for agent_name in self.usage_history.keys():
            agent_summary = self.get_agent_summary(agent_name, period_hours)
            if agent_summary:
                summary[agent_name] = agent_summary
        return summary

    def get_total_cost(self, period_hours: int = 24) -> float:
        """
        Get total cost across all agents.

        Args:
            period_hours: Time period in hours

        Returns:
            Total cost in USD
        """
        summaries = self.get_all_agents_summary(period_hours)
        return sum(s.total_cost for s in summaries.values())

    def check_budget_status(self) -> Dict[str, Any]:
        """
        Check current budget status.

        Returns:
            Dictionary with budget information and alerts
        """
        if not self.daily_budget:
            return {
                'budget_enabled': False,
                'message': 'No daily budget set'
            }

        daily_cost = self.get_total_cost(period_hours=24)
        budget_used_pct = (daily_cost / self.daily_budget) * 100

        status = {
            'budget_enabled': True,
            'daily_budget': self.daily_budget,
            'cost_today': daily_cost,
            'remaining_budget': self.daily_budget - daily_cost,
            'budget_used_percent': budget_used_pct,
            'alerts': []
        }

        # Generate alerts
        if budget_used_pct >= 100:
            status['alerts'].append({
                'severity': 'critical',
                'message': f'Daily budget exceeded! Used ${daily_cost:.2f} of ${self.daily_budget:.2f}'
            })
        elif budget_used_pct >= 90:
            status['alerts'].append({
                'severity': 'high',
                'message': f'90% of daily budget used (${daily_cost:.2f} / ${self.daily_budget:.2f})'
            })
        elif budget_used_pct >= 75:
            status['alerts'].append({
                'severity': 'medium',
                'message': f'75% of daily budget used (${daily_cost:.2f} / ${self.daily_budget:.2f})'
            })

        return status

    def get_cost_optimization_tips(self) -> List[Dict[str, str]]:
        """
        Get cost optimization recommendations.

        Returns:
            List of optimization tips
        """
        tips = []
        summaries = self.get_all_agents_summary(period_hours=24)

        for agent_name, summary in summaries.items():
            # Check if using expensive models
            for model, breakdown in summary.model_breakdown.items():
                if model in [ModelType.GPT_4_TURBO, ModelType.GPT_4O]:
                    tips.append({
                        'agent': agent_name,
                        'type': 'model_optimization',
                        'message': f'{agent_name} is using {model}. Consider GPT-4O-MINI for cost savings.',
                        'potential_savings': self._estimate_savings(breakdown['tokens'], model)
                    })

            # Check for high token usage
            if summary.avg_tokens_per_call > 5000:
                tips.append({
                    'agent': agent_name,
                    'type': 'token_optimization',
                    'message': f'{agent_name} uses {summary.avg_tokens_per_call:.0f} tokens/call. '
                               'Consider optimizing prompts or using streaming.'
                })

        return tips

    def _estimate_savings(self, tokens: int, current_model: str) -> str:
        """Estimate cost savings by switching to cheaper model."""
        current_cost = (tokens / 1_000_000) * (
            MODEL_PRICING.get(current_model, MODEL_PRICING[ModelType.GPT_4O_MINI])['input'] +
            MODEL_PRICING.get(current_model, MODEL_PRICING[ModelType.GPT_4O_MINI])['output']
        ) / 2  # Average input/output

        cheaper_cost = (tokens / 1_000_000) * (
            MODEL_PRICING[ModelType.GPT_4O_MINI]['input'] +
            MODEL_PRICING[ModelType.GPT_4O_MINI]['output']
        ) / 2

        savings = current_cost - cheaper_cost
        savings_pct = (savings / current_cost) * 100 if current_cost > 0 else 0

        return f"${savings:.4f} ({savings_pct:.1f}% savings)"

    def export_usage_report(self, filepath: Optional[str] = None) -> str:
        """
        Export usage report as JSON.

        Args:
            filepath: Optional file path to save

        Returns:
            JSON string of usage report
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'daily_budget': self.daily_budget,
            'budget_status': self.check_budget_status(),
            'total_cost_24h': self.get_total_cost(24),
            'agent_summaries': {
                name: summary.to_dict()
                for name, summary in self.get_all_agents_summary().items()
            },
            'optimization_tips': self.get_cost_optimization_tips()
        }

        json_data = json.dumps(report, indent=2, default=str)

        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_data)
            logger.info(f"📁 Usage report exported to {filepath}")

        return json_data


# Global cost tracker instance
global_cost_tracker = CostTracker()
