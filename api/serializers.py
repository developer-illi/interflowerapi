# myapp/serializers.py

from rest_framework import serializers
from .models import *

class Greeting_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Association_greeting
        fields = '__all__'

class HistoryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = History_event
        fields = '__all__'
class HistoryContentSerializer(serializers.ModelSerializer):
    event = HistoryEventSerializer(source='history_event_set', many=True, read_only=True)
    class Meta:
        model = History_content
        fields = '__all__'

class HistorySetUpSerializer(serializers.ModelSerializer):
    contents = HistoryContentSerializer(source='history_content_set', many=True, read_only=True)

    class Meta:
        model = History_set_up
        fields = '__all__'