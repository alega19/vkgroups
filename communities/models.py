from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField


class Community(models.Model):

    TYPE_PUBLIC_PAGE = 0
    TYPE_OPEN_GROUP = 1
    TYPE_CLOSED_GROUP = 2
    TYPE_PRIVATE_GROUP = 3
    _TYPE_CHOICES = (
        (TYPE_PUBLIC_PAGE, "Public page"),
        (TYPE_OPEN_GROUP, "Open group"),
        (TYPE_CLOSED_GROUP, "Closed group"),
        (TYPE_PRIVATE_GROUP, "Private group")
    )

    AGELIMIT_UNKNOWN = -1
    AGELIMIT_NONE = 0
    AGELIMIT_16 = 16
    AGELIMIT_18 = 18
    _AGELIMIT_CHOICES = (
        (AGELIMIT_UNKNOWN, 'Unknown'),
        (AGELIMIT_NONE, 'None'),
        (AGELIMIT_16, '16+'),
        (AGELIMIT_18, '18+')
    )

    vkid = models.PositiveIntegerField(primary_key=True)
    deactivated = models.BooleanField()
    ctype = models.SmallIntegerField(db_column='type', choices=_TYPE_CHOICES)
    verified = models.NullBooleanField()
    age_limit = models.SmallIntegerField(choices=_AGELIMIT_CHOICES, default=AGELIMIT_UNKNOWN)
    name = models.TextField(blank=True)
    description = models.TextField(blank=True)
    followers = models.PositiveIntegerField(blank=True, null=True)
    status = models.TextField(blank=True)
    icon50url = models.TextField(blank=True)
    icon100url = models.TextField(blank=True)
    checked_at = models.DateTimeField(blank=True, null=True)
    wall_checked_at = models.DateTimeField(blank=True, null=True)
    posts_per_week = models.PositiveSmallIntegerField(blank=True, null=True)
    views_per_post = models.FloatField(blank=True, null=True)
    likes_per_view = models.FloatField(blank=True, null=True)
    growth_per_day = models.IntegerField(blank=True, null=True)
    growth_per_week = models.IntegerField(blank=True, null=True)


class CommunityHistory(models.Model):
    community = models.ForeignKey('Community', on_delete=models.CASCADE)
    changed_at = models.DateTimeField(default=timezone.now)
    followers = models.PositiveIntegerField()


class Post(models.Model):
    id = models.BigIntegerField(primary_key=True)
    community = models.ForeignKey('Community', on_delete=models.CASCADE)
    vkid = models.PositiveIntegerField()
    checked_at = models.DateTimeField()
    published_at = models.DateTimeField()
    content = JSONField()
    views = models.PositiveIntegerField(blank=True, null=True)
    likes = models.PositiveIntegerField()
    shares = models.PositiveIntegerField()
    comments = models.PositiveIntegerField()
    marked_as_ads = models.BooleanField()
    links = models.PositiveSmallIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.id = self.community_id * 2147483648 + self.vkid
        super().save(*args, **kwargs)
