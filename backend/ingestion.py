import os
from typing import Tuple
import pdfplumber
import docx  # python-docx
from pathlib import Path
from langchain_openai import ChatOpenAI

#Defines/creates the folder where docs_texts should be saved
TEXT_OUTPUT_DIR = os.path.join("backend", "data", "docs_texts")
os.makedirs(TEXT_OUTPUT_DIR, exist_ok=True)

def _extract_text_from_pdf(path: str) -> str:
    text_chunks = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
    raw_text = "\n\n".join(text_chunks)

    # 2. Repair spacing, line breaks, and word splits using LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    repair_prompt = f"""
    
    Your job is to clean the following text extracted from a PDF. Fix the formatting WITHOUT changing the meaning.

    Fix the following extracted text:
    - Remove duplicated labels when they appear in two languages (e.g., "Partida / Departure:" → "Departure:")
    - Keep the English label and remove ones in different languages.
    - Restore missing spaces between words
    - Reconstruct natural line breaks
    - Fix broken words
    - Do not summarize or remove any content
    - Output only the corrected text
    
    Text to fix:
    {raw_text}
    """

    cleaned_text = llm.invoke(repair_prompt).content
    return cleaned_text
def _extract_text_from_docx(path: str) -> str:
    doc = docx.Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text]
    return "\n\n".join(paragraphs)

def _extract_text_from_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
    
def extract_text(file_path: str) -> Tuple[str, str]:
    """
    Extract text from a file on disk.

    Args:
        file_path: Path to the saved file (PDF, DOCX, TXT)

    Returns:
        (extracted_text, saved_txt_path)
        - extracted_text: the string extracted from the document
        - saved_txt_path: path where the .txt version was saved
    """
    p = Path(file_path)
    suffix = p.suffix.lower()

    if suffix in [".pdf"]:
        extracted = _extract_text_from_pdf(file_path)
    elif suffix in [".docx", ".doc"]:
        extracted = _extract_text_from_docx(file_path)
    elif suffix in [".txt", ".md"]:
        extracted = _extract_text_from_txt(file_path)
    else:
        # Unknown type — return empty string to be explicit
        extracted = ""

    # Save extracted text to backend/data/docs_texts/<original_filename>.txt
    base_name = p.stem
    txt_filename = f"{base_name}.txt"
    txt_path = os.path.join(TEXT_OUTPUT_DIR, txt_filename)
    try:
        with open(txt_path, "w", encoding="utf-8") as f: + f.write(extracted)
    except Exception as e:
        # If saving fails, still return the text and a None or partial path
        return extracted, None

    return extracted, txt_path