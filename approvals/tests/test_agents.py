import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from django.test import TestCase
from django.db import connection
from approvals.models import Approval
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_openai import ChatOpenAI
from approvals.agents.agents import Agent, search, get_city, continue_agent


from django.test import TransactionTestCase


class AgentTestCase(TransactionTestCase):
    def setUp(self):
        self.model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.tools = [search, get_city]
        self.agent = Agent(model=self.model, tools=self.tools)

    def test_run_creates_approval(self):
        inputs = {
            "messages": [
                ("user", "What's the weather in Paris?"),
            ]
        }
        config = {"configurable": {"thread_id": "4321"}}

        self.agent.run(inputs, config)

        approval = Approval.objects.first()
        self.assertIsNotNone(approval)
        self.assertEqual(approval.state, "pending")
        self.assertFalse(approval.response)
        self.assertEqual(approval.comment, "")

    def test_approval_state_change_to_approved(self):
        inputs = {
            "messages": [
                ("user", "What's the weather in Paris?"),
            ]
        }
        config = {"configurable": {"thread_id": "4321"}}

        self.agent.run(inputs, config)

        approval = Approval.objects.first()
        approval.state = "approved"
        approval.response = "The weather in Paris is sunny."
        approval.save()

        with self.assertLogs(level="INFO") as log:
            continue_agent(Approval, approval)

        self.assertIn("The weather in Paris is sunny.", log.output[-1])


if __name__ == "__main__":
    import unittest

    unittest.main()
