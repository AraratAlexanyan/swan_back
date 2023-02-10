from django.db import models


class AbstractComment(models.Model):

    comment_text = models.TextField('Message', max_length=256)
    commented_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment_text[:10]

    class Meta:
        abstract = True
