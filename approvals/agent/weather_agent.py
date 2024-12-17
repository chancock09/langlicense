from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from approvals.agent.base_agent import BaseAgent, get_city

from langchain_core.tools import tool
from langgraph.types import interrupt

from langchain_community.tools.tavily_search import TavilySearchResults

from django.dispatch import receiver
from django.db.models.signals import post_save
from langgraph.types import Command
from approvals.models import Approval

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


agent = WeatherAgent()


## Helpers


def run_agent(inputs=None, config=None):
    return agent.run(inputs, config)


def render_snapshot(config):
    return agent.render_snapshot(config)


@receiver(post_save, sender=Approval)
def continue_agent(sender, instance, **kwargs):
    if instance.state == "approved":
        # with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        #     graph = create_react_agent(model, tools=[search, get_city], checkpointer=checkpointer)
        #     invoked_result = graph.invoke(Command(resume=instance.response), config=instance.snapshot)
        #     print(invoked_result["messages"][-1].content)
        agent = WeatherAgent()
        result = agent.run(inputs=Command(resume=instance.response), config=instance.snapshot)
        print(result["messages"][-1].content)