from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from functools import wraps
from django.db.models.signals import post_save
from django.dispatch import receiver
from approvals.models import Approval
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.tools import tool
from langgraph.types import interrupt


DB_URI = "postgresql://postgres:postgres@localhost:5454/postgres?sslmode=disable"


class BaseAgent:
    def __init__(self, model, tools, name):
        self.db_uri = DB_URI
        self.model = model
        self.tools = tools
        self.name = name

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

    def render_snapshot(self, config):
        with PostgresSaver.from_conn_string(self.db_uri) as checkpointer:
            graph = create_react_agent(self.model, tools=self.tools, checkpointer=checkpointer)

            all_states = []
            for state in graph.get_state_history(config):
                all_states.append(state)

            return all_states


@receiver(post_save, sender=Approval)
def continue_agent(sender, instance, **kwargs):
    if instance.state == "approved":
        # with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        #     graph = create_react_agent(model, tools=[search, get_city], checkpointer=checkpointer)
        #     invoked_result = graph.invoke(Command(resume=instance.response), config=instance.snapshot)
        #     print(invoked_result["messages"][-1].content)
        agent = BaseAgent(model, tools)
        result = agent.run(inputs=Command(resume=instance.response), config=instance.snapshot)
        print(result["messages"][-1].content)
