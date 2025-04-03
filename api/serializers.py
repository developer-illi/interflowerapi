# myapp/serializers.py

from rest_framework import serializers
from .models import *

class Greeting_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Association_greeting
        fields = '__all__'


class History_year_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Association_history_year
        fields = '__all__'

class History_month_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Association_history_month
        fields = '__all__'