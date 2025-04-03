from django.shortcuts import render

# Create your views here.
# myapp/views.py

from rest_framework import viewsets
from .models import *
from .serializers import *

class Greeting_ViewSet(viewsets.ModelViewSet):
    queryset = Association_greeting.objects.all()
    serializer_class = Greeting_Serializer

class history_year_Viewset(viewsets.ModelViewSet):
    queryset = Association_history_year.objects.all()
    serializer_class = History_year_Serializer

class History_month_Viewset(viewsets.ModelViewSet):
    queryset = Association_history_month.objects.all()
    serializer_class = History_month_Serializer

