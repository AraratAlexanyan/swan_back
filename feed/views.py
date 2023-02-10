
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from wall.serializers import *

from wall.serializers import PostListSerializer
from .services import post_feed


class FeedView(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PostListSerializer

    def list(self, request, *args, **kwargs):
        queryset = post_feed.get_post_list(request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = post_feed.get_single_post(kwargs.get('pk'))
        serializer = PostSerializer(instance)
        return Response(serializer.data)
    
