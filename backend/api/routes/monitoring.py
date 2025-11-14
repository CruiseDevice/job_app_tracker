"""
API routes for agent monitoring and performance tracking.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from ...agents_framework.monitoring.performance_monitor import global_performance_monitor
from ...agents_framework.monitoring.cost_tracker import global_cost_tracker

router = APIRouter()


# Response Models
class MetricsResponse(BaseModel):
    """Response model for metrics data."""
    agent_name: str
    metrics: List[Dict[str, Any]]


class AggregatedMetricsResponse(BaseModel):
    """Response model for aggregated metrics."""
    agent_name: str
    period_start: str
    period_end: str
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
    errors: List[str]


class CostSummaryResponse(BaseModel):
    """Response model for cost summary."""
    agent_name: str
    period_start: str
    period_end: str
    total_calls: int
    total_tokens: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost: float
    avg_cost_per_call: float
    avg_tokens_per_call: float
    model_breakdown: Dict[str, Dict[str, Any]]


class AlertResponse(BaseModel):
    """Response model for alerts."""
    agent: str
    type: str
    severity: str
    message: str
    value: float
    threshold: float


class BudgetStatusResponse(BaseModel):
    """Response model for budget status."""
    budget_enabled: bool
    daily_budget: Optional[float] = None
    cost_today: Optional[float] = None
    remaining_budget: Optional[float] = None
    budget_used_percent: Optional[float] = None
    alerts: List[Dict[str, Any]] = []


# Performance Monitoring Endpoints

@router.get("/performance/agents", tags=["monitoring"])
async def get_all_agents_performance(
    period_hours: int = Query(24, ge=1, le=168, description="Time period in hours")
) -> Dict[str, AggregatedMetricsResponse]:
    """
    Get performance summary for all agents.

    Args:
        period_hours: Time period in hours (1-168)

    Returns:
        Dictionary of agent performance summaries
    """
    try:
        summary = global_performance_monitor.get_all_agents_summary(period_hours)
        return {
            name: AggregatedMetricsResponse(**metrics.to_dict())
            for name, metrics in summary.items()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance data: {str(e)}")


@router.get("/performance/agents/{agent_name}", tags=["monitoring"])
async def get_agent_performance(
    agent_name: str,
    period_hours: int = Query(24, ge=1, le=168, description="Time period in hours")
) -> AggregatedMetricsResponse:
    """
    Get performance metrics for a specific agent.

    Args:
        agent_name: Name of the agent
        period_hours: Time period in hours (1-168)

    Returns:
        Aggregated performance metrics
    """
    try:
        metrics = global_performance_monitor.get_aggregated_metrics(agent_name, period_hours)
        if not metrics:
            raise HTTPException(status_code=404, detail=f"No metrics found for agent '{agent_name}'")
        return AggregatedMetricsResponse(**metrics.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance data: {str(e)}")


@router.get("/performance/agents/{agent_name}/raw", tags=["monitoring"])
async def get_agent_raw_metrics(
    agent_name: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of metrics to return")
) -> MetricsResponse:
    """
    Get raw metrics data for a specific agent.

    Args:
        agent_name: Name of the agent
        limit: Maximum number of metrics to return

    Returns:
        List of raw metrics
    """
    try:
        metrics = global_performance_monitor.get_agent_metrics(agent_name)
        if not metrics:
            raise HTTPException(status_code=404, detail=f"No metrics found for agent '{agent_name}'")

        # Return most recent metrics
        recent_metrics = metrics[-limit:]
        return MetricsResponse(
            agent_name=agent_name,
            metrics=[m.to_dict() for m in recent_metrics]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get raw metrics: {str(e)}")


@router.get("/performance/alerts", tags=["monitoring"])
async def get_performance_alerts(
    max_error_rate: float = Query(10.0, description="Maximum error rate threshold (%)"),
    max_avg_execution_time: float = Query(30.0, description="Maximum average execution time (seconds)"),
    max_avg_cost: float = Query(0.50, description="Maximum average cost per execution ($)")
) -> List[AlertResponse]:
    """
    Get performance alerts based on thresholds.

    Args:
        max_error_rate: Maximum error rate threshold (%)
        max_avg_execution_time: Maximum average execution time (seconds)
        max_avg_cost: Maximum average cost per execution ($)

    Returns:
        List of performance alerts
    """
    try:
        thresholds = {
            'max_error_rate': max_error_rate,
            'max_avg_execution_time': max_avg_execution_time,
            'max_avg_cost': max_avg_cost
        }
        alerts = global_performance_monitor.get_performance_alerts(thresholds)
        return [AlertResponse(**alert) for alert in alerts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


# Cost Tracking Endpoints

@router.get("/costs/agents", tags=["monitoring", "costs"])
async def get_all_agents_costs(
    period_hours: int = Query(24, ge=1, le=168, description="Time period in hours")
) -> Dict[str, CostSummaryResponse]:
    """
    Get cost summary for all agents.

    Args:
        period_hours: Time period in hours (1-168)

    Returns:
        Dictionary of agent cost summaries
    """
    try:
        summary = global_cost_tracker.get_all_agents_summary(period_hours)
        return {
            name: CostSummaryResponse(**cost_summary.to_dict())
            for name, cost_summary in summary.items()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cost data: {str(e)}")


@router.get("/costs/agents/{agent_name}", tags=["monitoring", "costs"])
async def get_agent_costs(
    agent_name: str,
    period_hours: int = Query(24, ge=1, le=168, description="Time period in hours")
) -> CostSummaryResponse:
    """
    Get cost summary for a specific agent.

    Args:
        agent_name: Name of the agent
        period_hours: Time period in hours (1-168)

    Returns:
        Cost summary for the agent
    """
    try:
        summary = global_cost_tracker.get_agent_summary(agent_name, period_hours)
        if not summary:
            raise HTTPException(status_code=404, detail=f"No cost data found for agent '{agent_name}'")
        return CostSummaryResponse(**summary.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cost data: {str(e)}")


@router.get("/costs/total", tags=["monitoring", "costs"])
async def get_total_costs(
    period_hours: int = Query(24, ge=1, le=168, description="Time period in hours")
) -> Dict[str, float]:
    """
    Get total costs across all agents.

    Args:
        period_hours: Time period in hours (1-168)

    Returns:
        Dictionary with total cost
    """
    try:
        total_cost = global_cost_tracker.get_total_cost(period_hours)
        return {
            "period_hours": period_hours,
            "total_cost": total_cost
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get total cost: {str(e)}")


@router.get("/costs/budget/status", tags=["monitoring", "costs"])
async def get_budget_status() -> BudgetStatusResponse:
    """
    Get current budget status and alerts.

    Returns:
        Budget status information
    """
    try:
        status = global_cost_tracker.check_budget_status()
        return BudgetStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get budget status: {str(e)}")


@router.get("/costs/optimization/tips", tags=["monitoring", "costs"])
async def get_optimization_tips() -> List[Dict[str, Any]]:
    """
    Get cost optimization recommendations.

    Returns:
        List of optimization tips
    """
    try:
        tips = global_cost_tracker.get_cost_optimization_tips()
        return tips
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get optimization tips: {str(e)}")


@router.post("/costs/budget/set", tags=["monitoring", "costs"])
async def set_daily_budget(budget: float = Query(..., ge=0, description="Daily budget in USD")) -> Dict[str, Any]:
    """
    Set daily budget limit.

    Args:
        budget: Daily budget in USD

    Returns:
        Success message with new budget
    """
    try:
        global_cost_tracker.daily_budget = budget
        return {
            "success": True,
            "message": f"Daily budget set to ${budget:.2f}",
            "daily_budget": budget
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set budget: {str(e)}")


# Export and Utility Endpoints

@router.get("/export/metrics", tags=["monitoring"])
async def export_metrics(agent_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Export performance metrics as JSON.

    Args:
        agent_name: Optional agent name (exports all if not specified)

    Returns:
        JSON metrics data
    """
    try:
        json_str = global_performance_monitor.export_metrics(agent_name)
        import json
        return json.loads(json_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export metrics: {str(e)}")


@router.get("/export/costs", tags=["monitoring", "costs"])
async def export_cost_report() -> Dict[str, Any]:
    """
    Export cost usage report as JSON.

    Returns:
        JSON cost report
    """
    try:
        json_str = global_cost_tracker.export_usage_report()
        import json
        return json.loads(json_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export cost report: {str(e)}")


@router.get("/health", tags=["monitoring"])
async def monitoring_health() -> Dict[str, Any]:
    """
    Get monitoring system health status.

    Returns:
        Health status information
    """
    try:
        perf_summary = global_performance_monitor.get_all_agents_summary(24)
        cost_summary = global_cost_tracker.get_all_agents_summary(24)

        return {
            "status": "healthy",
            "monitoring_active": True,
            "agents_monitored": len(perf_summary),
            "total_executions_24h": sum(m.total_executions for m in perf_summary.values()),
            "total_cost_24h": global_cost_tracker.get_total_cost(24),
            "budget_status": global_cost_tracker.check_budget_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
