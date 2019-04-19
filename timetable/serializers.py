from rest_framework import serializers

from timetable.models import CoursesHtml, Donate, ColorTheme


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursesHtml
        fields = ('school', 'type', 'url', 'html')


class PostSerializer2(serializers.ModelSerializer):
    class Meta:
        model = CoursesHtml
        fields = ('school', 'contact', 'type', 'url', 'html')


class DonateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donate
        fields = ('name', 'money')


class ColorThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorTheme
        fields = ('id', 'username', 'description', 'download', 'like', 'precolor')


class ColorThemePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorTheme
        fields = ('username', 'description', 'config')
