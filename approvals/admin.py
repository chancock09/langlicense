from dotenv import load_dotenv
from pprint import pformat

# Load environment variables from .env file
load_dotenv()

from django.contrib import admin
from .models import Approval, AgentWebhook

from approvals.agent.weather_agent import WeatherAgent

agent = WeatherAgent()


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ("state", "response", "user", "created_at", "updated_at", "render_snapshot")
    list_filter = ("state", "created_at", "updated_at")
    search_fields = ("user__username", "comment")
    readonly_fields = ("render_snapshot",)

    def render_snapshot(self, obj):
        snapshot = agent.render_snapshot(obj.snapshot)
        return "<br>".join(pformat(state) for state in snapshot)

    render_snapshot.short_description = "Snapshot History"


@admin.register(AgentWebhook)
class AgentWebhookAdmin(admin.ModelAdmin):
    list_display = ("agent", "thread_id", "message")
    search_fields = ("agent", "thread_id")
