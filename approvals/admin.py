from dotenv import load_dotenv
from pprint import pformat

# Load environment variables from .env file
load_dotenv()

from django.contrib import admin
from .models import Approval, Trigger

from approvals.agent import get_agent


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ("state", "response", "user", "created_at", "updated_at", "render_history")
    list_filter = ("state", "created_at", "updated_at")
    search_fields = ("user__username", "comment")
    readonly_fields = ("render_history",)

    def render_history(self, obj):
        agent = get_agent(obj.agent_name)

        history = agent.render_history(obj.snapshot_config)

        return pformat([entry for entry in history])

    render_history.short_description = "SnapshotHistory"


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = ("agent_name", "config", "input")
    search_fields = ("agent_name", "config")
