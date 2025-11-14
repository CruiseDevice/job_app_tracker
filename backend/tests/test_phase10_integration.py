"""
Integration tests for Phase 10: Polish & Optimization

Tests all monitoring, cost tracking, explainability, and error handling systems.
"""

import pytest
import asyncio
from datetime import datetime
from typing import List

# Import monitoring systems
from agents_framework.monitoring.performance_monitor import (
    PerformanceMonitor,
    AgentMetrics,
    global_performance_monitor
)
from agents_framework.monitoring.cost_tracker import (
    CostTracker,
    TokenUsage,
    ModelType,
    global_cost_tracker
)
from agents_framework.monitoring.structured_logger import (
    StructuredLogger,
    create_log_context,
    LogContext
)

# Import explainability systems
from agents_framework.explainability.decision_explainer import (
    DecisionExplainer,
    ReasoningType,
    ConfidenceLevel,
    global_decision_explainer
)
from agents_framework.explainability.explanation_formatter import (
    ExplanationFormatter,
    ExplanationFormat
)

# Import failsafe systems
from agents_framework.failsafe.retry_handler import (
    RetryHandler,
    RetryPolicy,
    BackoffStrategy,
    with_retry
)
from agents_framework.failsafe.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitBreakerError,
    with_circuit_breaker
)
from agents_framework.failsafe.error_handler import (
    ErrorHandler,
    ErrorSeverity,
    ErrorCategory,
    ErrorRecoveryStrategy,
    global_error_handler
)


class TestPerformanceMonitoring:
    """Test performance monitoring system."""

    def test_performance_monitor_initialization(self):
        """Test performance monitor can be initialized."""
        monitor = PerformanceMonitor()
        assert monitor is not None
        assert len(monitor.metrics) == 0

    def test_execution_tracking(self):
        """Test tracking agent execution."""
        monitor = PerformanceMonitor()

        # Start execution
        monitor.start_execution("TestAgent", "exec-1", {"test": "context"})
        assert "exec-1" in monitor._execution_contexts

        # End execution
        metrics = monitor.end_execution(
            execution_id="exec-1",
            success=True,
            tokens_used=1000,
            cost=0.0015,
            tool_calls=3
        )

        assert metrics is not None
        assert metrics.agent_name == "TestAgent"
        assert metrics.success is True
        assert metrics.tokens_used == 1000
        assert metrics.cost == 0.0015
        assert metrics.tool_calls == 3

    def test_aggregated_metrics(self):
        """Test aggregated metrics calculation."""
        monitor = PerformanceMonitor()

        # Create multiple executions
        for i in range(5):
            monitor.start_execution("TestAgent", f"exec-{i}")
            monitor.end_execution(
                execution_id=f"exec-{i}",
                success=i < 4,  # 4 successes, 1 failure
                tokens_used=1000 + i * 100,
                cost=0.001 + i * 0.0001,
                tool_calls=2
            )

        # Get aggregated metrics
        agg = monitor.get_aggregated_metrics("TestAgent", period_hours=24)

        assert agg is not None
        assert agg.total_executions == 5
        assert agg.successful_executions == 4
        assert agg.failed_executions == 1
        assert agg.success_rate == 80.0
        assert agg.total_tool_calls == 10

    def test_performance_alerts(self):
        """Test performance alert generation."""
        monitor = PerformanceMonitor()

        # Create executions with high error rate
        for i in range(10):
            monitor.start_execution("FailingAgent", f"exec-{i}")
            monitor.end_execution(
                execution_id=f"exec-{i}",
                success=i < 2,  # 20% success rate (80% error rate)
                tokens_used=1000,
                cost=0.001
            )

        # Get alerts with 10% error threshold
        alerts = monitor.get_performance_alerts({'max_error_rate': 10.0})

        # Should have alert for high error rate
        assert len(alerts) > 0
        assert any(a['type'] == 'high_error_rate' for a in alerts)


