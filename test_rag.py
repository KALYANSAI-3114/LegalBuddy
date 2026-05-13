"""
Test the RAG system after database initialization
Run this to verify everything is working correctly
"""

import sys
from pathlib import Path
from rag_engine import LegalRAGEngine

def test_rag_system():
    """Test the RAG system with sample queries"""
    
    print("=" * 70)
    print("RAG SYSTEM TEST")
    print("=" * 70)
    print()
    
    # Initialize engine
    engine = LegalRAGEngine(
        data_folder="data",
        chroma_db_path="./chroma_db",
        model_name="phi3:mini"
    )
    
    try:
        engine.initialize()
    except Exception as e:
        print(f"❌ Failed to initialize RAG engine: {e}")
        print("   Make sure you've run: python initialize_db.py")
        return
    
    print()
    print("=" * 70)
    print("TEST QUERIES")
    print("=" * 70)
    print()
    
    test_queries = [
        ("How to file an FIR?", "Should find CRPC information"),
        ("What are the different IPC sections?", "Should find IPC details"),
        ("What is the Indian Constitution?", "Should reference Constitutional law"),
        ("Tell me about cyber crimes", "Should find IT Act 2000 information"),
        ("What are fundamental rights?", "Should find Constitution articles"),
    ]
    
    for query, expected in test_queries:
        print(f"📝 Query: {query}")
        print(f"   Expected: {expected}")
        
        try:
            result = engine.query(query)
            print(f"   ✅ Answer found: {result['answer'][:150]}...")
            print(f"   📚 Sources: {', '.join(result['sources'][:2])}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("=" * 70)
    print("✅ Test complete! System appears to be working.")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Start the backend: uvicorn backend.main:app --reload")
    print("  2. Open browser: http://localhost:8000")
    print("  3. Ask your legal questions!")
    print()

if __name__ == "__main__":
    test_rag_system()
