# myapp/serializers.py

from rest_framework import serializers
from .models import *

class Greeting_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Association_greeting
        fields = '__all__'
