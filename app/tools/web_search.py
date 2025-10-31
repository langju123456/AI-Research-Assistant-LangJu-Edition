"""
Web search tool for retrieving information from the internet.
"""
from typing import Optional, List, Dict
from app.tools.base import BaseTool
from app.config import SERPAPI_KEY
from app.utils import logger

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class WebSearchTool(BaseTool):
    """Web search tool using SerpAPI (optional) or DuckDuckGo."""
    
    name = "web_search"
    description = "Searches the web for information. Input should be a search query string."
    
    def __init__(self, api_key: str = None):
        """
        Initialize web search tool.
        
        Args:
            api_key: SerpAPI key (optional)
        """
        self.api_key = api_key or SERPAPI_KEY
    
    def run(self, query: str, max_results: int = 5) -> str:
        """
        Search the web for information.
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            Formatted search results
        """
        if not REQUESTS_AVAILABLE:
            return "Error: requests library not available. Install with: pip install requests"
        
        try:
            if self.api_key:
                return self._search_with_serpapi(query, max_results)
            else:
                return self._search_with_duckduckgo(query, max_results)
        
        except Exception as e:
            error_msg = f"Error searching for '{query}': {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _search_with_serpapi(self, query: str, max_results: int) -> str:
        """Search using SerpAPI."""
        try:
            import requests
            
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": max_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for i, item in enumerate(data.get('organic_results', [])[:max_results], 1):
                title = item.get('title', 'No title')
                snippet = item.get('snippet', 'No description')
                link = item.get('link', '')
                results.append(f"{i}. {title}\n   {snippet}\n   {link}")
            
            if not results:
                return "No results found."
            
            logger.info(f"Web search for '{query}' returned {len(results)} results")
            return "\n\n".join(results)
        
        except Exception as e:
            logger.error(f"SerpAPI search error: {e}")
            return f"Error performing web search: {str(e)}"
    
    def _search_with_duckduckgo(self, query: str, max_results: int) -> str:
        """Search using DuckDuckGo (fallback)."""
        try:
            import requests
            
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Abstract
            if data.get('Abstract'):
                results.append(f"Summary: {data['Abstract']}")
            
            # Related topics
            for i, topic in enumerate(data.get('RelatedTopics', [])[:max_results], 1):
                if isinstance(topic, dict) and 'Text' in topic:
                    text = topic.get('Text', '')
                    url = topic.get('FirstURL', '')
                    if text:
                        results.append(f"{i}. {text}\n   {url}")
            
            if not results:
                return f"No detailed results found for '{query}'. Try a more specific query."
            
            logger.info(f"Web search for '{query}' returned {len(results)} results")
            return "\n\n".join(results)
        
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return f"Error performing web search: {str(e)}"
