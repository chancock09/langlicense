from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from approvals.agent.base_agent import BaseAgent

from langchain_core.tools import tool
from langgraph.types import interrupt

from langchain_community.tools.tavily_search import TavilySearchResults

## Tools


search = TavilySearchResults(k=1)


@tool("get_location", parse_docstring=True)
def get_location():
    """Find the users's current city if they have not provided it"""
    city = interrupt("Please provide city:")

    return city


@tool("add_numbers", parse_docstring=True)
def add_numbers(a: int, b: int):
    """Add two numbers together"""
    return a + b


## Agent


class WeatherAgent(BaseAgent):
    model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    tools = [search, get_location]
    name = "weather_agent"
    prompt = "You tell people the weather in cities, and you talk like a pirate."


class MathAgent(BaseAgent):
    model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    tools = [add_numbers]
    name = "math_agent"
    prompt = "You solve math problems."
