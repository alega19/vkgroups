from django.db import models
from django.db.models.expressions import RawSQL, Func, F, Value, Q
from django.contrib.postgres.fields import JSONField


class Separator(Func):
    template = '(%(expressions)s)'

    def __init__(self, separator, *expressions, **extra):
        self.arg_joiner = ' {0} '.format(separator)
        super().__init__(*expressions, **extra)


class ExtraQuerySet(models.QuerySet):

    def sort_by(self, field_name, inverse=False):
        if inverse:
            inverse_prefix = '-'
        else:
            inverse_prefix = ''
        return self.order_by(
            inverse_prefix + field_name
        )

    def exclude_nulls(self, *field_names):
        return self.filter(**{
            field_name + '__isnull': False
            for field_name in field_names
        })

    def filter_ignoring_nonetype(self, **kwargs):
        params = {
            field_name: value
            for field_name, value in kwargs.items()
            if value is not None
        }
        return self.filter(**params)


class AvailableCommunityManager(models.Manager.from_queryset(ExtraQuerySet)):

    def get_queryset(self):
        return super().get_queryset().exclude(deactivated=True).exclude(ctype=Community.TYPE_PRIVATE_GROUP)


class Community(models.Model):

    TYPE_PUBLIC_PAGE = 0
    TYPE_OPEN_GROUP = 1
    TYPE_CLOSED_GROUP = 2
    TYPE_PRIVATE_GROUP = 3
    TYPE_CHOICES = (
        (TYPE_PUBLIC_PAGE, "Public page"),
        (TYPE_OPEN_GROUP, "Open group"),
        (TYPE_CLOSED_GROUP, "Closed group"),
        (TYPE_PRIVATE_GROUP, "Private group")
    )

    AGELIMIT_UNKNOWN = -1
    AGELIMIT_NONE = 0
    AGELIMIT_16 = 16
    AGELIMIT_18 = 18
    AGELIMIT_CHOICES = (
        (AGELIMIT_UNKNOWN, 'Unknown'),
        (AGELIMIT_NONE, 'None'),
        (AGELIMIT_16, '16+'),
        (AGELIMIT_18, '18+')
    )

    vkid = models.PositiveIntegerField(primary_key=True)
    deactivated = models.BooleanField()
    ctype = models.SmallIntegerField(db_column='type', choices=TYPE_CHOICES)
    verified = models.NullBooleanField()
    age_limit = models.SmallIntegerField(choices=AGELIMIT_CHOICES, default=AGELIMIT_UNKNOWN)
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

    objects = models.Manager()
    available = AvailableCommunityManager()

    def vk_url(self):
        if self.ctype == self.TYPE_PUBLIC_PAGE:
            prefix = 'public'
        else:
            prefix = 'club'
        return r'https://vk.com/{0}{1:d}'.format(prefix, self.vkid)


class CommunityHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    community = models.ForeignKey('Community', on_delete=models.CASCADE)
    checked_at = models.DateTimeField()
    followers = models.PositiveIntegerField()


class PostQuerySet(ExtraQuerySet):
    
    # This expression has an index.
    # Since PostgreSQL requires the expressions in index and query to match it is necessary to use raw SQL.
    # Even the different ordering of arguments in an AND-expression makes the index useless.
    POST_LIKES_PER_VIEW_EXPRESSION = (
        'CASE WHEN ("communities_post"."views" IS NOT NULL AND "communities_post"."views" <> 0) '
        'THEN ("communities_post"."likes"::double precision / "communities_post"."views"::double precision) END'
    )

    def with_likes_per_view(self):
        return self.annotate(
            post_likes_per_view=RawSQL(self.POST_LIKES_PER_VIEW_EXPRESSION, (), output_field=models.FloatField())
        )

    def search(self, query):
        if not query:
            return self

        tsquery = Func(Value('russian'), Value(query), function='plainto_tsquery')
        return self.annotate(
            query_size_annotation=Func(
                tsquery,
                function='numnode',
                output_field=models.IntegerField()
            ),
            found_annotation=Separator(
                '@@',
                Func(Value('russian'), F('content'), function='post_content_to_tsvector'),
                tsquery,
                output_field=models.BooleanField()
            )
        ).filter(Q(query_size_annotation=0) | Q(found_annotation=True))


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
    links = models.PositiveSmallIntegerField()

    objects = PostQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.id = self.community_id * 2147483648 + self.vkid
        super().save(*args, **kwargs)

    def vk_url(self):
        return r'https://vk.com/wall-{0:d}_{1:d}'.format(self.community_id, self.vkid)


# for old migrations
class PostManager(models.Manager.from_queryset(PostQuerySet)):
    POST_LIKES_PER_VIEW_EXPRESSION = (
        'CASE WHEN ("communities_post"."views" IS NOT NULL AND "communities_post"."views" <> 0) '
        'THEN ("communities_post"."likes"::double precision / "communities_post"."views"::double precision) END'
    )
