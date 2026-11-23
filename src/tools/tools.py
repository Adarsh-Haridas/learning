import os
import requests
import trafilatura
from langchain.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv



load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query: str) -> str:
    """Search the web for the given query using Tavily and return the top results."""
    try:
        response = tavily.search(query=query, max_results=5)
    except Exception as e:
        return f"Web search failed: {e}"

    results = response.get("results", [])
    if not results:
        return "No results found."

    separator = "\n" + "." * 60 + "\n"
    return separator.join(
        f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
        for r in results
    )


@tool
def scrape_url(url: str) -> str:
    """Scrape the given URL and return its clean, readable text content."""
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; LangChainAgent/1.0)"},
            timeout=15,
        )
        response.raise_for_status()
    except Exception as e:
        return f"Failed to fetch {url}: {e}"

    content = trafilatura.extract(
        response.text,
        include_links=False,
        include_comments=False,
        include_tables=True,
    )
    if not content:
        return f"No readable content found at {url}."

    # Keep the output at a size that is safe to pass to an LLM
    max_chars = 8000
    if len(content) > max_chars:
        content = content[:max_chars] + "\n\n[content truncated]"

    return f"URL: {url}\n\n{content}"

