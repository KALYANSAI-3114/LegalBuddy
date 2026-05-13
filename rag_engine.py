"""
RAG Engine - Extracted from notebook
Handles all RAG logic: document loading, embeddings, retrieval, and LLM calls
"""

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
import ollama
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# System prompt — strict grounding to prevent hallucination
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a helpful Indian Legal Assistant. Answer questions about Indian law in simple, modern language.

RULES:
1. Answer in plain English - not robotic legal jargon
2. Be concise and direct (2-3 sentences max for basic questions)
3. Use simple words, avoid outdated language like "hereinafter", "whereby", etc.
4. Only use information from the provided context - never make up information
5. If the context doesn't answer the question, say: "I don't have information on this in my database."
6. Mention relevant Act names and years (e.g., "IPC 1860", "BNS 2024")
7. Keep it user-friendly, not a law textbook"""

# Relevance score threshold — deprecated, using simple similarity search now
# RELEVANCE_THRESHOLD = 0.15


class LegalRAGEngine:
    def __init__(self, data_folder="data", chroma_db_path="./chroma_db", model_name="phi3:mini"):
        """Initialize the RAG Engine
        
        Args:
            data_folder: Path to folder containing PDF documents
            chroma_db_path: Path to ChromaDB persistent directory
            model_name: Ollama model name to use for generation
        """
        self.data_folder = data_folder
        self.chroma_db_path = chroma_db_path
        self.model_name = model_name
        self.vector_store = None
        self.embedding_model = None
        
    def initialize(self):
        """Initialize the RAG system - load documents, embeddings, and vectorstore"""
        print("Initializing RAG Engine...")
        
        # Step 1: Load embeddings
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("✓ Embeddings model loaded")
        
        # Step 2: Load vectorstore from persistent directory
        self.vector_store = Chroma(
            persist_directory=self.chroma_db_path,
            embedding_function=self.embedding_model
        )
        print("✓ Vector store loaded from Chroma DB")
        
        print(f"✓ Using LLM model: {self.model_name}")
        print("RAG Engine initialized successfully!\n")
        
    def train_from_pdfs(self):
        """Train the RAG system from PDF documents"""
        print("Starting training from PDFs...")
        
        # Step 1: Data Ingestion
        documents = []
        if not os.path.exists(self.data_folder):
            print(f"ERROR: {self.data_folder} folder not found")
            return False
            
        pdf_files = [f for f in os.listdir(self.data_folder) if f.endswith(".pdf")]
        
        if not pdf_files:
            print(f"ERROR: No PDF files found in {self.data_folder}")
            return False
        
        print(f"Found {len(pdf_files)} PDF files to process:")
        for file in pdf_files:
            print(f"  • {file}")
        
        for file in pdf_files:
            file_path = os.path.join(self.data_folder, file)
            print(f"\n📄 Loading: {file}")
            try:
                loader = PyPDFLoader(file_path)
                pdf_docs = loader.load()
                
                if not pdf_docs:
                    print(f"   ⚠️  No pages extracted from {file}")
                    continue
                
                for doc in pdf_docs:
                    doc.metadata["source"] = file
                documents.extend(pdf_docs)
                print(f"   ✓ Loaded {len(pdf_docs)} pages")
            except Exception as e:
                print(f"   ✗ Error loading {file}: {e}")
                continue
        
        if not documents:
            print("\nERROR: No documents were successfully loaded!")
            return False
            
        print(f"\n✓ Total pages loaded: {len(documents)}")
        
        # Step 2: Text Splitting — smaller chunks for more focused retrieval
        print("\nSplitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=200,
        )
        chunks = text_splitter.split_documents(documents)
        print(f"✓ Total chunks created: {len(chunks)}")
        
        # Step 3: Initialize embeddings
        print("\nInitializing embeddings model...")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("✓ Embeddings model loaded")
        
        # Step 4: Create and persist vectorstore
        print("\nCreating vector store and indexing chunks...")
        try:
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedding_model,
                persist_directory=self.chroma_db_path
            )
            print("✓ Vector store created and persisted to Chroma DB")
        except Exception as e:
            print(f"ERROR: Failed to create vector store: {e}")
            return False
        
        print("\n✅ Training completed successfully!")
        return True
        
    def ask_ollama(self, query, context):
        """Call Ollama LLM with structured legal prompt - fast & natural"""
        try:
            user_message = f"""Answer this legal question based ONLY on the information below.
Keep your answer simple, clear, and user-friendly (not robotic legal jargon).

CONTEXT:
{context}

QUESTION: {query}

Answer:"""
            
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                stream=False,
                options={
                    "num_predict": 150,  # Even shorter - max 150 tokens
                    "temperature": 0.3,  # Slightly warmer for natural language
                    "top_k": 40,
                    "top_p": 0.9,
                }
            )
            
            answer = response.get("message", {}).get("content", "").strip()
            if not answer:
                raise ValueError("Empty response from Ollama")
            
            return answer
        except Exception as e:
            print(f"  Error calling Ollama: {e}")
            raise Exception(f"Failed to generate answer from LLM: {str(e)}")
    
    def query(self, user_query):
        """Process a legal question through the RAG pipeline - ultra-fast"""
        if not self.vector_store:
            raise Exception("RAG Engine not initialized. Call initialize() first.")
        
        # Retrieve only 2 most relevant chunks (super fast)
        results = self.vector_store.similarity_search(user_query, k=2)
        
        if not results:
            return {
                "answer": "I don't have information on this in my database. Please try rephrasing your question or ask about a different legal topic.",
                "sources": []
            }
        
        # Log retrieval for debugging
        print(f"  Retrieved {len(results)} chunks for answer")
        for doc in results:
            source = doc.metadata.get('source', 'Unknown')
            print(f"    Source: {source}")
        
        # Create lean context (no redundant metadata)
        context = "\n\n".join([doc.page_content for doc in results])
        
        # Generate answer using Ollama
        answer = self.ask_ollama(user_query, context)
        
        # Collect unique source documents
        sources = list(set([
            doc.metadata.get("source", "Unknown") 
            for doc in results
        ]))
        
        return {
            "answer": answer,
            "sources": sources
        }


if __name__ == "__main__":
    # Example usage
    engine = LegalRAGEngine()
    
    # Check if database exists and has content
    import glob
    chroma_path = Path("./chroma_db/b080aa20-49cb-4e6a-a37f-99e2338b7215/data/embeddings.parquet")
    db_exists = chroma_path.exists()
    
    if not db_exists:
        print("⚠️  Chroma DB is empty. Indexing documents...")
        engine.train_from_pdfs()
    else:
        print("✓ Chroma DB found. Loading existing data...")
    
    engine.initialize()
    
    # Query the RAG system
    print("\n" + "="*70)
    print("TESTING RAG SYSTEM")
    print("="*70 + "\n")
    
    test_queries = [
        "How to file an FIR?",
        "What are the different IPC sections?",
        "What is the Indian Penal Code?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        result = engine.query(query)
        print(f"✓ Answer: {result['answer'][:200]}...")
        print(f"✓ Sources: {result['sources']}")
        print("-" * 70)
