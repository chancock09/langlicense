# Generated by Django 5.1.4 on 2024-12-18 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approvals', '0008_remove_approval_comment_remove_approval_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trigger',
            name='input',
            field=models.TextField(),
        ),
    ]
