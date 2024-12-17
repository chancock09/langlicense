from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from approvals.agent import get_agent
from langgraph.types import Command

# Create your models here.

User = get_user_model()


class Approval(models.Model):
    """A huaman approval of a checkpoint with a yes/no"""

    state = models.CharField(
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], max_length=10
    )

    agent_name = models.CharField(max_length=255, blank=True, null=True)
    snapshot_config = models.JSONField()
    response = models.JSONField()

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=Approval)
def continue_agent(sender, instance, **kwargs):
    if instance.state == "approved":

        agent_instance = get_agent(instance.agent_name)

        if agent_instance:
            result = agent_instance.run(inputs=Command(resume=instance.response), config=instance.snapshot_config)
            print(result["messages"][-1].content)
        else:
            print("No agent found")
    else:
        print("Approval not approved")


class Trigger(models.Model):
    """Webhooks that kick off an agent workflow"""

    agent_name = models.CharField(max_length=255)
    config = models.JSONField()
    input = models.JSONField()


@receiver(post_save, sender=Trigger)
def handle_trigger(sender, instance, created, **kwargs):
    if created:
        agent = get_agent(instance.agent_name)
        if agent:
            result, snapshot = agent.run(inputs=instance.input, config=instance.config)
            print(result)
        else:
            print(f"No agent found with name {instance.agent_name}")
