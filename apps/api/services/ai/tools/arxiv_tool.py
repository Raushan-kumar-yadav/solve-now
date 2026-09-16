import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from .base import BaseTool

class ArxivTool(BaseTool):
    name = "arxiv"
    description = (
        "A tool that searches arXiv for scientific and academic research papers, machine learning studies, math, and computer science papers. "
        "Inputs: query (string)."
    )

    def run(self, query: str = "", **kwargs) -> str:
        if not query:
            query = kwargs.get("input", kwargs.get("search_query", ""))
        if not query:
            return "Error: No search query provided for arXiv."

        try:
            params = urllib.parse.urlencode({
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": 3
            })
            url = f"http://export.arxiv.org/api/query?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "SolveNow-AI-Bot/1.0"})
            with urllib.request.urlopen(req, timeout=8) as response:
                content = response.read().decode("utf-8")
                root = ET.fromstring(content)
                # Atom namespace
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                entries = root.findall("atom:entry", ns)
                if not entries:
                    return f"No arXiv research papers found matching '{query}'."

                results = []
                for entry in entries:
                    title = entry.find("atom:title", ns)
                    summary = entry.find("atom:summary", ns)
                    id_elem = entry.find("atom:id", ns)
                    published = entry.find("atom:published", ns)

                    t_text = title.text.strip().replace("\n", " ") if title is not None else "Unknown Title"
                    s_text = summary.text.strip().replace("\n", " ") if summary is not None else "No summary"
                    link = id_elem.text.strip() if id_elem is not None else ""
                    pub_date = published.text[:10] if published is not None else ""

                    results.append(f"Title: {t_text}\nPublished: {pub_date}\nLink: {link}\nAbstract: {s_text[:400]}...")

                return "\n\n---\n\n".join(results)
        except Exception as e:
            return f"arXiv search error: {str(e)}"
