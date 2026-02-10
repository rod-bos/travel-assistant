# 🧭 Travel Assistant — Developer Guide

**Travel Assistant** is an AI-powered RAG (Retrieval-Augmented Generation) application built with **FastAPI**, **LangChain**, **Chroma**, and **Streamlit**.  
It allows you to upload travel-related documents (like tickets, hotel reservations, itineraries) and ask natural-language questions about them.

---

## ⚙️ Project Structure

```
travel_assistant/
│
├── backend/
│   ├── main.py                # FastAPI app (API endpoints + RAG logic)
│   ├── ingestion.py           # Handles document extraction and cleaning
│   ├── rag.py                 # Vectorstore creation and loading
│   ├── requirements.txt       # Backend dependencies
│   └── data/
│       ├── docs/              # Uploaded PDFs
│       ├── docs_texts/        # Cleaned text extracted from PDFs
│       └── vectorstore/       # Persistent Chroma vector database
│
├── frontend/
│   └── app.py                 # Streamlit frontend
│
└── .env                       # Environment variables
```

---

## 🧬 Requirements

- **Python 3.11+**
- **Anaconda** (recommended)
- **pip**
- **OpenAI API key**

---

## 🧱 Setup Instructions

### 1️⃣ Create and activate a new environment
```bash
conda create -n travelassistant python=3.11
conda activate travelassistant
```

### 2️⃣ Install dependencies
Inside the `backend` folder:
```bash
pip install -r requirements.txt
```

Your `requirements.txt` should contain:
```
fastapi
uvicorn
langchain
langchain-openai
langchain-community
langchain-text-splitters
chromadb
pdfplumber
python-docx
streamlit
python-dotenv
```

---

## 🔑 Environment Variables

Create a `.env` file in the **project root** (`travel_assistant/.env`):

```
OPENAI_API_KEY=sk-your-openai-key-here
```

> ⚠️ Never commit your `.env` file to Git.

---

## 🚀 Running the Application

### 🧠 Start the FastAPI backend
From inside the `backend` folder:
```bash
uvicorn backend.main:app --reload
```

Then open:
- **Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### 💻 Start the Streamlit frontend
From the `frontend` folder:
```bash
streamlit run app.py
```

The interface will open automatically in your browser at:
[http://localhost:8501](http://localhost:8501)

---

## 📂 Workflow Overview

1️⃣ **Upload travel documents** (PDF or DOCX).  
   They’ll be stored in `backend/data/docs/`.

2️⃣ **Automatic text extraction and cleaning**  
   Text is extracted with **pdfplumber** and cleaned for spacing and readability.  
   Cleaned `.txt` files are saved to `backend/data/docs_texts/`.

3️⃣ **Vectorstore indexing**  
   After uploading, the app automatically rebuilds the **Chroma vector database** (`backend/data/vectorstore/`).

4️⃣ **Ask questions**  
   Use the chat interface or the `/ask` endpoint to query your documents.

Example queries:
- “Who is traveling?”
- “When is the return flight?”
- “How much was paid for accommodation?”

---

## 🧪 Troubleshooting

| Problem | Cause | Fix |
|----------|--------|-----|
| `ModuleNotFoundError: ChatOpenAI` | Missing dependency | `pip install langchain-openai` |
| Missing spaces in PDF text | Common with airline PDFs | Already mitigated with cleaner |
| RAG returns incomplete answers | Vectorstore missing | Run `/reindex` after upload |
| UI not refreshing after upload | Cached state | Refresh Streamlit page manually |

---

## ✨ Author

**Rodrigo Bossan**  
AI Developer • Travel Enthusiast  
Built with FastAPI, LangChain, and Streamlit.

