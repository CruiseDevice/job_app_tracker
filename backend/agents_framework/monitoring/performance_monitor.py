"""
Performance monitoring system for agents.

This module provides comprehensive performance tracking including:
- Execution time monitoring
- Success/failure rate tracking
- Response time analysis
- Error rate monitoring
- Historical performance data
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from enum import Enum
import json

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics tracked."""
    EXECUTION_TIME = "execution_time"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    TOKEN_USAGE = "token_usage"
    COST = "cost"
    RESPONSE_TIME = "response_time"


@dataclass
class AgentMetrics:
    """Metrics for a single agent execution."""
    agent_name: str
    execution_id: str
    timestamp: datetime
    execution_time: float  # seconds
    success: bool
    error: Optional[str] = None
    tokens_used: int = 0
    cost: float = 0.0
    tool_calls: int = 0
    memory_used: int = 0  # bytes
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for an agent over a time period."""
    agent_name: str
    period_start: datetime
    period_end: datetime
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time: float
    max_execution_time: float
    min_execution_time: float
    total_tokens_used: int
    total_cost: float
    avg_tokens_per_execution: float
    avg_cost_per_execution: float
    success_rate: float
    error_rate: float
    total_tool_calls: int
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregated metrics to dictionary."""
        data = asdict(self)
        data['period_start'] = self.period_start.isoformat()
        data['period_end'] = self.period_end.isoformat()
        return data


