from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import Account
from followers.models import Followers
from followers.serializers import ListFollowersSerializer


class ListFollowersView(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ListFollowersSerializer

    def get_queryset(self):
        return Followers.objects.filter(user=self.request.user)


class ListSubscribersView(generics.ListAPIView):

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ListFollowersSerializer

    def get_queryset(self):
        return Followers.objects.filter(subscriber=self.request.user)


class FollowerView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):

        if request.user.id == pk:
            return

        try:
            user = Account.objects.get(id=pk)
        except Followers.DoesNotExist:
            return Response(status=404)
        Followers.objects.create(subscriber=request.user, user=user)
        return Response(status=201)

    def delete(self, request, pk):
        try:
            sub = Followers.objects.get(subscriber=request.user, user_id=pk)
        except Followers.DoesNotExist:
            return Response(status=404)
        sub.delete()
        return Response(status=204)
