from approvals.agent.weather_agent import WeatherAgent

agent_registry = {}


def _register_agent(agent_class):
    agent_instance = agent_class()
    agent_registry[agent_instance.get_name()] = agent_instance


# Register agents
_register_agent(WeatherAgent)


def get_agent(name):
    return agent_registry.get(name)
