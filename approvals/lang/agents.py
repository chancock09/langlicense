from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from functools import wraps
from django.db.models.signals import post_save
from django.dispatch import receiver
from approvals.models import Approval
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langgraph.types import interrupt

search = TavilySearchResults(k=1)


@tool
def get_city(query):
    """Get the current city"""
    city = interrupt("Please provide city:")
    return city


tools = [search, get_city]
model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
prompt = "You tell people the weather in cities, and you talk like a pirate."
default_input = {
    "messages": [
        ("user", "What's the weather in Paris?"),
    ]
}
default_config = {"configurable": {"thread_id": "12"}}

DB_URI = "postgresql://postgres:postgres@localhost:5454/postgres?sslmode=disable"


def run_agent(inputs=None, config=None):
    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        graph = create_react_agent(model, tools=tools, checkpointer=checkpointer)
        result = graph.invoke(inputs, config)
        snapshot = graph.get_state(config)

        if snapshot.next:
            approval, created = Approval.objects.get_or_create(
                snapshot=snapshot.config,
                defaults={"state": "pending", "response": False, "comment": ""},
            )

            print(f"approval {approval.id}, created: {created}")

            return (None, snapshot)
        else:
            return (result, snapshot)


def render_snapshot(config):
    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        graph = create_react_agent(model, tools=tools, checkpointer=checkpointer)

        all_states = []
        for state in graph.get_state_history(config):
            all_states.append(state)

        return all_states


@receiver(post_save, sender=Approval)
def continue_agent(sender, instance, **kwargs):
    if instance.state == "approved":
        with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
            graph = create_react_agent(model, tools=[search, get_city], checkpointer=checkpointer)
            invoked_result = graph.invoke(Command(resume=instance.response), config=instance.snapshot)
            print(invoked_result["messages"][-1].content)
