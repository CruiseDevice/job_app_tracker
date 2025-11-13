"""
Vector Memory System using ChromaDB for RAG (Retrieval Augmented Generation)

Provides semantic search and long-term memory storage using embeddings.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Install with: pip install chromadb")

logger = logging.getLogger(__name__)


class VectorMemoryStore:
    """
    Vector-based memory storage using ChromaDB for semantic search.

    Features:
    - Automatic embeddings using OpenAI
    - Semantic similarity search
    - Persistent storage
    - Metadata filtering
    - Multiple collections
    """

    def __init__(
        self,
        collection_name: str = "agent_memory",
        persist_directory: str = "./data/chroma",
        embedding_model: str = "text-embedding-3-small",
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model

        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available. Using fallback mode.")
            self.client = None
            self.collection = None
            self.embedding_function = None
            return

        # Initialize ChromaDB client
        try:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )

            # Initialize embedding function (OpenAI)
            import os
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=openai_api_key,
                    model_name=embedding_model
                )
            else:
                # Fallback to default embedding function
                logger.warning("OPENAI_API_KEY not found. Using default embeddings.")
                self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Agent long-term memory storage"}
            )

            logger.info(f"✅ Vector memory initialized: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
            self.collection = None
            self.embedding_function = None

    def add(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> str:
        """
        Add a memory to the vector store.

        Args:
            content: Text content to store
            metadata: Optional metadata (must be JSON serializable)
            doc_id: Optional custom document ID

        Returns:
            Document ID
        """
        if not self.collection:
            logger.warning("ChromaDB not available. Memory not stored.")
            return "unavailable"

        try:
            # Generate ID if not provided
            if not doc_id:
                doc_id = f"mem_{uuid.uuid4().hex[:16]}"

            # Prepare metadata
            meta = metadata or {}
            meta["timestamp"] = datetime.now().isoformat()
            meta["content_length"] = len(content)

            # Add to collection
            self.collection.add(
                documents=[content],
                metadatas=[meta],
                ids=[doc_id]
            )

            logger.debug(f"Added memory: {doc_id}")
            return doc_id

        except Exception as e:
            logger.error(f"Error adding to vector memory: {e}")
            raise

    def add_batch(
        self,
        contents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        doc_ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add multiple memories in batch.

        Args:
            contents: List of text contents
            metadatas: Optional list of metadata dicts
            doc_ids: Optional list of custom document IDs

        Returns:
            List of document IDs
        """
        if not self.collection:
            logger.warning("ChromaDB not available. Memories not stored.")
            return ["unavailable"] * len(contents)

        try:
            # Generate IDs if not provided
            if not doc_ids:
                doc_ids = [f"mem_{uuid.uuid4().hex[:16]}" for _ in contents]

            # Prepare metadata
            if not metadatas:
                metadatas = [{}] * len(contents)

            for meta, content in zip(metadatas, contents):
                meta["timestamp"] = datetime.now().isoformat()
                meta["content_length"] = len(content)

            # Add batch to collection
            self.collection.add(
                documents=contents,
                metadatas=metadatas,
                ids=doc_ids
            )

            logger.info(f"Added {len(contents)} memories in batch")
            return doc_ids

        except Exception as e:
            logger.error(f"Error adding batch to vector memory: {e}")
            raise

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar memories using semantic search.

        Args:
            query: Search query text
            n_results: Number of results to return
            where: Metadata filter (e.g., {"category": "learning"})
            where_document: Document content filter

        Returns:
            List of matching memories with scores
        """
        if not self.collection:
            logger.warning("ChromaDB not available. Returning empty results.")
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=["documents", "metadatas", "distances"]
            )

            # Format results
            memories = []
            if results and results['ids']:
                for i in range(len(results['ids'][0])):
                    memory = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i],
                        'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                    }
                    memories.append(memory)

            logger.debug(f"Found {len(memories)} similar memories for query: {query[:50]}...")
            return memories

        except Exception as e:
            logger.error(f"Error searching vector memory: {e}")
            return []

    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID.

        Args:
            doc_id: Document ID

        Returns:
            Memory dict or None
        """
        if not self.collection:
            return None

        try:
            result = self.collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )

            if result and result['ids']:
                return {
                    'id': result['ids'][0],
                    'content': result['documents'][0],
                    'metadata': result['metadatas'][0],
                }

            return None

        except Exception as e:
            logger.error(f"Error getting memory: {e}")
            return None

    def delete(self, doc_id: str) -> bool:
        """
        Delete a memory by ID.

        Args:
            doc_id: Document ID

        Returns:
            True if successful
        """
        if not self.collection:
            return False

        try:
            self.collection.delete(ids=[doc_id])
            logger.debug(f"Deleted memory: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return False

    def delete_by_metadata(self, where: Dict[str, Any]) -> int:
        """
        Delete memories matching metadata filter.

        Args:
            where: Metadata filter (e.g., {"category": "temp"})

        Returns:
            Number of memories deleted
        """
        if not self.collection:
            return 0

        try:
            # Get IDs matching filter
            results = self.collection.get(where=where, include=[])

            if results and results['ids']:
                count = len(results['ids'])
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {count} memories matching filter")
                return count

            return 0

        except Exception as e:
            logger.error(f"Error deleting by metadata: {e}")
            return 0

    def clear_all(self) -> bool:
        """
        Clear all memories from collection.

        Returns:
            True if successful
        """
        if not self.collection:
            return False

        try:
            # Get all IDs
            results = self.collection.get(include=[])

            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Cleared all memories from collection")

            return True

        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False

    def count(self) -> int:
        """
        Get total number of memories.

        Returns:
            Count of memories
        """
        if not self.collection:
            return 0

        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting memories: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector memory.

        Returns:
            Statistics dict
        """
        stats = {
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory,
            "embedding_model": self.embedding_model,
            "chromadb_available": CHROMADB_AVAILABLE,
            "initialized": self.collection is not None,
        }

        if self.collection:
            stats["total_memories"] = self.count()

        return stats

    def __repr__(self) -> str:
        count = self.count() if self.collection else 0
        return f"<VectorMemoryStore '{self.collection_name}': {count} memories>"


class RAGMemoryManager:
    """
    High-level RAG (Retrieval Augmented Generation) memory manager.

    Combines vector search with metadata filtering for intelligent memory retrieval.
    """

    def __init__(
        self,
        agent_name: str,
        persist_directory: str = "./data/chroma",
    ):
        self.agent_name = agent_name
        self.vector_store = VectorMemoryStore(
            collection_name=f"{agent_name}_memory",
            persist_directory=persist_directory,
        )

        logger.info(f"RAG memory manager initialized for '{agent_name}'")

    def store_experience(
        self,
        experience: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store an experience or learning in memory.

        Args:
            experience: Text description of the experience
            category: Category (e.g., "learning", "decision", "insight")
            tags: Optional list of tags
            metadata: Optional additional metadata

        Returns:
            Memory ID
        """
        meta = metadata or {}
        meta["category"] = category
        meta["tags"] = tags or []
        meta["agent"] = self.agent_name

        return self.vector_store.add(experience, metadata=meta)

    def retrieve_similar(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar experiences using semantic search.

        Args:
            query: Search query
            category: Optional category filter
            limit: Number of results

        Returns:
            List of similar memories
        """
        where = None
        if category:
            where = {"category": category}

        return self.vector_store.search(query, n_results=limit, where=where)

    def get_context_for_query(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 3,
    ) -> str:
        """
        Get formatted context from memory for a query.

        Args:
            query: Search query
            category: Optional category filter
            limit: Number of memories to retrieve

        Returns:
            Formatted context string
        """
        memories = self.retrieve_similar(query, category, limit)

        if not memories:
            return ""

        context_parts = ["Relevant past experiences:"]

        for i, mem in enumerate(memories, 1):
            similarity = mem.get('similarity', 0)
            content = mem.get('content', '')
            cat = mem.get('metadata', {}).get('category', 'unknown')

            context_parts.append(f"\n{i}. [{cat}] (similarity: {similarity:.2f})")
            context_parts.append(f"   {content[:200]}...")

        return "\n".join(context_parts)

    def clear_category(self, category: str) -> int:
        """Clear all memories in a category"""
        return self.vector_store.delete_by_metadata({"category": category})

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "agent_name": self.agent_name,
            **self.vector_store.get_stats()
        }

    def __repr__(self) -> str:
        return f"<RAGMemoryManager for '{self.agent_name}'>"
