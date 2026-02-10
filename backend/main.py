from fastapi import FastAPI, UploadFile, File
from typing import List
import os
import asyncio
from backend.rag import load_vectorstore
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

#import the text extraction function
from backend.ingestion import extract_text
#import .env  
from dotenv import load_dotenv
load_dotenv()
from backend.rag import build_vectorstore_from_texts

app = FastAPI(title = "Travel Assistant BackEnd")

@app.get('/health')
def health_check():
    import os
    return {"status": "ok", "has_key": os.getenv("OPENAI_API_KEY") is not None}

@app.post('/ingest')
async def ingest_files(files: List[UploadFile] = File(...)):
    saved_files = []
    extracted_files = []
    
    #Define where to save the files
    docs_folder = os.path.join("backend","data", "docs")
    
    # Makes sure folder exists (safe to call every time)
    os.makedirs(docs_folder, exist_ok=True)    
    
   # Save each uploaded file
    for file in files:
        file_path = os.path.join(docs_folder, file.filename)

        # Read file content (async)
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)

        saved_files.append(file_path)
        
        extracted_text, text_path = await asyncio.to_thread(
            extract_text,
            file_path
        )
        
        extracted_files.append({
            "source_file": file.filename,
            "extracted_text_file": text_path,
            "text_preview": extracted_text[:300]  # small preview
        })     
        
                 
    # ======================================
    # AUTO-REINDEX AFTER ALL FILES
    # ======================================
    reindex_result = await asyncio.to_thread(build_vectorstore_from_texts)

    return {
        "message": "Files saved, text extracted, and vectorstore rebuilt.",
        "saved_files": saved_files,
        "extracted_files": extracted_files,
        "vectorstore_status": "Vectorstore updated." if reindex_result else "No text files found."
    }
    
@app.post("/reindex")
async def reindex_vectorstore():
    """
    Rebuild the vectorstore from all .txt files in docs_texts.
    """
    # run in thread to avoid blocking the event loop
    import asyncio

    result = await asyncio.to_thread(build_vectorstore_from_texts)

    if result is None:
        return {"status": "no_texts", "message": "No text files to index."}

    return {"status": "ok", "message": "Vectorstore rebuilt successfully."}

class Question(BaseModel):
    question: str


@app.post("/ask")
async def ask_question(payload: Question):
    """
    RAG pipeline:
    1. Load vectorstore
    2. Retrieve top documents
    3. Build prompt with retrieved context
    4. Ask the LLM
    """
    # 1. Load vectorstore
    vectordb = load_vectorstore()
    if vectordb is None:
        return {"error": "Vectorstore not found. Run /reindex first."}

    # 2. Retrieve relevant chunksno
    retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 10, "fetch_k": 10}
    )
    docs = retriever.invoke(payload.question)

    # Extract raw text for debugging
    retrieved_context = "\n\n".join([d.page_content for d in docs])

    # 3. Build prompt
    prompt = f"""
    You are a helpful travel assistant.

    Use the information below as your primary source to answer the user's question.
    You may interpret the information even if it is incomplete or messy.
    If the context is unclear or contains multiple possibilities, list all relevant information found.
    If the information really has nothing to do with the query, then say 'I dont have enough information to answer'

    Context:
    {retrieved_context}

    Question:
    {payload.question}

    Answer:
    """

    # 4. Ask the LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response = llm.invoke(prompt)

    return {
        "answer": response.content + "\n",
        "sources": [d.metadata.get("source") for d in docs]
    }