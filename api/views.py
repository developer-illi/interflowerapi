import json

from django.shortcuts import render

# Create your views here.
# myapp/views.py

from rest_framework import viewsets
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Organizational_chart
from .serializers import OrChartSetSerializer
import json


class Greeting_ViewSet(viewsets.ModelViewSet):
    queryset = Association_greeting.objects.all()
    serializer_class = Greeting_Serializer


@api_view(['GET'])
def History_DataSet(request):
    histories = History_set_up.objects.all()
    serializer = HistorySetUpSerializer(histories, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_history(request):
    serializers = History_DataSet(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

#국내전시
@api_view(['GET'])
def Local_DataSet(request):
    local = Local.objects.all()
    serializers = Local_ContentSetSerializer(local, many=True)
    return Response(serializers.data)

#대외사업
@api_view(['GET'])
def Overseas_DataSet(request):
    overseas = Overseas.objects.all()
    serializers = OverseasContentSerializer(overseas, many=True)
    return Response(serializers.data)

#자격증
@api_view(['GET'])
def License_DataSet(request):
    license = License.objects.all()
    serializers = LicenseContentSetSerializer(license, many=True)
    return Response(serializers.data)

#주요사업?
@api_view(['GET'])
def Contents_DataSet(request):
    content = Contests.objects.all()
    serializers = ContestsContentSerializer(content, many=True)
    return Response(serializers.data)

#협회소식
@api_view(['GET'])
def News_DataSet(request):
    content = News.objects.all()
    serializers = NewsContentSetSerializer(content, many=True)
    return Response(serializers.data)

#공지사항
@api_view(['GET'])
def Notice_DataSet(request):
    content = Notice.objects.all()
    serializers = NoticeSetSerializer(content, many=True)
    return Response(serializers.data)


#조직도
@api_view(['GET'])
def Organizational_DataSet(request):
    organizational = Organizational_chart.objects.all()
    serializer = OrChartSetSerializer(organizational, many=True)
    return Response(serializer.data)



@api_view(['POST'])
def create_organizational_chart(request):
    # request.data를 바로 사용
    serializer = or_chart_serializer(data=request.data)
    try:
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

