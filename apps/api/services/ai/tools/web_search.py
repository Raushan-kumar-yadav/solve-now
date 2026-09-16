import urllib.request
import urllib.parse
import json
import re
import os
from .base import BaseTool

class WebSearchTool(BaseTool):
    name = "web_search"
    description = (
        "A search engine tool to find up-to-date facts, documentation, or technical information on the internet. "
        "Inputs: query (string)."
    )

    def run(self, query: str = "", **kwargs) -> str:
        if not query:
            query = kwargs.get("input", kwargs.get("search_query", ""))
        if not query:
            return "Error: No search query provided."

        # Check if Tavily key is set for enhanced search
        tavily_key = os.environ.get("TAVILY_API_KEY")
        if tavily_key:
            try:
                url = "https://api.tavily.com/search"
                headers = {"Content-Type": "application/json"}
                data = json.dumps({
                    "api_key": tavily_key,
                    "query": query,
                    "max_results": 5
                }).encode("utf-8")
                req = urllib.request.Request(url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=8) as response:
                    res_json = json.loads(response.read().decode("utf-8"))
                    results = res_json.get("results", [])
                    if results:
                        formatted = []
                        for r in results:
                            formatted.append(f"Title: {r.get('title')}\nURL: {r.get('url')}\nSnippet: {r.get('content')}")
                        return "\n\n---\n\n".join(formatted)
            except Exception as e:
                pass # fallback to DuckDuckGo

        # DuckDuckGo Instant Answer API (Free, no key required)
        try:
            params = urllib.parse.urlencode({
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            })
            api_url = f"https://api.duckduckgo.com/?{params}"
            req = urllib.request.Request(
                api_url, 
                headers={"User-Agent": "SolveNow-AI-Bot/1.0"}
            )
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode("utf-8"))
                output = []
                if data.get("AbstractText"):
                    output.append(f"Abstract: {data['AbstractText']} (Source: {data.get('AbstractURL')})")
                
                related = data.get("RelatedTopics", [])
                for topic in related[:4]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        output.append(f"- {topic['Text']}")
                
                if output:
                    return "\n".join(output)
                
                return f"Web search for '{query}' completed, but returned concise or general index entries."
        except Exception as e:
            return f"Search notice: External web search temporarily unavailable ({str(e)}). Proceeding with model knowledge."
