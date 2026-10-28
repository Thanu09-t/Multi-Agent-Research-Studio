import os
import json
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")
if not api_key:
    raise ValueError(
        "TAVILY_API_KEY is missing. Check your project-root .env file."
    )

tavily = TavilyClient(api_key=api_key)


@tool
def web_search(query: str) -> str:
    """Search the web and return relevant titles, URLs, and snippets."""
    try:
        results = tavily.search(query=query, max_results=5)
        items = []
        for r in results.get("results", []):
            title = r.get("title", "Untitled")
            url = r.get("url", "")
            content = r.get("content", "")
            items.append(f"Title: {title}\nURL: {url}\nSnippet: {content}")
        return "\n\n---\n\n".join(items) if items else "No relevant web results found."
    except Exception as exc:
        return f"Error performing web search: {exc}"


@tool
def scrape_url(url: str) -> str:
    """Extract readable text from a publicly accessible webpage using fast extraction with fallback."""
    # Method 1: Tavily extract (instant, handles bot-blocks, clean text)
    try:
        extracted = tavily.extract(urls=[url])
        results = extracted.get("results", [])
        if results and results[0].get("raw_content"):
            content = results[0]["raw_content"].strip()
            title = results[0].get("title", "Webpage Content")
            if len(content) > 100:
                return f"Title: {title}\nURL: {url}\n\nContent:\n{content[:10000]}"
    except Exception:
        pass

    # Method 2: Fast HTTP fetch fallback with short timeout
    try:
        response = requests.get(
            url,
            timeout=5,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
            element.decompose()

        title = soup.title.get_text(strip=True) if soup.title else "Untitled"
        content = soup.get_text(separator=" ", strip=True)
        return f"Title: {title}\nURL: {url}\n\nContent:\n{content[:10000]}"

    except Exception as exc:
        return f"Unable to extract content from {url}: {exc}"