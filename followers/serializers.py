from rest_framework import serializers

from account.serializers import UserFollowSerializer
from . import models


class ListFollowersSerializer(serializers.ModelSerializer):

    subscriber = serializers.ReadOnlyField()

    class Meta:
        model = models.Followers
        fields = ('subscriber',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        subscriber = data.pop('subscriber')
        data['subscriber'] = UserFollowSerializer(subscriber).data

        return data