class PerformanceMonitor:
    """
    Performance monitoring system for tracking agent metrics.

    Features:
    - Real-time metric collection
    - Historical data storage
    - Aggregated statistics
    - Performance alerts
    - Trend analysis
    """

    def __init__(self, max_history: int = 10000):
        """
        Initialize performance monitor.

        Args:
            max_history: Maximum number of metrics to keep in memory
        """
        self.metrics: Dict[str, List[AgentMetrics]] = defaultdict(list)
        self.max_history = max_history
        self._execution_contexts: Dict[str, Dict[str, Any]] = {}
        logger.info("🔍 Performance Monitor initialized")

    def start_execution(self, agent_name: str, execution_id: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Start tracking an agent execution.

        Args:
            agent_name: Name of the agent
            execution_id: Unique execution identifier
            context: Optional context data
        """
        self._execution_contexts[execution_id] = {
            'agent_name': agent_name,
            'start_time': time.time(),
            'context': context or {}
        }
        logger.debug(f"📊 Started tracking execution {execution_id} for {agent_name}")

    def end_execution(
        self,
        execution_id: str,
        success: bool,
        error: Optional[str] = None,
        tokens_used: int = 0,
        cost: float = 0.0,
        tool_calls: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentMetrics:
        """
        End tracking an agent execution and record metrics.

        Args:
            execution_id: Unique execution identifier
            success: Whether execution was successful
            error: Error message if failed
            tokens_used: Number of tokens used
            cost: Cost of execution
            tool_calls: Number of tool calls made
            metadata: Additional metadata

        Returns:
            AgentMetrics object with recorded metrics
        """
        if execution_id not in self._execution_contexts:
            logger.warning(f"⚠️ No context found for execution {execution_id}")
            return None

        context = self._execution_contexts.pop(execution_id)
        execution_time = time.time() - context['start_time']
        agent_name = context['agent_name']

        metrics = AgentMetrics(
            agent_name=agent_name,
            execution_id=execution_id,
            timestamp=datetime.now(),
            execution_time=execution_time,
            success=success,
            error=error,
            tokens_used=tokens_used,
            cost=cost,
            tool_calls=tool_calls,
            metadata=metadata or {}
        )

        # Store metrics
        self.metrics[agent_name].append(metrics)

        # Trim history if needed
        if len(self.metrics[agent_name]) > self.max_history:
            self.metrics[agent_name] = self.metrics[agent_name][-self.max_history:]

        status_icon = "✅" if success else "❌"
        logger.info(
            f"{status_icon} Agent {agent_name} execution {execution_id}: "
            f"{execution_time:.2f}s, {tokens_used} tokens, ${cost:.4f}"
        )

        return metrics

    def get_agent_metrics(
        self,
        agent_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AgentMetrics]:
        """
        Get metrics for a specific agent within a time range.

        Args:
            agent_name: Name of the agent
            start_time: Start of time range (inclusive)
            end_time: End of time range (inclusive)

        Returns:
            List of AgentMetrics
        """
        metrics = self.metrics.get(agent_name, [])

        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]

        return metrics

    def get_aggregated_metrics(
        self,
        agent_name: str,
        period_hours: int = 24
    ) -> Optional[AggregatedMetrics]:
        """
        Get aggregated metrics for an agent over a time period.

        Args:
            agent_name: Name of the agent
            period_hours: Time period in hours to aggregate

        Returns:
            AggregatedMetrics object or None if no data
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=period_hours)

        metrics = self.get_agent_metrics(agent_name, start_time, end_time)

        if not metrics:
            return None

        successful = [m for m in metrics if m.success]
        failed = [m for m in metrics if not m.success]
        execution_times = [m.execution_time for m in metrics]

        return AggregatedMetrics(
            agent_name=agent_name,
            period_start=start_time,
            period_end=end_time,
            total_executions=len(metrics),
            successful_executions=len(successful),
            failed_executions=len(failed),
            avg_execution_time=sum(execution_times) / len(execution_times),
            max_execution_time=max(execution_times),
            min_execution_time=min(execution_times),
            total_tokens_used=sum(m.tokens_used for m in metrics),
            total_cost=sum(m.cost for m in metrics),
            avg_tokens_per_execution=sum(m.tokens_used for m in metrics) / len(metrics),
            avg_cost_per_execution=sum(m.cost for m in metrics) / len(metrics),
            success_rate=len(successful) / len(metrics) * 100,
            error_rate=len(failed) / len(metrics) * 100,
            total_tool_calls=sum(m.tool_calls for m in metrics),
            errors=[m.error for m in failed if m.error]
        )

    def get_all_agents_summary(self, period_hours: int = 24) -> Dict[str, AggregatedMetrics]:
        """
        Get aggregated metrics summary for all agents.

        Args:
            period_hours: Time period in hours to aggregate

        Returns:
            Dictionary mapping agent names to their aggregated metrics
        """
        summary = {}
        for agent_name in self.metrics.keys():
            agg_metrics = self.get_aggregated_metrics(agent_name, period_hours)
            if agg_metrics:
                summary[agent_name] = agg_metrics
        return summary

    def get_performance_alerts(self, thresholds: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """
        Get performance alerts based on thresholds.

        Args:
            thresholds: Dictionary of metric thresholds

        Returns:
            List of alert dictionaries
        """
        default_thresholds = {
            'max_error_rate': 10.0,  # 10% error rate
            'max_avg_execution_time': 30.0,  # 30 seconds
            'max_avg_cost': 0.50,  # $0.50 per execution
        }
        thresholds = thresholds or default_thresholds

        alerts = []
        summary = self.get_all_agents_summary()

        for agent_name, metrics in summary.items():
            # Check error rate
            if metrics.error_rate > thresholds.get('max_error_rate', 10.0):
                alerts.append({
                    'agent': agent_name,
                    'type': 'high_error_rate',
                    'severity': 'high',
                    'message': f"Error rate {metrics.error_rate:.1f}% exceeds threshold",
                    'value': metrics.error_rate,
                    'threshold': thresholds['max_error_rate']
                })

            # Check execution time
            if metrics.avg_execution_time > thresholds.get('max_avg_execution_time', 30.0):
                alerts.append({
                    'agent': agent_name,
                    'type': 'slow_execution',
                    'severity': 'medium',
                    'message': f"Average execution time {metrics.avg_execution_time:.2f}s is slow",
                    'value': metrics.avg_execution_time,
                    'threshold': thresholds['max_avg_execution_time']
                })

            # Check cost
            if metrics.avg_cost_per_execution > thresholds.get('max_avg_cost', 0.50):
                alerts.append({
                    'agent': agent_name,
                    'type': 'high_cost',
                    'severity': 'medium',
                    'message': f"Average cost ${metrics.avg_cost_per_execution:.4f} is high",
                    'value': metrics.avg_cost_per_execution,
                    'threshold': thresholds['max_avg_cost']
                })

        return alerts

    def export_metrics(self, agent_name: Optional[str] = None, filepath: Optional[str] = None) -> str:
        """
        Export metrics to JSON format.

        Args:
            agent_name: Specific agent to export (None for all)
            filepath: Optional file path to save (None returns JSON string)

        Returns:
            JSON string of exported metrics
        """
        if agent_name:
            data = {
                'agent': agent_name,
                'metrics': [m.to_dict() for m in self.metrics.get(agent_name, [])]
            }
        else:
            data = {
                'agents': {
                    name: [m.to_dict() for m in metrics]
                    for name, metrics in self.metrics.items()
                }
            }

        json_data = json.dumps(data, indent=2, default=str)

        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_data)
            logger.info(f"📁 Metrics exported to {filepath}")

        return json_data

    def clear_metrics(self, agent_name: Optional[str] = None) -> None:
        """
        Clear stored metrics.

        Args:
            agent_name: Specific agent to clear (None clears all)
        """
        if agent_name:
            self.metrics[agent_name] = []
            logger.info(f"🗑️ Cleared metrics for {agent_name}")
        else:
            self.metrics.clear()
            logger.info("🗑️ Cleared all metrics")


# Global performance monitor instance
global_performance_monitor = PerformanceMonitor()
