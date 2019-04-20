from rest_framework import serializers

from home.models import LinkGameRanking


class LinkGameRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkGameRanking
        fields = ('username', 'type', 'record', 'date')

