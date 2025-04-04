from django.shortcuts import render

# Create your views here.
# myapp/views.py

from rest_framework import viewsets
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view


class Greeting_ViewSet(viewsets.ModelViewSet):
    queryset = Association_greeting.objects.all()
    serializer_class = Greeting_Serializer
    print(serializer_class)


@api_view(['GET'])
def his_join(request):
    histories = History_set_up.objects.all()
    serializer = HistorySetUpSerializer(histories, many=True)
    return Response(serializer.data)
