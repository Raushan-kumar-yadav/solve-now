import os
from typing import List, Dict, Any

class DocumentProcessor:
    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."

        ext = os.path.splitext(file_path)[1].lower()

        try:
            # Text & Code formats
            if ext in [".txt", ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".csv", ".md", ".yaml", ".yml", ".sql", ".sh"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()

            # PDF Extraction (using pypdf if available, or basic stream parser)
            elif ext == ".pdf":
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    text = []
                    for page in reader.pages:
                        t = page.extract_text()
                        if t:
                            text.append(t)
                    return "\n".join(text) or "PDF file contained no extractable text."
                except ImportError:
                    # Fallback plain extraction
                    with open(file_path, "rb") as f:
                        raw = f.read().decode("latin1", errors="ignore")
                        import re
                        strings = re.findall(r'[A-Za-z0-9\s.,;:\-_\'"()]{4,}', raw)
                        return " ".join(strings)[:4000]

            else:
                return f"Unsupported file type: {ext}"
        except Exception as e:
            return f"Error reading file {os.path.basename(file_path)}: {str(e)}"

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[Dict[str, Any]]:
        chunks = []
        start = 0
        text_len = len(text)
        chunk_id = 0

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append({
                    "chunk_id": chunk_id,
                    "content": chunk_content,
                    "char_start": start,
                    "char_end": end
                })
                chunk_id += 1
            start += (chunk_size - overlap)

        return chunks

