"""
Agent Communication Protocol

Defines the communication protocol and message formats for inter-agent communication.
Enables agents to send messages, share context, and coordinate tasks.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages that can be sent between agents"""
    TASK_REQUEST = "task_request"  # Request another agent to perform a task
    TASK_RESPONSE = "task_response"  # Response from an agent after task completion
    CONTEXT_SHARE = "context_share"  # Share context/information with other agents
    STATUS_UPDATE = "status_update"  # Update on task progress
    ERROR = "error"  # Error notification
    COORDINATION = "coordination"  # Coordination message for multi-agent workflows
    QUERY = "query"  # Query for information from another agent
    RESULT = "result"  # Result from a query


class MessagePriority(Enum):
    """Priority levels for messages"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentMessage:
    """
    Message structure for inter-agent communication.

    Attributes:
        message_id: Unique identifier for the message
        sender: Name of the sending agent
        recipient: Name of the receiving agent (or "broadcast" for all)
        message_type: Type of message
        priority: Message priority level
        content: Message content (can be text, dict, or any serializable data)
        context: Additional context data
        correlation_id: ID to correlate related messages (e.g., request-response pairs)
        timestamp: Message creation timestamp
        metadata: Additional metadata
    """
    sender: str
    recipient: str
    message_type: MessageType
    content: Any
    message_id: str = field(default_factory=lambda: str(uuid4()))
    priority: MessagePriority = MessagePriority.MEDIUM
    context: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "context": self.context,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary"""
        return cls(
            message_id=data.get("message_id", str(uuid4())),
            sender=data["sender"],
            recipient=data["recipient"],
            message_type=MessageType(data["message_type"]),
            priority=MessagePriority(data.get("priority", MessagePriority.MEDIUM.value)),
            content=data["content"],
            context=data.get("context"),
            correlation_id=data.get("correlation_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if isinstance(data.get("timestamp"), str) else data.get("timestamp", datetime.now()),
            metadata=data.get("metadata")
        )


class AgentCommunicationProtocol:
    """
    Communication protocol for agent-to-agent messaging.

    Handles message routing, queuing, and delivery between agents.
    Supports both direct messaging and broadcast messaging.
    """

    def __init__(self):
        # Message queues for each agent
        self.message_queues: Dict[str, List[AgentMessage]] = {}

        # Message history for debugging and tracking
        self.message_history: List[AgentMessage] = []

        # Registered agents
        self.registered_agents: Dict[str, Any] = {}

        # Maximum message history size
        self.max_history_size = 1000

        logger.info("✅ Agent Communication Protocol initialized")

    def register_agent(self, agent_name: str, agent_instance: Any = None) -> None:
        """
        Register an agent with the communication protocol.

        Args:
            agent_name: Name of the agent
            agent_instance: Optional agent instance reference
        """
        if agent_name not in self.message_queues:
            self.message_queues[agent_name] = []
            self.registered_agents[agent_name] = agent_instance
            logger.info(f"📝 Agent '{agent_name}' registered with communication protocol")

    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent"""
        if agent_name in self.message_queues:
            del self.message_queues[agent_name]
            del self.registered_agents[agent_name]
            logger.info(f"📝 Agent '{agent_name}' unregistered from communication protocol")

    def send_message(self, message: AgentMessage) -> bool:
        """
        Send a message to an agent.

        Args:
            message: AgentMessage to send

        Returns:
            True if message was delivered, False otherwise
        """
        try:
            # Handle broadcast messages
            if message.recipient == "broadcast":
                for agent_name in self.message_queues.keys():
                    if agent_name != message.sender:
                        self.message_queues[agent_name].append(message)
                logger.info(f"📢 Broadcast message from '{message.sender}' to all agents")
            else:
                # Direct message to specific agent
                if message.recipient not in self.message_queues:
                    logger.warning(f"⚠️ Agent '{message.recipient}' not registered. Message not delivered.")
                    return False

                self.message_queues[message.recipient].append(message)
                logger.info(f"📨 Message sent from '{message.sender}' to '{message.recipient}' (type: {message.message_type.value})")

            # Add to history
            self.message_history.append(message)

            # Limit history size
            if len(self.message_history) > self.max_history_size:
                self.message_history = self.message_history[-self.max_history_size:]

            return True

        except Exception as e:
            logger.error(f"❌ Error sending message: {e}", exc_info=True)
            return False

    def receive_messages(
        self,
        agent_name: str,
        message_type: Optional[MessageType] = None,
        clear_after_read: bool = True
    ) -> List[AgentMessage]:
        """
        Retrieve messages for an agent.

        Args:
            agent_name: Name of the agent
            message_type: Optional filter by message type
            clear_after_read: Whether to clear messages after reading

        Returns:
            List of messages for the agent
        """
        if agent_name not in self.message_queues:
            logger.warning(f"⚠️ Agent '{agent_name}' not registered")
            return []

        messages = self.message_queues[agent_name]

        # Filter by message type if specified
        if message_type:
            messages = [msg for msg in messages if msg.message_type == message_type]

        # Clear queue if requested
        if clear_after_read:
            if message_type:
                # Remove only filtered messages
                self.message_queues[agent_name] = [
                    msg for msg in self.message_queues[agent_name]
                    if msg.message_type != message_type
                ]
            else:
                # Clear all messages
                self.message_queues[agent_name] = []

        logger.debug(f"📬 Agent '{agent_name}' received {len(messages)} messages")
        return messages

    def get_pending_message_count(self, agent_name: str) -> int:
        """Get count of pending messages for an agent"""
        if agent_name not in self.message_queues:
            return 0
        return len(self.message_queues[agent_name])

    def get_message_history(
        self,
        agent_name: Optional[str] = None,
        limit: int = 100
    ) -> List[AgentMessage]:
        """
        Get message history, optionally filtered by agent.

        Args:
            agent_name: Optional agent name to filter by
            limit: Maximum number of messages to return

        Returns:
            List of historical messages
        """
        history = self.message_history

        if agent_name:
            history = [
                msg for msg in history
                if msg.sender == agent_name or msg.recipient == agent_name
            ]

        return history[-limit:]

    def clear_all_queues(self) -> None:
        """Clear all message queues"""
        for queue in self.message_queues.values():
            queue.clear()
        logger.info("🧹 All message queues cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get protocol statistics"""
        return {
            "registered_agents": list(self.registered_agents.keys()),
            "agent_count": len(self.registered_agents),
            "total_messages_sent": len(self.message_history),
            "pending_messages_by_agent": {
                agent: len(queue)
                for agent, queue in self.message_queues.items()
            },
            "total_pending_messages": sum(len(queue) for queue in self.message_queues.values())
        }


# Global protocol instance (singleton)
_global_protocol = None

def get_global_protocol() -> AgentCommunicationProtocol:
    """Get or create the global communication protocol instance"""
    global _global_protocol
    if _global_protocol is None:
        _global_protocol = AgentCommunicationProtocol()
    return _global_protocol
