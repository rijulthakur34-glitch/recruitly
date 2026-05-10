import pypdf
import os

def parse_jd(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_resume(path: str) -> dict:
    if path.lower().endswith(".pdf"):
        reader = pypdf.PdfReader(path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    else:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    
    return {
        "name": os.path.basename(path),
        "text": text
    }
