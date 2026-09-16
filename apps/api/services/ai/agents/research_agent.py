from typing import Dict, Any
from ..base import AIProvider
from ..engine.react_agent import SolveNowReactAgent
from ..tools.web_search import WebSearchTool
from ..tools.wikipedia_tool import WikipediaTool
from ..tools.arxiv_tool import ArxivTool
from ..tools.url_reader import URLReaderTool

class ResearchAgent:
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.tools = [WebSearchTool(), WikipediaTool(), ArxivTool(), URLReaderTool()]
        self.agent = SolveNowReactAgent(
            provider=self.provider,
            tools=self.tools,
            role_name="Scientific & Technical Research Specialist"
        )

    def research(self, topic: str, context: str = "") -> Dict[str, Any]:
        system_context = (
            "You are an academic researcher and intelligence analyst. "
            "Gather verified facts, cite sources (arXiv, Wikipedia, web links), "
            "and synthesize comprehensive, well-structured executive summaries."
        )
        if context:
            system_context += f"\n\nContext:\n{context}"

        return self.agent.run(prompt=topic, system_context=system_context)
