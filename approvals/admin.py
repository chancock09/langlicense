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
        return Approval.objects.filter(thread_id=obj.thread_id)

    def related_results(self, obj):
        return Result.objects.filter(thread_id=obj.thread_id)

    def related_approvals_links(self, obj):
        approvals = self.related_approvals(obj)
        links = [
            format_html(
                '<a href="{}">{}</a>', reverse("admin:approvals_approval_change", args=[approval.id]), approval.id
            )
            for approval in approvals
        ]
        return format_html(", ".join(links))

    def related_results_links(self, obj):
        results = self.related_results(obj)
        links = [
            format_html('<a href="{}">{}</a>', reverse("admin:approvals_result_change", args=[result.id]), result.id)
            for result in results
        ]
        return format_html(", ".join(links))

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
    )

    readonly_fields = (
        "agent_name",
        "render_prompt",
        "render_history",
        "snapshot_config",
        "related_triggers_links",
        "related_results_links",
    )

    def render_prompt(self, obj):
        agent = get_agent(obj.agent_name)
        return agent.get_state_history(obj.snapshot_config)[0].tasks[0].interrupts[0].value

    def render_history(self, obj):
        agent = get_agent(obj.agent_name)
        return agent.pretty_print_history(obj.snapshot_config)

    render_history.short_description = "SnapshotHistory"

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        for inline in inline_instances:
            inline.parent_instance = obj
        return inline_instances

    def related_triggers(self, obj):
        return Trigger.objects.filter(thread_id=obj.thread_id)

    def related_results(self, obj):
        return Result.objects.filter(thread_id=obj.thread_id)

    def related_triggers_links(self, obj):
        triggers = self.related_triggers(obj)
        links = [
            format_html('<a href="{}">{}</a>', reverse("admin:approvals_trigger_change", args=[trigger.id]), trigger.id)
            for trigger in triggers
        ]
        return format_html(", ".join(links))

    def related_results_links(self, obj):
        results = self.related_results(obj)
        links = [
            format_html('<a href="{}">{}</a>', reverse("admin:approvals_result_change", args=[result.id]), result.id)
            for result in results
        ]
        return format_html(", ".join(links))

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
        return Trigger.objects.filter(thread_id=obj.thread_id)

    def related_approvals(self, obj):
        return Approval.objects.filter(thread_id=obj.thread_id)

    def related_triggers_links(self, obj):
        triggers = self.related_triggers(obj)
        links = [
            format_html('<a href="{}">{}</a>', reverse("admin:approvals_trigger_change", args=[trigger.id]), trigger.id)
            for trigger in triggers
        ]
        return format_html(", ".join(links))

    def related_approvals_links(self, obj):
        approvals = self.related_approvals(obj)
        links = [
            format_html(
                '<a href="{}">{}</a>', reverse("admin:approvals_approval_change", args=[approval.id]), approval.id
            )
            for approval in approvals
        ]
        return format_html(", ".join(links))

    related_triggers_links.short_description = "Related Triggers"
    related_approvals_links.short_description = "Related Approvals"
