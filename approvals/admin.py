from dotenv import load_dotenv
from pprint import pformat

# Load environment variables from .env file
load_dotenv()

from django.contrib import admin
from django import forms
from .models import Approval, Trigger

from approvals.agent import get_agent, agent_registry


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ("id", "agent_name", "state", "response", "user", "created_at", "updated_at")
    list_filter = ("state", "created_at", "updated_at")
    search_fields = ("user__username", "comment")
    readonly_fields = ("render_history",)

    def render_history(self, obj):
        agent = get_agent(obj.agent_name)

        history = agent.render_history(obj.snapshot_config)

        return pformat([entry for entry in history])

    render_history.short_description = "SnapshotHistory"


class TriggerForm(forms.ModelForm):
    class Meta:
        model = Trigger
        fields = "__all__"

    agent_name = forms.ChoiceField(choices=[(key, key) for key in agent_registry.keys()])


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    form = TriggerForm
    list_display = ("agent_name", "config", "input")
    search_fields = ("agent_name", "config")
