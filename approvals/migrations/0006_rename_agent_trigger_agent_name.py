# Generated by Django 5.1.4 on 2024-12-17 23:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('approvals', '0005_trigger_delete_agentwebhook'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trigger',
            old_name='agent',
            new_name='agent_name',
        ),
    ]
