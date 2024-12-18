# Generated by Django 5.1.4 on 2024-12-18 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approvals', '0010_remove_result_updated_at_remove_trigger_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trigger',
            name='config',
        ),
        migrations.AddField(
            model_name='approval',
            name='thread_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='result',
            name='thread_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='trigger',
            name='thread_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
