# Generated by Django 5.1.4 on 2024-12-18 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approvals', '0007_result_trigger_created_at_trigger_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='approval',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='approval',
            name='user',
        ),
        migrations.AlterField(
            model_name='approval',
            name='response',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='result',
            name='output',
            field=models.TextField(),
        ),
    ]