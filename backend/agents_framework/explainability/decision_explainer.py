"""
Decision explanation system for agents.

Provides transparent explanations of agent decisions including:
- Reasoning steps
- Tool usage justification
- Confidence scores
- Alternative options considered
- Decision rationale
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ReasoningType(str, Enum):
    """Types of reasoning steps."""
    OBSERVATION = "observation"
    THOUGHT = "thought"
    ACTION = "action"
    TOOL_CALL = "tool_call"
    EVALUATION = "evaluation"
    DECISION = "decision"


class ConfidenceLevel(str, Enum):
    """Confidence levels for decisions."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ReasoningStep:
    """A single step in the reasoning process."""
    step_number: int
    reasoning_type: ReasoningType
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['reasoning_type'] = self.reasoning_type.value
        return data


@dataclass
class ToolUsageExplanation:
    """Explanation for why a tool was used."""
    tool_name: str
    reason: str
    inputs: Dict[str, Any]
    expected_outcome: str
    actual_outcome: Optional[str] = None
    success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AlternativeOption:
    """An alternative option that was considered."""
    description: str
    pros: List[str]
    cons: List[str]
    confidence: float
    reason_not_chosen: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DecisionExplanation:
    """Complete explanation of an agent's decision."""
    agent_name: str
    execution_id: str
    decision: str
    confidence: ConfidenceLevel
    confidence_score: float  # 0.0 to 1.0
    reasoning_steps: List[ReasoningStep]
    tool_usage: List[ToolUsageExplanation]
    alternatives_considered: List[AlternativeOption]
    key_factors: List[str]
    assumptions: List[str]
    limitations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'agent_name': self.agent_name,
            'execution_id': self.execution_id,
            'decision': self.decision,
            'confidence': self.confidence.value,
            'confidence_score': self.confidence_score,
            'reasoning_steps': [step.to_dict() for step in self.reasoning_steps],
            'tool_usage': [tool.to_dict() for tool in self.tool_usage],
            'alternatives_considered': [alt.to_dict() for alt in self.alternatives_considered],
            'key_factors': self.key_factors,
            'assumptions': self.assumptions,
            'limitations': self.limitations,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class DecisionExplainer:
    """
    System for generating explanations of agent decisions.

    Features:
    - Tracks reasoning process
    - Explains tool usage
    - Documents alternatives considered
    - Provides confidence scores
    - Identifies key factors and assumptions
    """

    def __init__(self):
        """Initialize decision explainer."""
        self.explanations: Dict[str, DecisionExplanation] = {}
        logger.info("🔍 Decision Explainer initialized")

    def create_explanation(
        self,
        agent_name: str,
        execution_id: str,
        decision: str,
        confidence_score: float = 0.8
    ) -> DecisionExplanation:
        """
        Create a new decision explanation.

        Args:
            agent_name: Name of the agent
            execution_id: Execution identifier
            decision: The decision made
            confidence_score: Confidence score (0.0-1.0)

        Returns:
            DecisionExplanation object
        """
        # Map confidence score to level
        if confidence_score >= 0.9:
            confidence_level = ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.7:
            confidence_level = ConfidenceLevel.HIGH
        elif confidence_score >= 0.5:
            confidence_level = ConfidenceLevel.MEDIUM
        elif confidence_score >= 0.3:
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.VERY_LOW

        explanation = DecisionExplanation(
            agent_name=agent_name,
            execution_id=execution_id,
            decision=decision,
            confidence=confidence_level,
            confidence_score=confidence_score,
            reasoning_steps=[],
            tool_usage=[],
            alternatives_considered=[],
            key_factors=[],
            assumptions=[],
            limitations=[]
        )

        self.explanations[execution_id] = explanation
        logger.info(f"📝 Created explanation for {agent_name} execution {execution_id}")
        return explanation

    def add_reasoning_step(
        self,
        execution_id: str,
        reasoning_type: ReasoningType,
        content: str,
        **metadata
    ) -> None:
        """
        Add a reasoning step to the explanation.

        Args:
            execution_id: Execution identifier
            reasoning_type: Type of reasoning
            content: Description of the step
            **metadata: Additional metadata
        """
        if execution_id not in self.explanations:
            logger.warning(f"⚠️ No explanation found for execution {execution_id}")
            return

        explanation = self.explanations[execution_id]
        step = ReasoningStep(
            step_number=len(explanation.reasoning_steps) + 1,
            reasoning_type=reasoning_type,
            content=content,
            metadata=metadata
        )
        explanation.reasoning_steps.append(step)
        logger.debug(f"Added reasoning step {step.step_number} to {execution_id}")

    def add_tool_usage(
        self,
        execution_id: str,
        tool_name: str,
        reason: str,
        inputs: Dict[str, Any],
        expected_outcome: str,
        actual_outcome: Optional[str] = None,
        success: bool = True
    ) -> None:
        """
        Add tool usage explanation.

        Args:
            execution_id: Execution identifier
            tool_name: Name of the tool used
            reason: Why the tool was used
            inputs: Tool inputs
            expected_outcome: Expected outcome
            actual_outcome: Actual outcome
            success: Whether tool call was successful
        """
        if execution_id not in self.explanations:
            logger.warning(f"⚠️ No explanation found for execution {execution_id}")
            return

        explanation = self.explanations[execution_id]
        tool_explanation = ToolUsageExplanation(
            tool_name=tool_name,
            reason=reason,
            inputs=inputs,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome,
            success=success
        )
        explanation.tool_usage.append(tool_explanation)
        logger.debug(f"Added tool usage explanation for {tool_name} to {execution_id}")

    def add_alternative(
        self,
        execution_id: str,
        description: str,
        pros: List[str],
        cons: List[str],
        confidence: float,
        reason_not_chosen: str
    ) -> None:
        """
        Add an alternative option that was considered.

        Args:
            execution_id: Execution identifier
            description: Description of the alternative
            pros: Advantages of this option
            cons: Disadvantages of this option
            confidence: Confidence score for this option
            reason_not_chosen: Why this option was not chosen
        """
        if execution_id not in self.explanations:
            logger.warning(f"⚠️ No explanation found for execution {execution_id}")
            return

        explanation = self.explanations[execution_id]
        alternative = AlternativeOption(
            description=description,
            pros=pros,
            cons=cons,
            confidence=confidence,
            reason_not_chosen=reason_not_chosen
        )
        explanation.alternatives_considered.append(alternative)
        logger.debug(f"Added alternative option to {execution_id}")

    def add_key_factors(self, execution_id: str, factors: List[str]) -> None:
        """Add key factors that influenced the decision."""
        if execution_id not in self.explanations:
            logger.warning(f"⚠️ No explanation found for execution {execution_id}")
            return
        self.explanations[execution_id].key_factors.extend(factors)

    def add_assumptions(self, execution_id: str, assumptions: List[str]) -> None:
        """Add assumptions made during decision-making."""
        if execution_id not in self.explanations:
            logger.warning(f"⚠️ No explanation found for execution {execution_id}")
            return
        self.explanations[execution_id].assumptions.extend(assumptions)

    def add_limitations(self, execution_id: str, limitations: List[str]) -> None:
        """Add limitations of the decision."""
        if execution_id not in self.explanations:
            logger.warning(f"⚠️ No explanation found for execution {execution_id}")
            return
        self.explanations[execution_id].limitations.extend(limitations)

    def get_explanation(self, execution_id: str) -> Optional[DecisionExplanation]:
        """
        Get explanation for a specific execution.

        Args:
            execution_id: Execution identifier

        Returns:
            DecisionExplanation or None
        """
        return self.explanations.get(execution_id)

    def get_agent_explanations(
        self,
        agent_name: str,
        limit: int = 10
    ) -> List[DecisionExplanation]:
        """
        Get recent explanations for an agent.

        Args:
            agent_name: Name of the agent
            limit: Maximum number of explanations

        Returns:
            List of DecisionExplanation objects
        """
        agent_explanations = [
            exp for exp in self.explanations.values()
            if exp.agent_name == agent_name
        ]
        # Sort by timestamp, most recent first
        agent_explanations.sort(key=lambda x: x.timestamp, reverse=True)
        return agent_explanations[:limit]

    def generate_summary(self, execution_id: str) -> Optional[str]:
        """
        Generate a human-readable summary of the explanation.

        Args:
            execution_id: Execution identifier

        Returns:
            Summary string or None
        """
        explanation = self.get_explanation(execution_id)
        if not explanation:
            return None

        summary_parts = [
            f"# Decision Explanation for {explanation.agent_name}",
            f"",
            f"**Decision:** {explanation.decision}",
            f"**Confidence:** {explanation.confidence.value} ({explanation.confidence_score:.1%})",
            f"",
            f"## Reasoning Process"
        ]

        # Add reasoning steps
        for step in explanation.reasoning_steps:
            summary_parts.append(f"{step.step_number}. [{step.reasoning_type.value}] {step.content}")

        # Add tool usage
        if explanation.tool_usage:
            summary_parts.extend(["", "## Tools Used"])
            for tool in explanation.tool_usage:
                status = "✅" if tool.success else "❌"
                summary_parts.append(f"- {status} **{tool.tool_name}**: {tool.reason}")

        # Add alternatives
        if explanation.alternatives_considered:
            summary_parts.extend(["", "## Alternatives Considered"])
            for alt in explanation.alternatives_considered:
                summary_parts.append(f"- {alt.description} ({alt.confidence:.1%} confidence)")
                summary_parts.append(f"  - Reason not chosen: {alt.reason_not_chosen}")

        # Add key factors
        if explanation.key_factors:
            summary_parts.extend(["", "## Key Factors"])
            for factor in explanation.key_factors:
                summary_parts.append(f"- {factor}")

        # Add assumptions
        if explanation.assumptions:
            summary_parts.extend(["", "## Assumptions"])
            for assumption in explanation.assumptions:
                summary_parts.append(f"- {assumption}")

        # Add limitations
        if explanation.limitations:
            summary_parts.extend(["", "## Limitations"])
            for limitation in explanation.limitations:
                summary_parts.append(f"- {limitation}")

        return "\n".join(summary_parts)

    def export_explanation(self, execution_id: str) -> Optional[str]:
        """
        Export explanation as JSON.

        Args:
            execution_id: Execution identifier

        Returns:
            JSON string or None
        """
        explanation = self.get_explanation(execution_id)
        if not explanation:
            return None
        return json.dumps(explanation.to_dict(), indent=2, default=str)


# Global decision explainer instance
global_decision_explainer = DecisionExplainer()
