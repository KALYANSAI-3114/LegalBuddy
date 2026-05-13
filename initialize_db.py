"""
Initialize and index the legal database from PDFs
Run this script once to populate Chroma DB with legal documents
"""

import sys
from pathlib import Path
from rag_engine import LegalRAGEngine

def main():
    # Initialize the RAG engine with data folder
    engine = LegalRAGEngine(
        data_folder="data",
        chroma_db_path="./chroma_db",
        model_name="phi3:mini"
    )
    
    print("=" * 70)
    print("LEGAL RAG APPLICATION — DATABASE INITIALIZATION")
    print("=" * 70)
    print()
    
    # Train from PDFs
    engine.train_from_pdfs()
    
    print()
    print("=" * 70)
    print("DATABASE INITIALIZATION COMPLETE")
    print("=" * 70)
    print()
    print("✅ The Chroma DB has been populated with legal documents.")
    print("✅ You can now start the backend server with:")
    print("   uvicorn backend.main:app --reload")
    print()

if __name__ == "__main__":
    main()
