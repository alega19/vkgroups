# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-18 09:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0003_added_field_checked_at_to_community'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='communityhistory',
            name='changed_at',
        ),
        migrations.AddField(
            model_name='communityhistory',
            name='checked_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='communityhistory',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
