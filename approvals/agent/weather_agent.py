from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from approvals.agent.base_agent import BaseAgent

from langchain_core.tools import tool
from langgraph.types import interrupt

from langchain_community.tools.tavily_search import TavilySearchResults

## Config

default_input = {"messages": [["user", "What's the weather in Paris?"]]}
default_config = {"configurable": {"thread_id": "123"}}


## Tools


search = TavilySearchResults(k=1)


@tool("get_city", parse_docstring=True)
def get_city():
    """Find the users's current city if they have not provided it"""
    city = interrupt("Please provide city:")
    return city


## Implement Agent


class WeatherAgent(BaseAgent):
    model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    tools = [search, get_city]
    name = "weather_agent"
    prompt = "You tell people the weather in cities, and you talk like a pirate."
