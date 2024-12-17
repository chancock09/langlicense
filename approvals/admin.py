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
    list_display = ("state", "response", "user", "created_at", "updated_at", "render_history")
    list_filter = ("state", "created_at", "updated_at")
    search_fields = ("user__username", "comment")
    readonly_fields = ("render_history",)

    def render_history(self, obj):
        history = agent.render_history(obj.snapshot)

        result = []
        for state in history:
            result.append(state)
            result("\n--")

        return result

    render_history.short_description = "SnapshotHistory"


@admin.register(AgentWebhook)
class AgentWebhookAdmin(admin.ModelAdmin):
    list_display = ("agent", "thread_id", "message")
    search_fields = ("agent", "thread_id")
