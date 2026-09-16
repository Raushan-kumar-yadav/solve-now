from typing import List, Dict, Any
from .document_processor import DocumentProcessor

class RAGRetriever:
    def __init__(self, documents: List[str] = None):
        self.chunks: List[Dict[str, Any]] = []
        if documents:
            for doc in documents:
                self.add_document_text(doc)

    def add_document_text(self, text: str, source_name: str = "attached_file"):
        doc_chunks = DocumentProcessor.chunk_text(text)
        for c in doc_chunks:
            c["source"] = source_name
            self.chunks.append(c)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.chunks:
            return []

        query_terms = set(query.lower().split())
        scored_chunks = []

        for c in self.chunks:
            content_lower = c["content"].lower()
            # Simple TF-IDF / term overlap score
            score = sum(1 for term in query_terms if term in content_lower)
            if score > 0:
                scored_chunks.append((score, c))

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_chunks[:top_k]]

