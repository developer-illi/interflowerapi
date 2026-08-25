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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView,
)

# api 라우터 세팅


urlpatterns = [
    path('admin/', admin.site.urls),
    path('greeting/', api_view.Greeting_DataSet, name='greeting'),
    # 리소스별로 구조 정리
    # 연혁

    path('history', api_view.History_DataSet, name='history'),
    path('history_post/', api_view.create_history, name='create_history'),
    path('history_post/content/', api_view.create_his_content, name='create_his_content'),
    path('history_post/event', api_view.create_his_event, name='create_his_event'),
    path('history_add', api_view.history_add, name='History_add'),
    path('history_event_add/<int:id>', api_view.history_event_add, name='history_event_add'),
    path('history_update/<int:id>', api_view.arter_his_event, name='history_update'),
    path('history_delete/<int:id>', api_view.del_his_event, name='history_delete'),

    # 조직도
    path('organization', api_view.organization_all_data, name='organizations'),
    path('organization_add', api_view.organizational_add, name='organizations'),
    path('organizational_post/', api_view.create_organizational_chart, name='organizational_post'),
    path('organizational_post/title/', api_view.create_organizational_title, name='create_organizational_title'),
    # path('organizational/<int:id>/', api_view.Organizational_Detail, name='organizational-detail'),

    # 국내,국외전시
    path('exhibition', api_view.Local_DataSet, name='local'),
    path('domesticAdd', api_view.domesticAdd, name='domesticAdd'),
    path('domesticContentAdd/<int:id>', api_view.domesticContnentAdd, name='domesticAdd'),
    path('overseasAdd', api_view.overseasAdd, name='domesticAdd'),
    path('internationalContentAdd/<int:id>', api_view.overseasContnentAdd, name='domesticAdd'),
    # path('local_post/', api_view.create_local, name='create_local'),
    path('local_post/content/', api_view.create_local_content, name='create_local_content'),
    path('domestic_update/<int:id>', api_view.domestic_update, name='domestic_update'),
    path('domestic_delete/<int:id>', api_view.domestic_delete, name='domestic_delete'),
    path('domestic_content_delete/<int:id>', api_view.domestic_content_delete, name='domestic_content_delete'),
    path('overseas_update/<int:id>', api_view.overseas_update, name='overseas_update'),
    path('overseas_delete/<int:id>', api_view.overseas_delete, name='overseas_delete'),
    path('overseas_content_delete/<int:id>', api_view.overseas_content_delete, name='overseas_content_delete'),

    # 자격증
    path('license', api_view.License_DataSet, name='license'),
    path('licenseAdd', api_view.licenseAdd, name='licenseAdd'),
    path('license_post/', api_view.create_license, name='create_license'),
    path('license_post/content/', api_view.create_license_content, name='create_license_content'),
    path('license_update/<int:id>', api_view.license_update, name='license_update'),
    path('license_delete/<int:id>', api_view.license_delete, name='license_delete'),

    # 주력사업
    path('activity', api_view.Contents_DataSet, name='contents'),
    path('activitiesAdd', api_view.activitiesAdd, name='activitiesAdd'),
    path('acticontentAdd/<int:id>', api_view.acticontentAdd, name='acticontentAdd'),
    path('activity/<int:id>', api_view.Content_detail_data, name='contents_detail'),
    path('activity_update/<int:id>', api_view.activity_update, name='activity_update'),
    path('activity_delete/<int:id>', api_view.activity_delete, name='activity_delete'),
    path('acticontent_update/<int:id>', api_view.acticontent_update, name='acticontent_update'),
    path('acticontent_delete/<int:id>', api_view.acticontent_delete, name='acticontent_delete'),
    # path('contents_post/', api_view.create_content, name='create_content'),
    # path('contents_post/content/', api_view.create_content_content, name='create_content_content'),

    # 협회소식
    path('news', api_view.News_DataSet, name='news'),
    path('news_add', api_view.news_add, name='news_add'),
    path('news/<int:id>', api_view.News_data_id, name='news_id'),
    path('news_post/', api_view.create_news, name='create_news'),
    path('news_update/<int:id>', api_view.news_update, name='news_update'),
    path('news_delete/<int:id>', api_view.del_news, name='news_delete'),
    path('news_post/content/', api_view.create_news_content, name='create_news_content'),

    # 공지사항
    path('notice', api_view.Notice_DataSet, name='notice'),
    path('notice_add', api_view.notice_add, name='notice_add'),
    path('notice/<int:id>', api_view.Notice_detail, name='notice_detail'),
    path('notice_update/<int:id>', api_view.notice_update, name='notice_update'),
    path('notice_delete/<int:id>', api_view.notice_delete, name='notice_delete'),
    path('notice_attachment_delete/<int:id>', api_view.notice_attachment_delete,
         name='notice_attachment_delete'),
    path('notice_post/', api_view.create_notice, name='create_notice'),
    path('notice_post/content/', api_view.create_notice_content, name='create_notice_content'),

    path('api/upload', api_view.upload_image, name='upload_image'),

    # 관리자 인증 (P2-4). ENFORCE_WRITE_AUTH=True 로 전환하기 전에는
    # 토큰이 없어도 쓰기가 허용되므로 배포만으로 기존 동작이 깨지지 않는다.
    path('auth/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify', TokenVerifyView.as_view(), name='token_verify'),
]

# 미처리 예외도 HTML 이 아닌 JSON 으로 응답
handler500 = 'api.exception_handlers.server_error'
handler404 = 'api.exception_handlers.not_found'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
