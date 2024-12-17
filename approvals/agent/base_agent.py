from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent
from functools import wraps
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.tools import tool
from langgraph.types import interrupt
from approvals.models import Approval
from langgraph.types import Command
from approvals.models import Approval

from django.dispatch import receiver
from django.db.models.signals import post_save

DB_URI = "postgresql://postgres:postgres@localhost:5454/postgres?sslmode=disable"

agent_registry = {}


class BaseAgent:
    def __init__(self, model, tools, name):
        self.db_uri = DB_URI
        self.model = model
        self.tools = tools
        self.name = name
        agent_registry[name] = self

    def run(self, inputs=None, config=None):
        with PostgresSaver.from_conn_string(self.db_uri) as checkpointer:
            graph = create_react_agent(self.model, tools=self.tools, checkpointer=checkpointer)
            result = graph.invoke(inputs, self.config)
            snapshot = graph.get_state(self.config)

            if snapshot.next:
                approval, created = Approval.objects.get_or_create(
                    snapshot=snapshot.config,
                    defaults={"state": "pending", "response": False, "comment": "", "agent_name": self.name},
                )

                return (None, snapshot)
            else:
                return (result, snapshot)

    def reunder_history(self, config):
        with PostgresSaver.from_conn_string(self.db_uri) as checkpointer:
            graph = create_react_agent(self.model, tools=self.tools, checkpointer=checkpointer)

            return graph.get_state_history(config)


@receiver(post_save, sender=Approval)
def continue_agent(sender, instance, **kwargs):
    if instance.state == "approved":

        agent_instance = agent_registry.get(instance.agent_name)

        if agent_instance:
            result = agent_instance.run(inputs=Command(resume=instance.response), config=instance.snapshot)
            print(result["messages"][-1].content)
