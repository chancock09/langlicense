from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent
from functools import wraps
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.tools import tool
from langgraph.types import interrupt
from approvals.models import Approval

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

            return graph.get_state(config)
