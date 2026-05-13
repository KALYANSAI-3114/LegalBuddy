# LegalBuddy — AI-Powered Legal Assistant

> **Your intelligent guide to Indian law.** Ask questions about Indian legal codes in plain English and get instant, sourced answers powered by RAG (Retrieval-Augmented Generation) and Ollama.

[![LegalBuddy](https://img.shields.io/badge/LegalBuddy-Legal_Assistant-D4A03C?style=for-the-badge)](https://github.com)
![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)

---

## ✨ Features

- **📖 Plain-English Legal Q&A** — Ask about laws, rights, and procedures in everyday language
- **📚 Source-Backed Answers** — Every response cites the legal documents it was sourced from
- **⚡ Fast Responses** — Get answers in 15-30 seconds (after initial model load)
- **🏛️ Comprehensive Coverage** — Access Indian Penal Code, CRPC, Constitution, IT Act, and more
- **🎨 Modern UI** — Navy & gold professional theme with responsive design
- **📡 Real-Time Status** — Live health indicator for Ollama and RAG connectivity
- **🔒 Privacy-First** — All processing happens locally - no data sent to external services
- **⚙️ Customizable** — Easy to add new legal documents or adjust LLM parameters

---

## 📁 Project Structure

```
legal-rag-application/
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── rag_engine.py                   # RAG pipeline core
├── test_rag.py                     # System testing script
├── initialize_db.py                # Database initialization
│
├── backend/
│   ├── main.py                     # FastAPI server
│   ├── requirements.txt            # Backend dependencies
│   └── .env                        # Configuration (not in repo)
│
├── frontend/
│   ├── index.html                  # Main UI
│   ├── app.js                      # Client logic
│   └── style.css                   # Styling
│
├── data/
│   └── *.pdf                       # Legal document PDFs
│
└── chroma_db/
    └── (Generated on first run)    # Vector database
```

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- **Python 3.10+** ([download](https://www.python.org/downloads/))
- **Ollama** installed and running ([download](https://ollama.com))
- **phi3:mini model** pulled in Ollama

### Step 1: Start Ollama Service

```bash
ollama serve
```

In another terminal, ensure the model is available:

```bash
ollama pull phi3:mini
ollama list  # Should show phi3:mini
```

### Step 2: Clone & Setup

```bash
# Clone repository (or extract files)
cd legal-rag-application

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### Step 3: Initialize Database (First Time Only)

```bash
# This indexes all PDFs into the vector store (~5-15 minutes)
python initialize_db.py
```

**Expected output:**
```
✓ Total pages loaded: 1527
✓ Total chunks created: 8093
✓ Embeddings model loaded
✓ Vector store created and persisted to Chroma DB

✅ Training completed successfully!
✅ DATABASE INITIALIZATION COMPLETE
```

### Step 4: Start Backend Server

```bash
cd backend
uvicorn main:app --reload
```

**Expected output:**
```
✅ RAG Engine ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 5: Open Application

Open your browser and navigate to:

```
http://localhost:8000
```

---

## 🧪 Testing

### Verify Installation

```bash
# Test the RAG system with sample queries
python test_rag.py
```

### Sample Questions

Try these in the web interface:

1. **"What is the Indian Penal Code?"**
   - Response time: 15-30 seconds
   - Expected: Simple, clear definition mentioning BNS 2024

2. **"How to file an FIR?"**
   - Response time: 15-30 seconds
   - Expected: Step-by-step CRPC Section 154 procedures

3. **"What are fundamental rights?"**
   - Response time: 15-30 seconds
   - Expected: Constitutional articles with examples

4. **"What is the Right to Information?"**
   - Response time: 15-30 seconds
   - Expected: RTI Act basics with filing procedure

---

## 🔌 API Reference

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "rag_engine": "ready",
  "ollama": "connected",
  "model": "phi3:mini"
}
```

### Ask Legal Question

```bash
POST /chat
Content-Type: application/json

{
  "query": "What is the Indian Constitution?"
}
```

**Response:**
```json
{
  "answer": "The Indian Constitution is the supreme law of India, adopted in 1950. It defines the structure of the government, fundamental rights, and duties of citizens...",
  "sources": ["constittion_pdf.pdf"]
}
```

---

## ⚙️ Configuration

### Environment Variables (Optional)

Create `backend/.env`:

```ini
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
```

### Switch LLM Models

To use a different Ollama model:

```bash
# Pull a different model
ollama pull llama3:latest

# Update backend/.env
OLLAMA_MODEL=llama3:latest

# Restart backend server
```

### Add More Legal Documents

1. Place PDF files in the `data/` folder
2. Run initialization again:
   ```bash
   python initialize_db.py
   ```
3. Restart backend server

---

## 🎯 Performance

| Metric | Value |
|--------|-------|
| **First response** | 45-60 seconds (model loading) |
| **Subsequent queries** | 15-30 seconds |
| **Retrieved chunks** | 2 (focused, fast) |
| **Max response length** | 150 tokens (~200 words) |
| **Database size** | 1,527 pages indexed |
| **Total chunks** | 8,093 |

---

## 🔧 Troubleshooting

### Issue: "Cannot connect to Ollama"

**Solution:**
```bash
# Ensure Ollama is running
ollama serve

# Check Ollama is accessible
curl http://localhost:11434/api/tags
```

### Issue: "No relevant information found" for all queries

**Solution:**
```bash
# Reinitialize the database
python initialize_db.py

# Verify initialization completed successfully
python test_rag.py
```

### Issue: Slow responses (5+ minutes)

**Solution:**
- Check CPU usage - model runs on CPU without GPU
- Verify Ollama is responsive: `ollama list`
- First query is always slower (model loads into memory)
- Restart backend: `uvicorn backend.main:app --reload`

### Issue: Module import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
pip install -r backend/requirements.txt --force-reinstall
```

---

## 🏗️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML, CSS, Vanilla JavaScript |
| **Backend** | FastAPI, Uvicorn |
| **LLM** | Ollama (Phi3:mini) |
| **Embeddings** | HuggingFace Sentence-Transformers |
| **Vector DB** | ChromaDB |
| **RAG Framework** | LangChain |

---

## 📚 Document Coverage

- ✅ **Indian Penal Code (IPC)** - 119 pages
- ✅ **Code of Criminal Procedure (CRPC)** - 263 pages
- ✅ **Indian Constitution** - 402 pages
- ✅ **Information Technology Act 2000** - 36 pages
- ✅ **Right to Information Act** - 27 pages
- ✅ **Companies Act** - 370 pages
- ✅ **CPA** - 40 pages
- ✅ **Other Acts** - 453+ pages

**Total: 1,527 pages indexed into 8,093 searchable chunks**

---

## ⚠️ Disclaimer

This tool provides **general legal information only**, not legal advice. While we strive for accuracy, legal information can be complex and varies by jurisdiction. Always consult a qualified lawyer for:

- Legal advice on specific matters
- Court proceedings
- Important legal decisions
- Contracts and agreements

---

## 📝 Development Notes

### Adding New Functionality

1. **New PDF documents**: Add to `data/` folder, run `initialize_db.py`
2. **Custom system prompt**: Edit `SYSTEM_PROMPT` in `rag_engine.py`
3. **Different LLM model**: Update `OLLAMA_MODEL` in `backend/.env`
4. **Response length**: Adjust `num_predict` in `rag_engine.py`

### Code Quality

- Clean architecture with separated concerns (backend, frontend, RAG engine)
- Comprehensive error handling
- Production-ready configurations
- Well-documented code with docstrings
- Type hints throughout

---

## 🚀 Deployment

### Local Deployment

Already set up! Just run the steps in Quick Start.

### Production Deployment (Gunicorn + Nginx)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn (4 workers)
cd backend
gunicorn main:app -w 4 -b 0.0.0.0:8000

# Use Nginx as reverse proxy (configure separately)
```

### Docker Deployment

Create `Dockerfile` if deploying to production containers.

---

## 📞 Support

### Common Questions

**Q: How often should I update the database?**
A: Whenever you add new PDF documents to the `data/` folder.

**Q: Can I run without internet?**
A: Yes! Everything runs locally. Internet only needed for first dependency install.

**Q: What if a query takes too long?**
A: First query loads the model (~60s). Restart Ollama if it hangs.

**Q: Can I use a different LLM?**
A: Yes! Install any Ollama model and update `.env`

---

## 🙏 Acknowledgments

- **LangChain** - For the RAG framework
- **Ollama** - For local LLM inference
- **ChromaDB** - For vector storage
- **FastAPI** - For the backend server
- **HuggingFace** - For embeddings models

---

## ✅ Verification Checklist

Before considering setup complete:

- [ ] Ollama service running (`ollama serve`)
- [ ] `python initialize_db.py` completed successfully
- [ ] Backend server starts without errors
- [ ] Frontend loads at http://localhost:8000
- [ ] Test query returns an answer with sources
- [ ] `/health` endpoint shows "ok" status
- [ ] Response time is 15-30 seconds
- [ ] Answers are clear and conversational (not robotic)


