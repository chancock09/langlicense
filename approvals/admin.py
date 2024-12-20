from dotenv import load_dotenv
from pprint import pformat

# Load environment variables from .env file
load_dotenv()

from django.contrib import admin
from django import forms
from .models import Approval, Trigger, Result

from approvals.agent import get_agent, agent_registry
from django.utils.html import format_html
from django.urls import reverse


def get_related_objects_links(obj, related_objects, admin_url_name):
    links = [
        format_html('<a href="{}">{}</a>', reverse(admin_url_name, args=[related_obj.id]), related_obj.id)
        for related_obj in related_objects
    ]
    return format_html(", ".join(links))


def get_related_objects(model, thread_id):
    return model.objects.filter(thread_id=thread_id)


class TriggerForm(forms.ModelForm):
    class Meta:
        model = Trigger
        fields = "__all__"

    agent_name = forms.ChoiceField(choices=[(key, key) for key in agent_registry.keys()])


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    form = TriggerForm
    list_display = (
        "agent_name",
        "thread_id",
        "input",
        "created_at",
    )
    search_fields = ("agent_name", "config")

    readonly_fields = ("related_approvals_links", "related_results_links")

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        for inline in inline_instances:
            inline.parent_instance = obj
        return inline_instances

    def related_approvals(self, obj):
        return get_related_objects(Approval, obj.thread_id)

    def related_results(self, obj):
        return get_related_objects(Result, obj.thread_id)

    def related_approvals_links(self, obj):
        approvals = self.related_approvals(obj)
        return get_related_objects_links(obj, approvals, "admin:approvals_approval_change")

    def related_results_links(self, obj):
        results = self.related_results(obj)
        return get_related_objects_links(obj, results, "admin:approvals_result_change")

    related_approvals_links.short_description = "Related Approvals"
    related_results_links.short_description = "Related Results"


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "agent_name",
        "thread_id",
        "response",
        "created_at",
        "updated_at",
    )
    list_filter = ("state", "created_at", "updated_at")

    fields = (
        "agent_name",
        "response",
        "render_prompt",
        "render_history",
        "snapshot_config",
        "related_triggers_links",
        "related_results_links",
        "render_state",
    )

    readonly_fields = (
        "agent_name",
        "render_prompt",
        "render_history",
        "snapshot_config",
        "related_triggers_links",
        "related_results_links",
        "render_state",
    )

    def render_prompt(self, obj):
        agent = get_agent(obj.agent_name)

        try:
            return agent.get_state_history(obj.snapshot_config)[0].tasks[0].interrupts[0].value
        except Exception as e:
            return "No interrupt found"

    def render_history(self, obj):
        agent = get_agent(obj.agent_name)
        return agent.pretty_print_history(obj.snapshot_config)

    render_history.short_description = "Messages History"

    def render_state(self, obj):
        agent = get_agent(obj.agent_name)
        return agent.get_state_history(obj.snapshot_config)

    render_state.short_description = "State Snapshot"

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        for inline in inline_instances:
            inline.parent_instance = obj
        return inline_instances

    def related_triggers(self, obj):
        return get_related_objects(Trigger, obj.thread_id)

    def related_results(self, obj):
        return get_related_objects(Result, obj.thread_id)

    def related_triggers_links(self, obj):
        triggers = self.related_triggers(obj)
        return get_related_objects_links(obj, triggers, "admin:approvals_trigger_change")

    def related_results_links(self, obj):
        results = self.related_results(obj)
        return get_related_objects_links(obj, results, "admin:approvals_result_change")

    related_triggers_links.short_description = "Related Triggers"
    related_results_links.short_description = "Related Results"


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "agent_name",
        "thread_id",
        "output",
        "created_at",
    )
    list_filter = ("created_at",)

    fields = (
        "agent_name",
        "output",
        "render_history",
        "snapshot_config",
        "related_triggers_links",
        "related_approvals_links",
    )

    readonly_fields = (
        "agent_name",
        "output",
        "render_history",
        "snapshot_config",
        "related_triggers_links",
        "related_approvals_links",
    )

    def render_history(self, obj):
        agent = get_agent(obj.agent_name)
        return agent.pretty_print_history(obj.snapshot_config)

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        for inline in inline_instances:
            inline.parent_instance = obj
        return inline_instances

    def related_triggers(self, obj):
        return get_related_objects(Trigger, obj.thread_id)

    def related_approvals(self, obj):
        return get_related_objects(Approval, obj.thread_id)

    def related_triggers_links(self, obj):
        triggers = self.related_triggers(obj)
        return get_related_objects_links(obj, triggers, "admin:approvals_trigger_change")

    def related_approvals_links(self, obj):
        approvals = self.related_approvals(obj)
        return get_related_objects_links(obj, approvals, "admin:approvals_approval_change")

    related_triggers_links.short_description = "Related Triggers"
    related_approvals_links.short_description = "Related Approvals"
