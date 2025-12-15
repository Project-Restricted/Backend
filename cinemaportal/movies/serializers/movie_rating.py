from rest_framework import serializers


class MovieRatingSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=1, max_value=10)