class TestCostTracking:
    """Test cost tracking system."""

    def test_cost_tracker_initialization(self):
        """Test cost tracker can be initialized."""
        tracker = CostTracker()
        assert tracker is not None

    def test_cost_calculation(self):
        """Test cost calculation for different models."""
        tracker = CostTracker()

        # Test GPT-4O-Mini (cheapest)
        usage = tracker.calculate_cost("gpt-4o-mini", 1000, 500)
        assert usage.input_tokens == 1000
        assert usage.output_tokens == 500
        assert usage.total_tokens == 1500
        assert usage.input_cost > 0
        assert usage.output_cost > 0
        assert usage.total_cost == usage.input_cost + usage.output_cost

        # Test GPT-4O (more expensive)
        usage_4o = tracker.calculate_cost("gpt-4o", 1000, 500)
        assert usage_4o.total_cost > usage.total_cost

    def test_usage_tracking(self):
        """Test tracking token usage."""
        tracker = CostTracker()

        usage = tracker.track_usage(
            agent_name="TestAgent",
            model="gpt-4o-mini",
            input_tokens=1000,
            output_tokens=500
        )

        assert usage.total_cost > 0
        assert "TestAgent" in tracker.usage_history
        assert len(tracker.usage_history["TestAgent"]) == 1

    def test_cost_summary(self):
        """Test cost summary generation."""
        tracker = CostTracker()

        # Track multiple uses
        for i in range(5):
            tracker.track_usage("TestAgent", "gpt-4o-mini", 1000, 500)

        summary = tracker.get_agent_summary("TestAgent", period_hours=24)

        assert summary is not None
        assert summary.total_calls == 5
        assert summary.total_tokens == 7500  # 1500 * 5
        assert summary.total_cost > 0

    def test_budget_monitoring(self):
        """Test budget monitoring and alerts."""
        tracker = CostTracker(daily_budget=1.00)

        # Use up budget
        for i in range(100):
            tracker.track_usage("ExpensiveAgent", "gpt-4o", 10000, 5000)

        status = tracker.check_budget_status()

        assert status['budget_enabled'] is True
        assert status['daily_budget'] == 1.00
        assert status['cost_today'] > 0
        assert len(status['alerts']) > 0

    def test_optimization_tips(self):
        """Test cost optimization recommendations."""
        tracker = CostTracker()

        # Use expensive model extensively
        for i in range(10):
            tracker.track_usage("ExpensiveAgent", "gpt-4o", 5000, 2500)

        tips = tracker.get_cost_optimization_tips()

        # Should suggest using cheaper model
        assert len(tips) > 0


class TestDecisionExplainability:
    """Test decision explanation system."""

    def test_explainer_initialization(self):
        """Test explainer can be initialized."""
        explainer = DecisionExplainer()
        assert explainer is not None

    def test_create_explanation(self):
        """Test creating decision explanation."""
        explainer = DecisionExplainer()

        explanation = explainer.create_explanation(
            agent_name="TestAgent",
            execution_id="exec-1",
            decision="Test decision",
            confidence_score=0.85
        )

        assert explanation is not None
        assert explanation.agent_name == "TestAgent"
        assert explanation.decision == "Test decision"
        assert explanation.confidence == ConfidenceLevel.HIGH
        assert explanation.confidence_score == 0.85

    def test_add_reasoning_steps(self):
        """Test adding reasoning steps."""
        explainer = DecisionExplainer()

        explainer.create_explanation("TestAgent", "exec-1", "Decision", 0.8)

        # Add reasoning steps
        explainer.add_reasoning_step(
            "exec-1",
            ReasoningType.OBSERVATION,
            "Observed key pattern"
        )
        explainer.add_reasoning_step(
            "exec-1",
            ReasoningType.THOUGHT,
            "Considered implications"
        )
        explainer.add_reasoning_step(
            "exec-1",
            ReasoningType.DECISION,
            "Made final decision"
        )

        explanation = explainer.get_explanation("exec-1")
        assert len(explanation.reasoning_steps) == 3

    def test_add_tool_usage(self):
        """Test adding tool usage explanations."""
        explainer = DecisionExplainer()

        explainer.create_explanation("TestAgent", "exec-1", "Decision", 0.8)

        explainer.add_tool_usage(
            "exec-1",
            tool_name="test_tool",
            reason="To analyze data",
            inputs={"data": "test"},
            expected_outcome="Analysis result",
            actual_outcome="Success",
            success=True
        )

        explanation = explainer.get_explanation("exec-1")
        assert len(explanation.tool_usage) == 1
        assert explanation.tool_usage[0].tool_name == "test_tool"

    def test_explanation_formatting(self):
        """Test formatting explanations in different formats."""
        explainer = DecisionExplainer()

        explanation = explainer.create_explanation(
            "TestAgent", "exec-1", "Decision", 0.9
        )
        explainer.add_reasoning_step(
            "exec-1",
            ReasoningType.OBSERVATION,
            "Test observation"
        )

        # Test different formats
        markdown = ExplanationFormatter.format(explanation, ExplanationFormat.MARKDOWN)
        assert "# Decision Explanation" in markdown
        assert "Test observation" in markdown

        html = ExplanationFormatter.format(explanation, ExplanationFormat.HTML)
        assert "<h1>" in html
        assert "Test observation" in html

        plain = ExplanationFormatter.format(explanation, ExplanationFormat.PLAIN_TEXT)
        assert "Decision Explanation" in plain
        assert "Test observation" in plain


