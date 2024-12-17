from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver


DB_URI = "postgresql://postgres:postgres@localhost:5454/postgres?sslmode=disable"


class BaseAgent:
    def __init__(self):
        self.db_uri = DB_URI

    def run(self, inputs=None, config=None):
        from approvals.models import Approval

        with PostgresSaver.from_conn_string(self.db_uri) as checkpointer:
            graph = self._create_graph(checkpointer)
            result = graph.invoke(inputs, config)
            snapshot = graph.get_state(config)

            if snapshot.next:
                approval, created = Approval.objects.get_or_create(
                    snapshot_config=snapshot.config,
                    defaults={"state": "pending", "response": False, "comment": "", "agent_name": self.get_name()},
                )

                return (None, snapshot)
            else:
                return (result, snapshot)

    def render_history(self, config):
        with PostgresSaver.from_conn_string(self.db_uri) as checkpointer:
            graph = self._create_graph(checkpointer)

            result = []

            for step in graph.get_state_history(config):
                result.append(step)

            return result

    def _create_graph(self, checkpointer):
        return create_react_agent(
            self.get_model(),
            tools=self.get_tools(),
            checkpointer=checkpointer,
            state_modifier=self.get_prompt(),
        )

    def get_model(self):
        return self.__class__.model

    def get_tools(self):
        return self.__class__.tools

    def get_name(self):
        return self.__class__.name

    def get_prompt(self):
        return self.__class__.prompt
