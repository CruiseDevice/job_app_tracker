"""
Explanation formatting utilities.

Provides different formats for presenting decision explanations:
- Markdown
- HTML
- Plain text
- JSON
"""

from typing import Optional
from enum import Enum
from .decision_explainer import DecisionExplanation, ReasoningType


class ExplanationFormat(str, Enum):
    """Output formats for explanations."""
    MARKDOWN = "markdown"
    HTML = "html"
    PLAIN_TEXT = "plain_text"
    JSON = "json"


class ExplanationFormatter:
    """Formatter for decision explanations."""

    @staticmethod
    def format(
        explanation: DecisionExplanation,
        format_type: ExplanationFormat = ExplanationFormat.MARKDOWN
    ) -> str:
        """
        Format explanation in specified format.

        Args:
            explanation: DecisionExplanation to format
            format_type: Output format

        Returns:
            Formatted explanation string
        """
        if format_type == ExplanationFormat.MARKDOWN:
            return ExplanationFormatter._format_markdown(explanation)
        elif format_type == ExplanationFormat.HTML:
            return ExplanationFormatter._format_html(explanation)
        elif format_type == ExplanationFormat.PLAIN_TEXT:
            return ExplanationFormatter._format_plain_text(explanation)
        elif format_type == ExplanationFormat.JSON:
            import json
            return json.dumps(explanation.to_dict(), indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    @staticmethod
    def _format_markdown(explanation: DecisionExplanation) -> str:
        """Format as Markdown."""
        lines = [
            f"# Decision Explanation: {explanation.agent_name}",
            "",
            f"**Execution ID:** `{explanation.execution_id}`",
            f"**Timestamp:** {explanation.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## Decision",
            "",
            f"**{explanation.decision}**",
            "",
            f"- **Confidence:** {explanation.confidence.value.replace('_', ' ').title()}",
            f"- **Score:** {explanation.confidence_score:.1%}",
            ""
        ]

        # Reasoning steps
        if explanation.reasoning_steps:
            lines.extend(["## Reasoning Process", ""])
            for step in explanation.reasoning_steps:
                emoji = ExplanationFormatter._get_reasoning_emoji(step.reasoning_type)
                lines.append(f"{step.step_number}. {emoji} **{step.reasoning_type.value.title()}:** {step.content}")
            lines.append("")

        # Tool usage
        if explanation.tool_usage:
            lines.extend(["## Tools Used", ""])
            for tool in explanation.tool_usage:
                status = "✅ Success" if tool.success else "❌ Failed"
                lines.extend([
                    f"### {tool.tool_name} ({status})",
                    "",
                    f"**Reason:** {tool.reason}",
                    "",
                    f"**Expected Outcome:** {tool.expected_outcome}",
                ])
                if tool.actual_outcome:
                    lines.append(f"**Actual Outcome:** {tool.actual_outcome}")
                lines.append("")

        # Alternatives considered
        if explanation.alternatives_considered:
            lines.extend(["## Alternatives Considered", ""])
            for i, alt in enumerate(explanation.alternatives_considered, 1):
                lines.extend([
                    f"### Alternative {i}: {alt.description}",
                    "",
                    f"**Confidence:** {alt.confidence:.1%}",
                    "",
                    "**Pros:**",
                ])
                for pro in alt.pros:
                    lines.append(f"- ✅ {pro}")
                lines.append("")
                lines.append("**Cons:**")
                for con in alt.cons:
                    lines.append(f"- ❌ {con}")
                lines.extend([
                    "",
                    f"**Why not chosen:** {alt.reason_not_chosen}",
                    ""
                ])

        # Key factors
        if explanation.key_factors:
            lines.extend(["## Key Factors", ""])
            for factor in explanation.key_factors:
                lines.append(f"- 🔑 {factor}")
            lines.append("")

        # Assumptions
        if explanation.assumptions:
            lines.extend(["## Assumptions", ""])
            for assumption in explanation.assumptions:
                lines.append(f"- 💭 {assumption}")
            lines.append("")

        # Limitations
        if explanation.limitations:
            lines.extend(["## Limitations", ""])
            for limitation in explanation.limitations:
                lines.append(f"- ⚠️ {limitation}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _format_html(explanation: DecisionExplanation) -> str:
        """Format as HTML."""
        html_parts = [
            "<div class='decision-explanation'>",
            f"<h1>Decision Explanation: {explanation.agent_name}</h1>",
            f"<p><strong>Execution ID:</strong> <code>{explanation.execution_id}</code></p>",
            f"<p><strong>Timestamp:</strong> {explanation.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>",
            "<hr>",
            "<h2>Decision</h2>",
            f"<p class='decision'><strong>{explanation.decision}</strong></p>",
            f"<p><strong>Confidence:</strong> {explanation.confidence.value.replace('_', ' ').title()} ({explanation.confidence_score:.1%})</p>",
        ]

        # Reasoning steps
        if explanation.reasoning_steps:
            html_parts.append("<h2>Reasoning Process</h2>")
            html_parts.append("<ol>")
            for step in explanation.reasoning_steps:
                emoji = ExplanationFormatter._get_reasoning_emoji(step.reasoning_type)
                html_parts.append(
                    f"<li>{emoji} <strong>{step.reasoning_type.value.title()}:</strong> {step.content}</li>"
                )
            html_parts.append("</ol>")

        # Tool usage
        if explanation.tool_usage:
            html_parts.append("<h2>Tools Used</h2>")
            for tool in explanation.tool_usage:
                status = "✅ Success" if tool.success else "❌ Failed"
                html_parts.extend([
                    f"<h3>{tool.tool_name} ({status})</h3>",
                    f"<p><strong>Reason:</strong> {tool.reason}</p>",
                    f"<p><strong>Expected Outcome:</strong> {tool.expected_outcome}</p>",
                ])
                if tool.actual_outcome:
                    html_parts.append(f"<p><strong>Actual Outcome:</strong> {tool.actual_outcome}</p>")

        # Alternatives
        if explanation.alternatives_considered:
            html_parts.append("<h2>Alternatives Considered</h2>")
            for i, alt in enumerate(explanation.alternatives_considered, 1):
                html_parts.extend([
                    f"<h3>Alternative {i}: {alt.description}</h3>",
                    f"<p><strong>Confidence:</strong> {alt.confidence:.1%}</p>",
                    "<p><strong>Pros:</strong></p>",
                    "<ul>",
                ])
                for pro in alt.pros:
                    html_parts.append(f"<li>✅ {pro}</li>")
                html_parts.extend([
                    "</ul>",
                    "<p><strong>Cons:</strong></p>",
                    "<ul>",
                ])
                for con in alt.cons:
                    html_parts.append(f"<li>❌ {con}</li>")
                html_parts.extend([
                    "</ul>",
                    f"<p><strong>Why not chosen:</strong> {alt.reason_not_chosen}</p>",
                ])

        # Key factors
        if explanation.key_factors:
            html_parts.append("<h2>Key Factors</h2>")
            html_parts.append("<ul>")
            for factor in explanation.key_factors:
                html_parts.append(f"<li>🔑 {factor}</li>")
            html_parts.append("</ul>")

        # Assumptions
        if explanation.assumptions:
            html_parts.append("<h2>Assumptions</h2>")
            html_parts.append("<ul>")
            for assumption in explanation.assumptions:
                html_parts.append(f"<li>💭 {assumption}</li>")
            html_parts.append("</ul>")

        # Limitations
        if explanation.limitations:
            html_parts.append("<h2>Limitations</h2>")
            html_parts.append("<ul>")
            for limitation in explanation.limitations:
                html_parts.append(f"<li>⚠️ {limitation}</li>")
            html_parts.append("</ul>")

        html_parts.append("</div>")
        return "\n".join(html_parts)

    @staticmethod
    def _format_plain_text(explanation: DecisionExplanation) -> str:
        """Format as plain text."""
        lines = [
            f"Decision Explanation: {explanation.agent_name}",
            "=" * 60,
            "",
            f"Execution ID: {explanation.execution_id}",
            f"Timestamp: {explanation.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "DECISION",
            "-" * 60,
            explanation.decision,
            "",
            f"Confidence: {explanation.confidence.value.replace('_', ' ').title()} ({explanation.confidence_score:.1%})",
            ""
        ]

        # Reasoning steps
        if explanation.reasoning_steps:
            lines.extend(["REASONING PROCESS", "-" * 60])
            for step in explanation.reasoning_steps:
                lines.append(f"{step.step_number}. [{step.reasoning_type.value}] {step.content}")
            lines.append("")

        # Tool usage
        if explanation.tool_usage:
            lines.extend(["TOOLS USED", "-" * 60])
            for tool in explanation.tool_usage:
                status = "SUCCESS" if tool.success else "FAILED"
                lines.extend([
                    f"{tool.tool_name} ({status})",
                    f"  Reason: {tool.reason}",
                    f"  Expected: {tool.expected_outcome}",
                ])
                if tool.actual_outcome:
                    lines.append(f"  Actual: {tool.actual_outcome}")
                lines.append("")

        # Alternatives
        if explanation.alternatives_considered:
            lines.extend(["ALTERNATIVES CONSIDERED", "-" * 60])
            for i, alt in enumerate(explanation.alternatives_considered, 1):
                lines.extend([
                    f"{i}. {alt.description} ({alt.confidence:.1%} confidence)",
                    f"   Why not chosen: {alt.reason_not_chosen}",
                    ""
                ])

        # Key factors
        if explanation.key_factors:
            lines.extend(["KEY FACTORS", "-" * 60])
            for factor in explanation.key_factors:
                lines.append(f"* {factor}")
            lines.append("")

        # Assumptions
        if explanation.assumptions:
            lines.extend(["ASSUMPTIONS", "-" * 60])
            for assumption in explanation.assumptions:
                lines.append(f"* {assumption}")
            lines.append("")

        # Limitations
        if explanation.limitations:
            lines.extend(["LIMITATIONS", "-" * 60])
            for limitation in explanation.limitations:
                lines.append(f"* {limitation}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _get_reasoning_emoji(reasoning_type: ReasoningType) -> str:
        """Get emoji for reasoning type."""
        emoji_map = {
            ReasoningType.OBSERVATION: "👁️",
            ReasoningType.THOUGHT: "💭",
            ReasoningType.ACTION: "⚡",
            ReasoningType.TOOL_CALL: "🔧",
            ReasoningType.EVALUATION: "📊",
            ReasoningType.DECISION: "✅"
        }
        return emoji_map.get(reasoning_type, "•")