class TestRetryHandler:
    """Test retry handler system."""

    def test_retry_handler_initialization(self):
        """Test retry handler can be initialized."""
        handler = RetryHandler()
        assert handler is not None

    @pytest.mark.asyncio
    async def test_successful_execution_no_retry(self):
        """Test successful execution requires no retry."""
        handler = RetryHandler(RetryPolicy(max_retries=3))

        call_count = 0

        async def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await handler.execute_async(successful_function)

        assert result == "success"
        assert call_count == 1  # Called only once

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test retry logic on failure."""
        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0.1,  # Short delay for testing
            backoff_strategy=BackoffStrategy.FIXED
        )
        handler = RetryHandler(policy)

        call_count = 0

        async def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"

        result = await handler.execute_async(failing_then_success)

        assert result == "success"
        assert call_count == 3  # Failed twice, succeeded on third

    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """Test behavior when all retries are exhausted."""
        policy = RetryPolicy(max_retries=2, initial_delay=0.1)
        handler = RetryHandler(policy)

        async def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            await handler.execute_async(always_fails)

    @pytest.mark.asyncio
    async def test_retry_decorator(self):
        """Test retry decorator."""
        call_count = 0

        @with_retry(RetryPolicy(max_retries=2, initial_delay=0.1))
        async def decorated_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Fail")
            return "success"

        result = await decorated_function()
        assert result == "success"
        assert call_count == 2


class TestCircuitBreaker:
    """Test circuit breaker system."""

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker can be initialized."""
        circuit = CircuitBreaker("test", CircuitBreakerConfig())
        assert circuit is not None
        assert circuit.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self):
        """Test circuit opens after threshold failures."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            timeout=1.0
        )
        circuit = CircuitBreaker("test", config)

        async def failing_function():
            raise ConnectionError("Service unavailable")

        # Fail threshold times
        for _ in range(3):
            try:
                await circuit.execute_async(failing_function)
            except ConnectionError:
                pass

        # Circuit should be open
        assert circuit.state == CircuitState.OPEN

        # Next call should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            await circuit.execute_async(failing_function)

    @pytest.mark.asyncio
    async def test_circuit_recovery(self):
        """Test circuit recovery to half-open and closed."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout=0.5  # Short timeout for testing
        )
        circuit = CircuitBreaker("test", config)

        call_count = 0

        async def sometimes_fails():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ConnectionError("Fail")
            return "success"

        # Open the circuit
        for _ in range(2):
            try:
                await circuit.execute_async(sometimes_fails)
            except ConnectionError:
                pass

        assert circuit.state == CircuitState.OPEN

        # Wait for timeout
        await asyncio.sleep(0.6)

        # Should be half-open now, allow test
        result = await circuit.execute_async(sometimes_fails)
        assert circuit.state == CircuitState.HALF_OPEN

        # One more success should close circuit
        result = await circuit.execute_async(sometimes_fails)
        assert circuit.state == CircuitState.CLOSED


