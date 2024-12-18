from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from approvals.agent import get_agent
from langgraph.types import Command

# TODO: this!!!
# https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/review-tool-calls/#simple-usage

# Create your models here.

User = get_user_model()


class Trigger(models.Model):
    """Triggers a run of an agent"""

    thread_id = models.CharField(max_length=255, blank=True, null=True)
    agent_name = models.CharField(max_length=255)
    input = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Trigger)
def handle_trigger(sender, instance, created, **kwargs):
    if created:
        agent = get_agent(instance.agent_name)

        if agent:
            agent.run(
                inputs={"messages": [["user", instance.input]]},
                config={"configurable": {"thread_id": instance.thread_id}},
            )
        else:
            print(f"No agent found with name {instance.agent_name}")


class Approval(models.Model):
    """A huaman approval of a checkpoint with a yes/no"""

    thread_id = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], max_length=10
    )

    agent_name = models.CharField(max_length=255, blank=True, null=True)
    snapshot_config = models.JSONField()

    response = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=Approval)
def continue_agent(sender, instance, created, **kwargs):
    if created:
        print("Approval created")
        return

    if instance.state == "approved":
        print("Approval approved with response:", instance.response)

        agent_instance = get_agent(instance.agent_name)

        if agent_instance:
            output, snapshot = agent_instance.run(
                inputs=Command(resume=instance.response), config=instance.snapshot_config
            )
        else:
            print("No agent found")
    else:
        print("Approval not handled")


class Result(models.Model):
    """The result of an agent run"""

    thread_id = models.CharField(max_length=255, blank=True, null=True)
    agent_name = models.CharField(max_length=255)
    snapshot_config = models.JSONField()
    output = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Result)
def handle_result(sender, instance, created, **kwargs):
    if created:
        print("Result created")
        return

    print("Result updated")
    print(instance.output)
    print(instance.snapshot_config)
    print(instance.agent_name)
    print("----")
