import urllib.request
import re
from .base import BaseTool

class URLReaderTool(BaseTool):
    name = "url_reader"
    description = (
        "A tool that fetches and extracts readable text from any HTTP/HTTPS URL. "
        "Inputs: url (string)."
    )

    def run(self, url: str = "", **kwargs) -> str:
        if not url:
            url = kwargs.get("input", kwargs.get("link", ""))
        if not url:
            return "Error: No URL provided to read."

        if not (url.startswith("http://") or url.startswith("https://")):
            url = f"https://{url}"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                html = response.read().decode("utf-8", errors="ignore")
                
                # Remove scripts, styles, and html tags
                text = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r'<[^>]+>', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                
                if len(text) > 3000:
                    text = text[:3000] + "... [content truncated]"
                return text or "Webpage loaded but contained no readable text."
        except Exception as e:
            return f"Failed to fetch content from URL '{url}': {str(e)}"