class TestErrorHandler:
    """Test error handler system."""

    def test_error_handler_initialization(self):
        """Test error handler can be initialized."""
        handler = ErrorHandler()
        assert handler is not None

    def test_error_classification(self):
        """Test error classification."""
        handler = ErrorHandler()

        # Network error
        network_error = ConnectionError("Network issue")
        category = handler.classify_error(network_error)
        assert category == ErrorCategory.NETWORK

        # Timeout error
        timeout_error = TimeoutError("Timeout")
        category = handler.classify_error(timeout_error)
        assert category == ErrorCategory.TIMEOUT

        # Validation error
        validation_error = ValueError("Invalid value")
        category = handler.classify_error(validation_error)
        assert category == ErrorCategory.VALIDATION

    def test_severity_assessment(self):
        """Test error severity assessment."""
        handler = ErrorHandler()

        # Critical error
        severity = handler.assess_severity(
            Exception("Config error"),
            ErrorCategory.CONFIGURATION
        )
        assert severity == ErrorSeverity.CRITICAL

        # Medium error
        severity = handler.assess_severity(
            Exception("Rate limit"),
            ErrorCategory.RATE_LIMIT
        )
        assert severity == ErrorSeverity.MEDIUM

    def test_recovery_strategy_determination(self):
        """Test recovery strategy determination."""
        handler = ErrorHandler()

        # Should retry on network errors
        strategy = handler.determine_recovery_strategy(
            ErrorCategory.NETWORK,
            ErrorSeverity.MEDIUM
        )
        assert strategy == ErrorRecoveryStrategy.RETRY

        # Should escalate critical errors
        strategy = handler.determine_recovery_strategy(
            ErrorCategory.CONFIGURATION,
            ErrorSeverity.CRITICAL
        )
        assert strategy == ErrorRecoveryStrategy.ESCALATE

    def test_error_handling_and_tracking(self):
        """Test error handling and history tracking."""
        handler = ErrorHandler()

        try:
            raise ValueError("Test error")
        except Exception as e:
            error_info = handler.handle_error(
                e,
                context={"test": "context"}
            )

        assert error_info is not None
        assert error_info.exception_type == "ValueError"
        assert error_info.message == "Test error"
        assert len(handler.error_history) == 1

        # Test stats
        stats = handler.get_error_stats()
        assert stats['total_errors'] == 1


class TestIntegration:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_full_monitoring_pipeline(self):
        """Test complete monitoring pipeline from execution to metrics."""
        # Clear existing data
        monitor = PerformanceMonitor()
        monitor.clear_metrics()

        # Simulate agent execution
        execution_id = "integration-test-1"
        monitor.start_execution("IntegrationAgent", execution_id)

        # Simulate some work
        await asyncio.sleep(0.1)

        # End execution
        metrics = monitor.end_execution(
            execution_id=execution_id,
            success=True,
            tokens_used=1500,
            cost=0.0023,
            tool_calls=2
        )

        # Verify metrics were recorded
        assert metrics is not None
        assert metrics.execution_time >= 0.1

        # Get aggregated metrics
        agg = monitor.get_aggregated_metrics("IntegrationAgent", period_hours=1)
        assert agg is not None
        assert agg.total_executions == 1

    def test_cost_and_performance_correlation(self):
        """Test that cost tracking correlates with performance metrics."""
        monitor = PerformanceMonitor()
        tracker = CostTracker()

        # Track execution
        execution_id = "cost-perf-test"
        monitor.start_execution("TestAgent", execution_id)

        # Track cost
        usage = tracker.track_usage("TestAgent", "gpt-4o-mini", 1000, 500)

        # End execution with same cost
        metrics = monitor.end_execution(
            execution_id=execution_id,
            success=True,
            tokens_used=1500,
            cost=usage.total_cost
        )

        # Verify correlation
        assert metrics.tokens_used == usage.total_tokens
        assert metrics.cost == usage.total_cost

    def test_error_handling_with_retry(self):
        """Test error handling integrated with retry logic."""
        handler = ErrorHandler()
        policy = RetryPolicy(max_retries=2, initial_delay=0.1)
        retry_handler = RetryHandler(policy)

        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                error = ConnectionError("Temporary failure")
                handler.handle_error(error, context={"attempt": call_count})
                raise error
            return "success"

        # Should succeed after retries
        result = retry_handler.execute_sync(failing_function)
        assert result == "success"

        # Should have error history
        stats = handler.get_error_stats()
        assert stats['total_errors'] == 2  # Failed twice before success


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
