from django.shortcuts import render

# Create your views here.
# myapp/views.py

from rest_framework import viewsets
from .models import *
from .serializers import *

class Greeting_ViewSet(viewsets.ModelViewSet):
    queryset = Association_greeting.objects.all()
    serializer_class = Greeting_Serializer
