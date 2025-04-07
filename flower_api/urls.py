"""
URL configuration for flower_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views as api_view

#api 라우터 세팅

router = DefaultRouter()
router.register(r'Greeting', api_view.Greeting_ViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('history', api_view.History_DataSet, name='history'),
    path('organizational', api_view.Organizational_DataSet, name='organizational'),
    path('local', api_view.Local_DataSet, name='organizational'),
    path('overseas', api_view.Organizational_DataSet, name='overseas'),
    path('license', api_view.Local_DataSet, name='license'),
    path('contents', api_view.Contents_DataSet, name='content'),
    path('news', api_view.News_DataSet, name='news'),
    path('notice', api_view.Notice_DataSet, name='notice'),
    path('organizational', api_view.Organizational_DataSet, name='organizational'),
]
