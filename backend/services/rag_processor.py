import uuid
import os
import fitz  # PyMuPDF
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter

MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", 50))
MAX_CHUNKS = int(os.getenv("MAX_CHUNKS", 200))
MAX_CSV_ROWS = int(os.getenv("MAX_CSV_ROWS", 1000))

def extract_text_from_pdf(file_bytes: bytes, filename: str, user_id: str, document_id: str):
    """Extracts text from PDF and returns a list of chunks with page metadata."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError("Failed to parse PDF document. File may be malformed or corrupted.") from e

    if doc.is_encrypted:
        raise ValueError("Cannot process encrypted or password-protected PDF documents.")
        
    if len(doc) > MAX_PDF_PAGES:
        raise ValueError(f"Document exceeds the maximum allowed length of {MAX_PDF_PAGES} pages.")

    chunks = []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    for page_num in range(len(doc)):
        if len(chunks) >= MAX_CHUNKS:
            # Stop processing early to protect resources
            break
            
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            page_chunks = text_splitter.split_text(text)
            for i, chunk_text in enumerate(page_chunks):
                if len(chunks) >= MAX_CHUNKS:
                    break
                chunks.append({
                    "id": f"{document_id}_page{page_num+1}_chunk{i}",
                    "text": chunk_text,
                    "metadata": {
                        "user_id": str(user_id),
                        "document_id": str(document_id),
                        "filename": filename,
                        "page": page_num + 1
                    }
                })
                
    if not chunks:
        raise ValueError("No extractable text found in the document.")
        
    return chunks

def extract_text_from_csv(file_bytes: bytes, filename: str, user_id: str, document_id: str):
    """Extracts text from CSV by converting rows to text and returns chunks."""
    from io import BytesIO
    try:
        df = pd.read_csv(BytesIO(file_bytes))
    except Exception as e:
        raise ValueError("Failed to parse CSV document.") from e
        
    if len(df) > MAX_CSV_ROWS:
        raise ValueError(f"CSV document exceeds the maximum allowed length of {MAX_CSV_ROWS} rows.")
        
    chunks = []
    
    # We will treat each row as a chunk if it's small, or split it if it's too large.
    # Usually a row in a CSV is self-contained.
    for index, row in df.iterrows():
        if len(chunks) >= MAX_CHUNKS:
            break
            
        # Convert row to a key-value string
        row_text = ", ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
        if row_text.strip():
            chunks.append({
                "id": f"{document_id}_row{index+1}",
                "text": row_text,
                "metadata": {
                    "user_id": str(user_id),
                    "document_id": str(document_id),
                    "filename": filename,
                    "row": index + 1
                }
            })
            
    if not chunks:
        raise ValueError("No extractable text found in the CSV document.")
        
    return chunks

def process_document(file_bytes: bytes, filename: str, user_id: str, document_id: str):
    """Main routing function for processing supported document types."""
    if filename.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_bytes, filename, user_id, document_id)
    elif filename.lower().endswith('.csv'):
        return extract_text_from_csv(file_bytes, filename, user_id, document_id)
    else:
        raise ValueError("Unsupported file format. Only PDF and CSV are supported.")
