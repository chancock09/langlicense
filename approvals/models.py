from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


class HumanApproval(models.Model):
    state = models.CharField(
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], max_length=10
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checkpoint = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField()

class HumanResponse(models.model):
    state = models.CharField(
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], max_length=10
    response = JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checkpoint = models.ForeignKey(HumanApproval, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField()
