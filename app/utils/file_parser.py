import io
import fitz  # PyMuPDF
from docx import Document
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

async def extract_text_from_file(file: UploadFile) -> str:
    content = await file.read()
    filename = file.filename.lower()
    
    if filename.endswith(".pdf"):
        # Extract from PDF
        with fitz.open(stream=content, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text
            
    elif filename.endswith((".docx", ".doc")):
        # Extract from Word
        #logger.info("Word Document Found")
        doc = Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])
        
    elif filename.endswith(".txt"):
        return content.decode("utf-8")
    
    else:
        # Fallback for unknown types (try decoding as text)
        try:
            return content.decode("utf-8")
        except:
            return ""
