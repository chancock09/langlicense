from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver
from functools import wraps


DB_URI = "postgresql://postgres:postgres@localhost:5454/postgres?sslmode=disable"


def with_postgres_saver(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with PostgresSaver.from_conn_string(self.db_uri) as checkpointer:
            return func(self, checkpointer, *args, **kwargs)

    return wrapper


class BaseAgent:
    def __init__(self):
        self.db_uri = DB_URI

    def ask(self, question):
        """Ask a question to the agent, no context (and therefore no thread/history/memory)"""
        return self.run(
            inputs={"messages": [["user", question]]},
            config={"configurable": {"thread_id": "ask"}},
        )

    @with_postgres_saver
    def run(self, checkpointer, inputs=None, config=None):
        """Run the agent with inputs and config"""
        from approvals.models import Approval, Result

        graph = self._create_graph(checkpointer)
        output = graph.invoke(inputs, config)
        snapshot = graph.get_state({"configurable": {"thread_id": config["configurable"]["thread_id"]}})

        if snapshot.next:
            return self._create_approval(snapshot, output)
        else:
            return self._create_result(snapshot, output)

    def _create_approval(self, snapshot, output):
        from approvals.models import Approval

        approval = Approval.objects.create(
            snapshot_config=snapshot.config,
            state="pending",
            response=None,
            agent_name=self.get_name(),
            thread_id=snapshot.config["configurable"]["thread_id"],
        )
        return (output, snapshot)

    def _create_result(self, snapshot, output):
        from approvals.models import Result

        result, created = Result.objects.get_or_create(
            snapshot_config=snapshot.config,
            defaults={
                "output": output["messages"][-1].content,
                "agent_name": self.get_name(),
                "thread_id": snapshot.config["configurable"]["thread_id"],
            },
        )
        return (output, snapshot)

    @with_postgres_saver
    def get_state_history(self, checkpointer, config):
        """Return all StateSnapshots from the agent"""
        graph = self._create_graph(checkpointer)
        return list(graph.get_state_history(config))

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
            interrupt_before=["agent"],
        )

    def get_model(self):
        return self.__class__.model

    def get_tools(self):
        return self.__class__.tools

    def get_name(self):
        return self.__class__.name

    def get_prompt(self):
        return self.__class__.prompt

    def get_graph(self):
        pass
