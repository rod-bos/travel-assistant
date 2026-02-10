# backend/rag.py

import os
import re

from dotenv import load_dotenv

load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


TXT_FOLDER = "backend/data/docs_texts"
PERSIST_DIR = "backend/data/vectorstore"

def clean_text(text: str) -> str:
    # Remove useless underscores and repeated underscores
    text = text.replace("_", " ")

    cleaned_lines = []
    for line in text.split("\n"):
        line = line.strip()

        # Skip empty lines or very short noise
        if len(line) < 3:
            continue

        # Collapse multiple spaces
        line = " ".join(line.split())

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def extract_passenger_name(text: str) -> str | None:
    # Looks for patterns like: Passageiro / Passenger: John Doe
    match = re.search(
        r"Passageiro\s*/\s*Passenger:\s*([A-Za-zÀ-ÿ ]+)",
        text
    )
    if match:
        return match.group(1).strip()
    return None

def build_vectorstore_from_texts():

    # 1. Load all extracted txt files
    texts = []
    metadatas = []
    
    for filename in os.listdir(TXT_FOLDER):
        if filename.endswith(".txt"):
            path = os.path.join(TXT_FOLDER, filename)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
                content = clean_text(raw)
                passenger_name = extract_passenger_name(content)
                
            texts.append(content)
            metadatas.append({
                "source": filename,
                "passenger": passenger_name
            })
    if not texts:
        print("No text files found. Nothing to index.")
        return None
    
    # 2. Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    chunks = splitter.create_documents(texts, metadatas=metadatas)

    embeddings = OpenAIEmbeddings()
    os.makedirs(PERSIST_DIR, exist_ok=True)
    vectordb = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
    )
    vectordb.persist()

    print("Vectorstore created.")
    return vectordb  
          
def load_vectorstore():
    """
    Load the existing Chroma vectorstore stored in backend/data/vectorstore.
    Returns the vectordb object or None if the vectorstore does not exist.
    """
    if not os.path.exists(PERSIST_DIR):
        print("No vectorstore found. Run /reindex first.")
        return None

    embeddings = OpenAIEmbeddings()

    vectordb = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

    return vectordb