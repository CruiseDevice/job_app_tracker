"""
Utility functions for the agent framework
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


def format_agent_response(response, include_metadata: bool = False) -> Dict[str, Any]:
    """Format agent response for API output"""
    formatted = {
        "output": response.output,
        "agent_name": response.agent_name,
        "success": response.success,
        "timestamp": response.timestamp.isoformat(),
    }

    if response.error:
        formatted["error"] = response.error

    if include_metadata:
        formatted["metadata"] = response.metadata
        formatted["intermediate_steps"] = [
            {
                "action": step[0].tool if hasattr(step[0], 'tool') else str(step[0]),
                "result": str(step[1])
            }
            for step in response.intermediate_steps
        ]

    return formatted


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate API cost based on model and token usage.

    Pricing as of 2024 (per 1M tokens):
    - GPT-4o: $2.50 input / $10.00 output
    - GPT-4o-mini: $0.150 input / $0.600 output
    """
    pricing = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.150, "output": 0.600},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }

    if model not in pricing:
        logger.warning(f"Unknown model '{model}' for cost calculation")
        return 0.0

    prices = pricing[model]
    input_cost = (input_tokens / 1_000_000) * prices["input"]
    output_cost = (output_tokens / 1_000_000) * prices["output"]

    return input_cost + output_cost


def log_agent_execution(
    agent_name: str,
    input_text: str,
    output: str,
    success: bool,
    execution_time: float,
    error: Optional[str] = None
) -> None:
    """Log agent execution for monitoring"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent_name": agent_name,
        "input_length": len(input_text),
        "output_length": len(output) if output else 0,
        "success": success,
        "execution_time": execution_time,
        "error": error,
    }

    if success:
        logger.info(f"✅ Agent '{agent_name}' completed in {execution_time:.2f}s")
    else:
        logger.error(f"❌ Agent '{agent_name}' failed after {execution_time:.2f}s: {error}")

    logger.debug(f"Agent execution details: {json.dumps(log_entry)}")


def validate_agent_config(config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate agent configuration.

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["name", "description"]

    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"

    if not isinstance(config.get("name"), str) or not config["name"].strip():
        return False, "Agent name must be a non-empty string"

    if not isinstance(config.get("description"), str) or not config["description"].strip():
        return False, "Agent description must be a non-empty string"

    # Validate optional fields
    if "temperature" in config:
        temp = config["temperature"]
        if not isinstance(temp, (int, float)) or not (0 <= temp <= 2):
            return False, "Temperature must be a number between 0 and 2"

    if "max_iterations" in config:
        max_iter = config["max_iterations"]
        if not isinstance(max_iter, int) or max_iter < 1:
            return False, "max_iterations must be a positive integer"

    return True, None


def sanitize_tool_input(input_str: str, max_length: int = 10000) -> str:
    """Sanitize and limit tool input"""
    if not input_str:
        return ""

    # Remove any potentially harmful characters
    sanitized = input_str.strip()

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "... (truncated)"
        logger.warning(f"Tool input truncated from {len(input_str)} to {max_length} characters")

    return sanitized


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from text that might contain markdown code blocks or extra text.

    Handles:
    - ```json ... ```
    - Plain JSON objects
    - JSON arrays
    """
    try:
        # Try direct JSON parse first
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract from markdown code blocks
    import re

    # Look for ```json ... ``` blocks
    json_block_pattern = r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```'
    matches = re.findall(json_block_pattern, text, re.DOTALL)

    if matches:
        try:
            return json.loads(matches[0])
        except json.JSONDecodeError:
            pass

    # Look for JSON objects without code blocks
    json_pattern = r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
    matches = re.findall(json_pattern, text, re.DOTALL)

    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    logger.warning("Could not extract valid JSON from text")
    return None


def format_tool_error(tool_name: str, error: Exception) -> str:
    """Format a tool execution error for agent consumption"""
    return f"Error executing tool '{tool_name}': {str(error)}. Please try a different approach or tool."


class TokenCounter:
    """Simple token counter for cost estimation"""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count (rough approximation).

        Real implementation should use tiktoken, but this is a simple fallback.
        Rule of thumb: ~1 token per 4 characters for English text
        """
        return len(text) // 4

    @staticmethod
    def count_messages_tokens(messages: list) -> int:
        """Estimate tokens in a list of messages"""
        total = 0
        for msg in messages:
            if hasattr(msg, 'content'):
                total += TokenCounter.estimate_tokens(msg.content)
            elif isinstance(msg, dict) and 'content' in msg:
                total += TokenCounter.estimate_tokens(msg['content'])
        return total
