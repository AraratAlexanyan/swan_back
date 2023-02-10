from django.conf import settings

from wall.models import Post


class Feed:

    def get_posts(self, user: settings.AUTH_USER_MODEL):
        return Post.objects.filter(author__swan_user__subscriber=user).order_by('-created_date')\
            .select_related('author').prefetch_related('comments')

    def get_single_post(self, pk: int):
        return Post.objects.select_related('user').prefetch_related('comments').get(id=pk)


post_feed = Feed()
