from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from approvals.agent.base_agent import BaseAgent

from langchain_core.tools import tool
from langgraph.types import interrupt

from langchain_community.tools.tavily_search import TavilySearchResults

## Config


prompt = "You tell people the weather in cities, and you talk like a pirate."
default_input = {
    "messages": [
        ("user", "What's the weather in Paris?"),
    ]
}
default_config = {"configurable": {"thread_id": "12"}}


## Tools


search = TavilySearchResults(k=1)


@tool
def get_city(query):
    """Get the current city"""
    city = interrupt("Please provide city:")
    return city


## Implement Agent


class WeatherAgent(BaseAgent):
    def __init__(self):
        model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        tools = [search, get_city]
        name = "weather_agent"
        super().__init__(model, tools, name)


wather_agent = WeatherAgent()
