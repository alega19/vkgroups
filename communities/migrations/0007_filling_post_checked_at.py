# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-19 10:40
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import Min, F


def fill_checked_at(apps, schema_editor):
    WallCheckingLog = apps.get_model('communities', 'WallCheckingLog')
    Post = apps.get_model('communities', 'Post')
    comm_ids = Post.objects.distinct(
        'community_id'
    ).filter(
        checked_at__isnull=True
    ).values_list('community_id', flat=True)
    for comm_id in comm_ids:
        checks_qs = WallCheckingLog.objects.filter(community_id=comm_id)

        min_check_time = Post.objects.filter(community_id=comm_id).aggregate(Min('checked_at'))['checked_at__min']
        if min_check_time is not None:
            checks_qs = checks_qs.filter(checked_at__lt=min_check_time)
        start, batch_size = 0, 1000
        while True:
            checks = checks_qs.order_by('-checked_at')[start:start+batch_size]
            if not checks:
                break
            for check in checks:
                if check.oldest_post_date is None:
                    break
                Post.objects.filter(
                    community_id=comm_id,
                    checked_at__isnull=True,
                    published_at__gte=check.oldest_post_date
                ).update(
                    checked_at=check.checked_at
                )
            Post.objects.filter(
                community_id=comm_id,
                checked_at__isnull=True
            ).update(
                checked_at=F('published_at')
            )
            if check.oldest_post_date is None:
                break
            start += batch_size


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('communities', '0006_post_checked_at'),
    ]

    operations = [
        migrations.RunPython(fill_checked_at, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='post',
            name='checked_at',
            field=models.DateTimeField(),
        )
    ]
