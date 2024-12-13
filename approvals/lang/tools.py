from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langgraph.types import interrupt

search = TavilySearchResults(k=1)


@tool
def get_city(query):
    """Get the current city"""
    city = interrupt("Please provide city:")
    return city
