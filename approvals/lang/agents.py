from langchain_core.tools import tool
from langgraph.types import interrupt, Command
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

from .tools import search, get_city

model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
memory = MemorySaver()
prompt = "You tell people the weather in cities, and you talk like a pirate."

weather_agent = create_react_agent(model, [search, get_city], checkpointer=memory, state_modifier=prompt)

agents = {
    "weather": weather_agent,
}
