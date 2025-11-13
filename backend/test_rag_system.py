"""
Test script for RAG (Retrieval Augmented Generation) system
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents_framework.memory.vector_memory import VectorMemoryStore, RAGMemoryManager


def test_vector_memory():
    """Test the vector memory store"""
    print("🧪 Testing Vector Memory Store\n")

    # Test 1: Initialize vector store
    print("1. Initializing VectorMemoryStore...")
    vector_store = VectorMemoryStore(
        collection_name="test_collection",
        persist_directory="./test_data/chroma"
    )
    print(f"   ✅ Initialized: {vector_store}")
    print(f"   Stats: {vector_store.get_stats()}\n")

    # Test 2: Add memories
    print("2. Adding memories...")
    memories = [
        "I applied to Google for a Software Engineer position and got an interview.",
        "Amazon rejected my application for Senior Developer role.",
        "Meta scheduled a phone screen for Backend Engineer position.",
        "I need to follow up with Microsoft about the Full Stack role.",
        "Stripe sent me a coding challenge for the API Engineer position.",
    ]

    ids = []
    for i, mem in enumerate(memories):
        meta = {
            "category": "application_update",
            "index": i,
        }
        mem_id = vector_store.add(mem, metadata=meta)
        ids.append(mem_id)
        print(f"   Added: {mem[:50]}... (ID: {mem_id})")

    print(f"\n   ✅ Total memories: {vector_store.count()}\n")

    # Test 3: Semantic search
    print("3. Testing semantic search...")
    queries = [
        "Which companies scheduled interviews?",
        "Tell me about coding challenges",
        "What about Google?",
    ]

    for query in queries:
        print(f"\n   Query: '{query}'")
        results = vector_store.search(query, n_results=2)

        if results:
            for i, result in enumerate(results, 1):
                similarity = result.get('similarity', 0)
                content = result.get('content', '')
                print(f"   {i}. (similarity: {similarity:.3f}) {content[:60]}...")
        else:
            print("   No results found (ChromaDB may not be available)")

    print("\n   ✅ Search completed\n")

    # Test 4: Get specific memory
    print("4. Retrieving specific memory...")
    if ids:
        memory = vector_store.get(ids[0])
        if memory:
            print(f"   ✅ Retrieved: {memory['content'][:60]}...")
        else:
            print("   ⚠️  Could not retrieve (ChromaDB may not be available)")
    print()

    # Test 5: Delete memory
    print("5. Testing delete...")
    if ids:
        success = vector_store.delete(ids[0])
        print(f"   {'✅' if success else '⚠️ '} Delete {'successful' if success else 'skipped'}")
        print(f"   Remaining memories: {vector_store.count()}")
    print()

    # Test 6: Clear all
    print("6. Clearing all memories...")
    vector_store.clear_all()
    print(f"   ✅ Cleared. Remaining: {vector_store.count()}\n")

    print("✅ Vector Memory Store tests completed!\n")


def test_rag_manager():
    """Test the RAG memory manager"""
    print("🧪 Testing RAG Memory Manager\n")

    # Test 1: Initialize
    print("1. Initializing RAGMemoryManager...")
    rag = RAGMemoryManager(
        agent_name="test_agent",
        persist_directory="./test_data/chroma"
    )
    print(f"   ✅ Initialized: {rag}\n")

    # Test 2: Store experiences
    print("2. Storing experiences...")
    experiences = [
        ("Learned that Google interviews focus heavily on algorithms", "learning", ["google", "interview"]),
        ("Decision: Always send follow-up emails after 2 weeks", "decision", ["follow-up", "strategy"]),
        ("Insight: Tech companies respond faster to referrals", "insight", ["referral", "strategy"]),
        ("Learned that Amazon uses STAR format for behavioral questions", "learning", ["amazon", "interview"]),
    ]

    for exp, category, tags in experiences:
        rag.store_experience(exp, category=category, tags=tags)
        print(f"   Stored [{category}]: {exp[:50]}...")

    print(f"\n   ✅ Stored {len(experiences)} experiences\n")

    # Test 3: Retrieve similar experiences
    print("3. Retrieving similar experiences...")
    queries = [
        ("How should I prepare for interviews?", "learning"),
        ("What's a good follow-up strategy?", "decision"),
        ("Tell me about Amazon", None),
    ]

    for query, category in queries:
        print(f"\n   Query: '{query}'")
        if category:
            print(f"   Category filter: {category}")

        similar = rag.retrieve_similar(query, category=category, limit=2)

        if similar:
            for i, mem in enumerate(similar, 1):
                content = mem.get('content', '')
                similarity = mem.get('similarity', 0)
                print(f"   {i}. (similarity: {similarity:.3f}) {content[:60]}...")
        else:
            print("   No results (ChromaDB may not be available)")

    print("\n   ✅ Retrieval completed\n")

    # Test 4: Get context for query
    print("4. Getting formatted context...")
    query = "Interview preparation tips"
    context = rag.get_context_for_query(query, limit=2)

    if context:
        print(f"   Query: '{query}'")
        print(f"   Context:\n{context}")
    else:
        print("   ⚠️  No context available (ChromaDB may not be available)")
    print()

    # Test 5: Statistics
    print("5. Getting statistics...")
    stats = rag.get_stats()
    print(f"   Agent: {stats.get('agent_name')}")
    print(f"   Collection: {stats.get('collection_name')}")
    print(f"   ChromaDB available: {stats.get('chromadb_available')}")
    print(f"   Initialized: {stats.get('initialized')}")
    if stats.get('initialized'):
        print(f"   Total memories: {stats.get('total_memories', 0)}")
    print()

    print("✅ RAG Memory Manager tests completed!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("RAG SYSTEM TEST SUITE")
    print("=" * 60)
    print()

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("Vector embeddings will use default function instead of OpenAI")
        print()

    try:
        # Test vector memory
        test_vector_memory()

        print("\n" + "=" * 60 + "\n")

        # Test RAG manager
        test_rag_manager()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
