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
from django.contrib import admin

# api 라우터 세팅


urlpatterns = [
    path('admin/', admin.site.urls),
    path('greeing/', api_view.Greeting_DataSet, name='greeing'),
    # 리소스별로 구조 정리
    # 연혁

    path('history/', api_view.History_DataSet, name='history'),
    path('history_post/', api_view.create_history, name='create_history'),
    path('history_post/content/', api_view.create_his_content, name='create_his_content'),
    path('history_post/event/', api_view.create_his_event, name='create_his_event'),

    # 조직도
    path('organization/', api_view.organization_all_data, name='organizations'),
    path('organizational_post/', api_view.create_organizational_chart, name='organizational_post'),
    path('organizational_post/title/', api_view.create_organizational_title, name='create_organizational_title'),
    # path('organizational/<int:id>/', api_view.Organizational_Detail, name='organizational-detail'),

    # 국내전시
    path('exhibition/', api_view.Local_DataSet, name='local'),
    # path('local_post/', api_view.create_local, name='create_local'),
    path('local_post/content/', api_view.create_local_content, name='create_local_content'),

    # 자격증
    path('license/', api_view.License_DataSet, name='license'),
    path('license_post/', api_view.create_license, name='create_license'),
    path('license_post/content/', api_view.create_license_content, name='create_license_content'),

    # 주력사업
    path('activity/', api_view.Contents_DataSet, name='contents'),
    path('activity/<int:id>', api_view.Content_detail_data, name='contents_detail'),
    # path('contents_post/', api_view.create_content, name='create_content'),
    # path('contents_post/content/', api_view.create_content_content, name='create_content_content'),

    # 협회소식
    path('news/', api_view.News_DataSet, name='news'),
    path('news/<int:id>', api_view.News_data_id, name='news_id'),
    path('news_post/', api_view.create_news, name='create_news'),
    path('news_post/content/', api_view.create_news_content, name='create_news_content'),

    # 공지사항
    path('notice/', api_view.Notice_DataSet, name='notice'),
    path('notice/<int:id>', api_view.Notice_detail, name='notice'),
    path('notice_post/', api_view.create_notice, name='create_notice'),
    path('notice_post/content/', api_view.create_notice_content, name='create_notice_content'),
]
