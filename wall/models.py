from django.conf import settings
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from wall.abstract_comment import AbstractComment


class Post(models.Model):

    text = models.TextField(max_length=1024)
    created_date = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    post_image = models.ImageField(blank=True, null=True, upload_to='post_images')

    def __str__(self):
        return self.text[:15]+'...'

    def comments_count(self):
        return self.comments.count()


class Comment(AbstractComment, MPTTModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', related_name='comments', on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child')

    def __str__(self):
        return f'{self.user}, {self.post}'
