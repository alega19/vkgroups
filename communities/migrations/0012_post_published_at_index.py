# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-06-21 10:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('communities', '0011_merge_20180612_0130'),
    ]

    operations = [
        migrations.RunSQL(
            'CREATE INDEX CONCURRENTLY communities_post_published_at_index ON communities_post (published_at)',
            'DROP INDEX communities_post_published_at_index'
        )
    ]
