from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver


DB_URI = "postgresql://postgres:postgres@localhost:5454/postgres?sslmode=disable"


class BaseAgent:
    def __init__(self):
        self.db_uri = DB_URI

    def ask(self, question):
        """Ask a question to the agent, no context (and therefore no thread/history/memory)"""

        return self.run(
            inputs={"messages": [["user", question]]},
            config={"configurable": {"thread_id": "ask"}},  # TODO: idk... we need thread_id for checkpointing?
        )

    def run(self, inputs=None, config=None):
        """Run the agent with inputs and config"""

        from approvals.models import Approval, Result

        with PostgresSaver.from_conn_string(self.db_uri) as checkpointer:
            graph = self._create_graph(checkpointer)
            output = graph.invoke(inputs, config)

            print("\n\n")

            print("output", output)

            print("\n\n")

            snapshot = graph.get_state({"configurable": {"thread_id": config["configurable"]["thread_id"]}})

            print("snapshot", snapshot)

            print("\n\n")

            if snapshot.next:
                approval = Approval.objects.create(
                    snapshot_config=snapshot.config,
                    state="pending",
                    response=None,
                    agent_name=self.get_name(),
                    thread_id=snapshot.config["configurable"]["thread_id"],
                )

                return (output, snapshot)
            else:
                print("RESULT")
                result, created = Result.objects.get_or_create(
                    snapshot_config=snapshot.config,
                    defaults={
                        "output": output["messages"][-1].content,
                        "agent_name": self.get_name(),
                        "thread_id": snapshot.config["configurable"]["thread_id"],
                    },
                )

                return (output, snapshot)

    def get_state_history(self, config):
        """Return all StateSnapshots from the agent"""
        with PostgresSaver.from_conn_string(self.db_uri) as checkpointer:
            graph = self._create_graph(checkpointer)

            result = []

            for step in graph.get_state_history(config):
                result.append(step)

            return result

    def pretty_print_history(self, config):
        history = self.get_state_history(config)
        messages = history[0].values["messages"]

        return "\n".join([msg.pretty_repr() for msg in messages[::-1]])

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
