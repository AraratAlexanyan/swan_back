from .helpers.serializers import *
from .models import Comment, Post


class MakeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('post', 'comment_text', 'parent')


class ListCommentSerializer(serializers.ModelSerializer):
    """
        Get all comments, with children, (Comment`s comment)
    """
    comment_text = serializers.SerializerMethodField()
    child = RecursiveSerializer(many=True)
    user = serializers.ReadOnlyField(source='user.username')

    def get_text(self, obj):
        if obj.deleted:
            return None
        return obj.comment_text

    class Meta:
        list_serializer_class = FilterCommentSerializer
        model = Comment
        fields = ('id', 'post', 'user', 'comment_text', 'created_date', 'child',)


class PostSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.username')
    comments = ListCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class PostListSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = ('id', 'created_date', 'author', 'text', 'post_image')
