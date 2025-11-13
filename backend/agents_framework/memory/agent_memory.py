"""
Agent Memory System

Provides conversation history and semantic memory for agents.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """A single memory entry"""
    role: str  # 'human', 'ai', 'system'
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }


class ConversationMemory:
    """
    Manages conversation history for an agent.

    Features:
    - Stores conversation history with timestamps
    - Limits memory size to prevent context overflow
    - Provides formatted context for prompts
    - Supports clearing and filtering
    """

    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: List[MemoryEntry] = []
        self.created_at = datetime.now()

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to memory"""
        entry = MemoryEntry(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )

        self.messages.append(entry)

        # Trim to max size
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

        logger.debug(f"Added {role} message to memory. Total: {len(self.messages)}")

    def add_human_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a human message"""
        self.add_message("human", content, metadata)

    def add_ai_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add an AI message"""
        self.add_message("ai", content, metadata)

    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a system message"""
        self.add_message("system", content, metadata)

    def get_messages(self, last_n: Optional[int] = None) -> List[MemoryEntry]:
        """Get messages (optionally last N)"""
        if last_n:
            return self.messages[-last_n:]
        return self.messages

    def get_langchain_messages(self, last_n: Optional[int] = None) -> List[BaseMessage]:
        """Get messages in LangChain format"""
        messages = self.get_messages(last_n)
        lc_messages = []

        for msg in messages:
            if msg.role == "human":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "ai":
                lc_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                lc_messages.append(SystemMessage(content=msg.content))

        return lc_messages

    def get_context_string(self, last_n: int = 6) -> str:
        """Get conversation history as formatted string"""
        messages = self.get_messages(last_n)

        if not messages:
            return ""

        context_parts = ["Previous conversation:"]
        for msg in messages:
            role_label = msg.role.capitalize()
            context_parts.append(f"{role_label}: {msg.content}")

        return "\n".join(context_parts)

    def clear(self) -> None:
        """Clear all messages"""
        self.messages.clear()
        logger.info("Conversation memory cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_messages": len(self.messages),
            "human_messages": sum(1 for m in self.messages if m.role == "human"),
            "ai_messages": sum(1 for m in self.messages if m.role == "ai"),
            "system_messages": sum(1 for m in self.messages if m.role == "system"),
            "max_messages": self.max_messages,
            "created_at": self.created_at.isoformat(),
        }

    def export_history(self) -> List[Dict[str, Any]]:
        """Export conversation history as list of dicts"""
        return [msg.to_dict() for msg in self.messages]

    def __len__(self) -> int:
        return len(self.messages)

    def __repr__(self) -> str:
        return f"<ConversationMemory: {len(self.messages)} messages>"


class SemanticMemory:
    """
    Semantic memory using vector embeddings for long-term memory.

    This will be used for storing and retrieving relevant past experiences,
    decisions, and learned patterns.
    """

    def __init__(self, collection_name: str = "agent_memory"):
        self.collection_name = collection_name
        self.memory_store: List[Dict[str, Any]] = []  # Simplified for now

        # TODO: Integrate with ChromaDB for actual vector storage
        logger.info(f"Semantic memory '{collection_name}' initialized (simplified mode)")

    def store(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        category: str = "general"
    ) -> str:
        """Store a memory with semantic embeddings"""
        memory_id = f"mem_{len(self.memory_store)}_{datetime.now().timestamp()}"

        memory = {
            "id": memory_id,
            "content": content,
            "category": category,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }

        self.memory_store.append(memory)
        logger.debug(f"Stored semantic memory: {memory_id}")

        return memory_id

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on query"""
        # Simplified retrieval - just return recent memories
        # TODO: Implement actual semantic search with embeddings

        results = self.memory_store

        # Filter by category if provided
        if category:
            results = [m for m in results if m["category"] == category]

        # Return most recent
        results = sorted(results, key=lambda x: x["timestamp"], reverse=True)
        return results[:limit]

    def clear_category(self, category: str) -> int:
        """Clear all memories in a category"""
        original_count = len(self.memory_store)
        self.memory_store = [m for m in self.memory_store if m["category"] != category]
        removed = original_count - len(self.memory_store)

        logger.info(f"Cleared {removed} memories from category '{category}'")
        return removed

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        categories = {}
        for mem in self.memory_store:
            cat = mem["category"]
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_memories": len(self.memory_store),
            "categories": categories,
            "collection_name": self.collection_name,
        }

    def __len__(self) -> int:
        return len(self.memory_store)


class AgentMemoryManager:
    """
    Manages both conversation and semantic memory for an agent.
    """

    def __init__(
        self,
        agent_name: str,
        max_conversation_messages: int = 20,
        enable_semantic: bool = True
    ):
        self.agent_name = agent_name

        # Initialize conversation memory
        self.conversation = ConversationMemory(max_messages=max_conversation_messages)

        # Initialize semantic memory
        self.semantic = None
        if enable_semantic:
            self.semantic = SemanticMemory(collection_name=f"{agent_name}_memory")

        logger.info(f"Memory manager initialized for agent '{agent_name}'")

    def add_interaction(
        self,
        human_message: str,
        ai_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a complete interaction (human + AI) to memory"""
        self.conversation.add_human_message(human_message, metadata)
        self.conversation.add_ai_message(ai_response, metadata)

    def store_learning(
        self,
        content: str,
        category: str = "learning",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Store a learning or insight in semantic memory"""
        if self.semantic:
            return self.semantic.store(content, metadata, category)
        return None

    def retrieve_relevant_memories(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories from semantic memory"""
        if self.semantic:
            return self.semantic.retrieve(query, category, limit)
        return []

    def clear_all(self) -> None:
        """Clear all memories"""
        self.conversation.clear()
        if self.semantic:
            self.semantic.memory_store.clear()
        logger.info(f"All memories cleared for agent '{self.agent_name}'")

    def get_full_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        stats = {
            "agent_name": self.agent_name,
            "conversation": self.conversation.get_stats(),
        }

        if self.semantic:
            stats["semantic"] = self.semantic.get_stats()

        return stats

    def __repr__(self) -> str:
        semantic_status = "enabled" if self.semantic else "disabled"
        return f"<AgentMemoryManager for '{self.agent_name}' - Semantic: {semantic_status}>"
