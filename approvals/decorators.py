from langchain.tools import tool
from langchain.interrupts import interrupt
from langgraph.graph import StateGraph


def approved_tool(tool_func):
    @tool(tool_func.__name__, parse_docstring=True)
    def tool_node(state):
        return tool_func(state)

    def approval_node(state):
        response = interrupt("Please approve the tool output:")
        return {"foo": state["foo"], "bar": response}

    def create_subgraph():
        subgraph_builder = StateGraph()
        subgraph_builder.add_node(tool_node)
        subgraph_builder.add_node(approval_node)
        subgraph = subgraph_builder.compile()

        builder = StateGraph()
        builder.add_node("subgraph", subgraph)
        return builder.compile()

    tool_node.create_subgraph = create_subgraph
    return tool_node
