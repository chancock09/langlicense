from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


class Continuation(models.Model):
    """A huaman approval of a checkpoint with a yes/no"""

    state = models.CharField(
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], max_length=10
    )
    response = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checkpoint = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField()


class AgentWebhook(models.Model):
    """Webhooks that kick off an agent workflow"""

    agent = models.CharField(max_length=255)
    thread_id = models.CharField(max_length=255)
    message = JSONField()
