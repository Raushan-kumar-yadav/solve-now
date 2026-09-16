import unittest
from services.ai.tools.python_repl import PythonREPLTool
from services.ai.tools.wikipedia_tool import WikipediaTool
from services.ai.tools.arxiv_tool import ArxivTool
from services.ai.tools.url_reader import URLReaderTool
from services.ai.tools.web_search import WebSearchTool
from services.ai.rag.document_processor import DocumentProcessor
from services.ai.rag.retriever import RAGRetriever

class TestAIEngine(unittest.TestCase):
    def test_python_repl_tool(self):
        repl = PythonREPLTool()
        output = repl.run("a = 15; b = 27; print(f'{a} + {b} = {a + b}')")
        self.assertIn("15 + 27 = 42", output)

    def test_python_repl_error_handling(self):
        repl = PythonREPLTool()
        output = repl.run("1 / 0")
        self.assertTrue("ZeroDivisionError" in output or "Execution Error" in output)

    def test_document_processor_chunking(self):
        text = "SolveNow provides real-time collaborative debugging and architectural problem solving."
        chunks = DocumentProcessor.chunk_text(text, chunk_size=25, overlap=5)
        self.assertGreaterEqual(len(chunks), 3)
        self.assertIn("SolveNow", chunks[0]["content"])

    def test_rag_retriever(self):
        retriever = RAGRetriever([
            "PostgreSQL supports ACID transactions, pgvector, and relational indexing.",
            "FastAPI is a modern, fast web framework for building APIs with Python.",
            "Next.js is a React framework for frontend production applications."
        ])
        results = retriever.search("PostgreSQL relational transactions")
        self.assertGreater(len(results), 0)
        self.assertIn("PostgreSQL", results[0]["content"])

if __name__ == "__main__":
    unittest.main()
