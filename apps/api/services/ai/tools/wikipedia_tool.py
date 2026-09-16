import urllib.request
import urllib.parse
import json
from .base import BaseTool

class WikipediaTool(BaseTool):
    name = "wikipedia"
    description = (
        "A tool that searches Wikipedia for encyclopedic summaries of concepts, historical topics, algorithms, or theories. "
        "Inputs: query (string)."
    )

    def run(self, query: str = "", **kwargs) -> str:
        if not query:
            query = kwargs.get("input", kwargs.get("topic", ""))
        if not query:
            return "Error: No search query provided for Wikipedia."

        try:
            encoded_title = urllib.parse.quote(query.strip().replace(" ", "_"))
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "SolveNow-AI-Bot/1.0 (contact: info@solvenow.local)"}
            )
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode("utf-8"))
                extract = data.get("extract")
                if extract:
                    return f"Wikipedia Summary for '{data.get('title', query)}':\n{extract}"
                return f"No detailed summary found on Wikipedia for '{query}'."
        except urllib.error.HTTPError as he:
            if he.code == 404:
                return f"Wikipedia page not found for '{query}'."
            return f"Wikipedia request error: HTTP {he.code}"
        except Exception as e:
            return f"Wikipedia lookup error: {str(e)}"

