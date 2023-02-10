from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from . import models
from .helpers.permissions import IsAuthor
from .helpers.viewsets import CreateRetrieveUpdateDestroyView, CreateUpdateDestroy
from .models import Post, Comment
from .serializers import PostSerializer, MakeCommentSerializer, PostListSerializer


class PostListView(generics.ListAPIView):
    permission_classes = permissions.IsAuthenticated
    serializer_class = PostListSerializer

    def get_queryset(self):
        return models.Post.objects.filter(published=True,
                                          user_id=self.kwargs.get('pk')).select_related('author').prefetch_related(
            'comments')


class PostRetrieveView(CreateRetrieveUpdateDestroyView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Post.objects.filter(published=True).select_related('author').prefetch_related('comments')
    serializer_class = PostSerializer
    permission_classes_by_action = {
        'get': [permissions.AllowAny],
        'update': [IsAuthor],
        'destroy': [IsAuthor]
    }

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostAuthorView(APIView):

    """
        If post doesn't publish , Only author can have access.
        
    """

    permission_classes = (IsAuthor,)

    def get(self, request, pk):
        data = Post.objects.get(pk)
        serializer = PostSerializer(data)
        return Response(serializer.data)


    def patch(self, request, pk):

        try:
            post = Post.objects.get(pk)
        except Post.DoesNotExist:
            return Response('Invalid post id')

        serializer = PostSerializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserDraftPosts(APIView):
    permission_classes = [IsAuthor]

    def get(self, request):
        queryset = Post.objects.filter(author_id=request.user.id).filter(published=False).select_related('author').\
            prefetch_related('comments')
        serializer = PostListSerializer(queryset, many=True)

        return Response(serializer.data)


class CommentView(CreateUpdateDestroy):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.all()
    serializer_class = MakeCommentSerializer
    permission_classes_by_action = {
        'update': [IsAuthor],
        'destroy': [IsAuthor]
    }

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()
        instance.save()
