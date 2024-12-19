from langchain_openai import ChatOpenAI
from approvals.agent.base_agent import BaseAgent

from langchain_core.tools import tool


@tool("add_numbers", parse_docstring=True)
def add_numbers(a: int, b: int):
    """Add two numbers together

    Args:
        a: The first number
        b: The second number

    Returns:
        The sum of the two numbers
    """
    return a + b


class MathAgent(BaseAgent):
    model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    tools = [add_numbers]
    name = "math_agent"
    prompt = "You solve math problems."
