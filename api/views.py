import datetime
import json

from django.shortcuts import render

# Create your views here.
# myapp/views.py

from rest_framework import viewsets
from .serializers import *
from django.http import HttpResponse
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Q
from django.conf import settings
from django.core.files.base import ContentFile
import os
import uuid
from django.utils import timezone
from django.core.files.storage import default_storage
from .models import Organizational_chart
from .serializers import OrChartSetSerializer
import json


class Greeting_ViewSet(viewsets.ModelViewSet):
    queryset = Association_greeting.objects.all()
    serializer_class = Greeting_Serializer

@api_view(['GET'])
def Greeting_DataSet(request):
    greeting = Association_greeting.objects.all()
    serializer = Greeting_Dataset(greeting, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def History_DataSet(request):
    histories = History_set_up.objects.all().order_by('-id')
    serializer = HistorySetUpSerializer(histories, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_history(request):
    # request.data를 바로 사용
    serializer = History_Set_Serializer(data=request.data)
    try:
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_his_content(request):
    serializers = History_content_Serializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def history_add(request):
    year = request.POST.get('year')
    modal = History_set_up.objects.create(dis_type='history', title=year)
    modal.save()

    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def history_event_add(request, id):
    try:
        # 1. 메인 연혁 객체 가져오기
        main_data = History_set_up.objects.get(id=id)

        # 2. 날짜 구성
        month = request.POST.get('month')
        date_str = f"{main_data.title}.{month}"

        # 3. 텍스트 내용
        content_text = request.POST.get('text')

        # 4. 이미지 처리 (이름 변경)
        image_file = request.FILES.get('image')
        if image_file:
            ext = os.path.splitext(image_file.name)[1]  # 확장자 유지
            new_filename = f"{uuid.uuid4().hex}{ext}"
            image_file.name = new_filename  # 이미지 이름 변경

        # 5. History_content 생성
        history_content = History_content.objects.create(
            date=date_str,
            history=main_data
        )

        # 6. History_event 생성
        History_event.objects.create(
            content=content_text,
            img=image_file,
            history_content=history_content
        )

        return Response(status=status.HTTP_201_CREATED)

    except History_set_up.DoesNotExist:
        return Response({"error": "해당 ID의 연혁이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_his_event(request):
    serializers = HistoryEventSerializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def arter_his_event(request, id):
    try:
        ori_content = History_event.objects.get(id=id)
    except History_event.DoesNotExist:
        raise NotFound(detail="해당 이벤트가 존재하지 않습니다.")

    content = request.data.get('content')
    image = request.FILES.get('image')  # ← 이미지 파일은 여기서 받아야 함

    if content:
        ori_content.content = content
    if image:
        ori_content.img = image  # History_event 모델에서 img 필드가 ImageField 여야 합니다.

    ori_content.save()

    serializer = HistoryEventSerializer(ori_content)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def del_his_event(request, id):
    try:
        ori_content = History_event.objects.get(id=id)
    except History_event.DoesNotExist:
        raise NotFound(detail="해당 이벤트가 존재하지 않습니다.")

    ori_content.delete()
    serializer = HistoryEventSerializer(ori_content)
    return Response(serializer.data, status=status.HTTP_200_OK)

#국내전시
@api_view(['GET'])
def Local_DataSet(request):
    get_data_type = request.GET.get('type')
    if get_data_type in ['domestic']:
        data_set = Local.objects.all()
        serializers = LocalSetSerializer(data_set, many=True)
    else:
        data_set = Overseas.objects.all()
        serializers = OverseasSetSerializer(data_set, many=True)
    return Response(serializers.data)

@api_view(['POST'])
def domesticAdd(request):
    main_data = request.POST.get('title')
    subTitle = request.POST.get('subTitle')
    content = request.POST.get('content')
    try:
        image_file = request.FILES.get('image')
        if image_file:
            ext = os.path.splitext(image_file.name)[1]  # 확장자 유지
            new_filename = f"{uuid.uuid4().hex}{ext}"
            image_file.name = new_filename  # 이미지 이름 변경
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    domestic = Local.objects.create(
        title=main_data,
        subTitle= subTitle,
        content=content,
        headerImage=image_file
    )
    domestic.save()
    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def domesticContnentAdd(request, id):
    domestic = Local.objects.get(id=id)
    title = request.POST.get('title')
    content = request.POST.get('content')
    try:
        image_file = request.FILES.get('image')
        if image_file:
            ext = os.path.splitext(image_file.name)[1]  # 확장자 유지
            new_filename = f"{uuid.uuid4().hex}{ext}"
            image_file.name = new_filename  # 이미지 이름 변경
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    content_add = Local_content.objects.create(
        title=title,
        date=datetime.datetime.now(),
        description=content,
        image= image_file,
        local=domestic
    )
    content_add.save()
    return Response(status=status.HTTP_201_CREATED)


@api_view(['POST'])
def overseasAdd(request):
    title = request.POST.get('title')
    subTitle = request.POST.get('subTitle')
    content = request.POST.get('content')
    try:
        image_file = request.FILES.get('image')
        if image_file:
            ext = os.path.splitext(image_file.name)[1]  # 확장자 유지
            new_filename = f"{uuid.uuid4().hex}{ext}"
            image_file.name = new_filename  # 이미지 이름 변경
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    domestic = Overseas.objects.create(
        title=title,
        sub_title= subTitle,
        content=content,
        headerImage=image_file
    )
    domestic.save()
    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def overseasContnentAdd(request, id):
    main_data = Overseas.objects.get(id=id)
    title = request.POST.get('title')
    content = request.POST.get('content')
    try:
        image_file = request.FILES.get('image')
        if image_file:
            ext = os.path.splitext(image_file.name)[1]  # 확장자 유지
            new_filename = f"{uuid.uuid4().hex}{ext}"
            image_file.name = new_filename  # 이미지 이름 변경
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    content_add = Overseas_content.objects.create(
        title=title,
        date=datetime.datetime.now(),
        description=content,
        image= image_file,
        overseas=main_data
    )
    content_add.save()
    return Response(status=status.HTTP_201_CREATED)

#국내 전시 컨탠츠 생성
@api_view(['POST'])
def create_local_content(request):
    serializers = Local_ContentSetSerializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

#주력사업
@api_view(['POST'])
def activitiesAdd(request):
    main_data = request.POST.get('title')
    content = request.POST.get('content')
    try:
        image_file = request.FILES.get('image')
        if image_file:
            ext = os.path.splitext(image_file.name)[1]  # 확장자 유지
            new_filename = f"{uuid.uuid4().hex}{ext}"
            image_file.name = new_filename  # 이미지 이름 변경
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    domestic = Contests.objects.create(
        title=main_data,
        content=content,
        headerImage=image_file
    )
    domestic.save()
    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def acticontentAdd(request, id):
    main_data = Contests.objects.get(id=id)
    title = request.POST.get('title')
    date = request.POST.get('date')
    location = request.POST.get('location')
    florists = request.POST.get('florists')
    content = request.POST.get('content')
    description = request.POST.get('description')
    try:
        image_file = request.FILES.get('image')
        if image_file:
            ext = os.path.splitext(image_file.name)[1]  # 확장자 유지
            new_filename = f"{uuid.uuid4().hex}{ext}"
            image_file.name = new_filename  # 이미지 이름 변경
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    acti_content = Contests_content.objects.create(
        mainImage=image_file,
        title=title,
        date=date,
        location=location,
        content=content,
        contests=main_data
    )
    acti_content.save()
    gallery_create = Contents_gallery.objects.create(
        id=acti_content.id,
        title=title,
        date=date,
        description=description,
        image=image_file,
        target_content=main_data
    )
    gallery_create.save()
    florists_create = Content_florist.objects.create(
        name=florists,
        target_content=acti_content
    )
    florists_create.save()
    return Response(status=status.HTTP_201_CREATED)

#대외사업 데이터 조회
@api_view(['GET'])
def Overseas_DataSet(request):
    overseas = Overseas.objects.all()
    serializers = OverseasContentSerializer(overseas, many=True)
    return Response(serializers.data)

#대외사업 메인 데이터셋 생성
@api_view(['POST'])
def create_overseas(request):
    serializers = Overseas_Set_Serializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

#대외사업 content 생성
@api_view(['POST'])
def create_overseas_content(request):
    serializers = OverseasContentSerializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.data, status=status.HTTP_400_BAD_REQUEST)

#자격증
@api_view(['GET'])
def License_DataSet(request):
    license = License.objects.all()
    serializers = LicenseSetSerializer(license, many=True)
    return Response(serializers.data)

@api_view(['POST'])
def licenseAdd(request):
    title = request.POST.get('title')
    content = request.POST.get('content')
    licenseInfo = request.POST.get('licenseInfo')
    link = request.POST.get('link')

    try:
        image_file = request.FILES.get('image')
        subImage = request.FILES.get('subImage')
        if image_file:
            ext = os.path.splitext(image_file.name)[1]  # 확장자 유지
            new_filename = f"{uuid.uuid4().hex}{ext}"
            image_file.name = new_filename  # 이미지 이름 변경
        if subImage:
            ext = os.path.splitext(subImage.name)[1]  # 확장자 유지
            new_filename = f"{uuid.uuid4().hex}{ext}"
            subImage.name = new_filename  # 이미지 이름 변경
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    license = License.objects.create(
        title=title,
        content=content,
        headerImage=image_file
    )
    license.save()
    license_content = License_content.objects.create(
        image=subImage,
        information=licenseInfo,
        hyperlink=link,
        license=license
    )
    license_content.save()
    return Response(status=status.HTTP_201_CREATED)

#자격증 메인 데이터셋 생성
@api_view(['POST'])
def create_license(request):
    serializers = License_Set_Serializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.data, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_license_content(request):
    serializers = LicenseContentSetSerializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.data, status=status.HTTP_400_BAD_REQUEST)

#주요사업?
@api_view(['GET'])
def Contents_DataSet(request):
    content = Contests.objects.all().order_by('id')
    serializers = ContestsSerializer(content, many=True)
    return Response(serializers.data)

@api_view(['GET'])
def Content_detail_data(request, id):
    print(id)
    detail_data = Contests_content.objects.get(id=id)
    serializers = ContestsContentSerializer(detail_data)
    return Response(serializers.data)


#주요사업 메인 데이터셋 생성
#주요사업 컨텐츠 생성
@api_view(['POST'])
def create_content_content(request):
    serializers = ContestsContentSerializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.data, status=status.HTTP_400_BAD_REQUEST)

#협회소식
@api_view(['GET'])
def News_DataSet(request):
    get_type = request.GET.get('type')
    if get_type in ['report', 'issues']:
        type_id = get_type
        content = News.objects.filter(type=type_id)
    else:
        content = News.objects.all()
    serializers = NewsContentSetSerializer(content, many=True)
    return Response(serializers.data)

@api_view(['POST'])
def news_add(request):
    title = request.POST.get('title')
    category = request.POST.get('category')
    sub_title = request.POST.get('sub_title')
    content = request.POST.get('content')
    image = request.FILES.get('image')
    image_url = None
    if image:
        ext = os.path.splitext(image.name)[1]
        new_filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join('uploads', new_filename)
        saved_path = default_storage.save(filepath, image)
        image_url = default_storage.url(saved_path)
        print(f"저장된 이미지 이름: {new_filename}")

    news_main = News.objects.create(
        title=title,
        content=sub_title,
        image=image,
        type=category
    )

    News_content.objects.create(
        title=title,
        content=content,
        type=category,
        news=news_main
    )

    return Response({'message': '성공'}, status=201)


@api_view(['GET'])
def News_data_id(request, id):
    if id is not None:
        head_data = News.objects.get(id=id)
        content = News_content.objects.filter(news=head_data)
    serializers = News_id_data_serializer(content, many=True)
    return Response(serializers.data)


#협회소식 메인 데이터셋 생성
@api_view(['POST'])
def create_news(request):
    serializers = News_Set_Serializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.data, status=status.HTTP_400_BAD_REQUEST)

#협회소식 content 생성
@api_view(['POST'])
def create_news_content(request):
    serializers = NewsContent_Set_Serializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.data, status=status.HTTP_400_BAD_REQUEST)

#공지사항
@api_view(['GET'])
def Notice_DataSet(request):
    search_keyword = request.GET.get('search')
    if search_keyword:
        # title 또는 content 에서 검색
        content = Notice.objects.filter(
            Q(title__icontains=search_keyword)
        ).order_by('-id')  # 필요시 정렬
    else:
        content = Notice.objects.all().order_by('-id')

    serializers = NoticeSetSerializer(content, many=True)
    return Response(serializers.data)

@api_view(['POST'])
def notice_add(request):
    title = request.POST.get('title')
    content = request.POST.get('content')
    notice = Notice.objects.create(
        title=title,
        date=datetime.datetime.now()
    )
    notice.save()
    notice_content =Notice_content.objects.create(
        title=title,
        date=datetime.datetime.now(),
        content=content,
        notice=notice
    )
    notice_content.save()

    return Response(status=status.HTTP_201_CREATED)
@api_view(['GET'])
def Notice_detail(request, id):
    try:
        notice = Notice.objects.get(id=id)
        set_up_data = notice.notice_content  # OneToOneField 이므로 역참조 사용
        serializer = NoticeContentSerializer(set_up_data)
        return Response(serializer.data)
    except Notice.DoesNotExist:
        return Response({"error": "Notice not found"}, status=404)
    except Notice_content.DoesNotExist:
        return Response({"error": "Notice content not found"}, status=404)

#공지사항 메인 데이터셋 생성
@api_view(['POST'])
def create_notice(request):
    serializers = Notice_Set_Serializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.data, status=status.HTTP_400_BAD_REQUEST)

#공지사항 content 생성
@api_view(['POST'])
def create_notice_content(request):
    serializers = NoticeContentSerializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.data, status=status.HTTP_400_BAD_REQUEST)

#조직도
@api_view(['GET'])
def organization_all_data(request):
    president_qs = ORGANIZATION_PRESIDENT.objects.all()
    vice_president_qs = ORGANIZATION_VICE_PRESIDENT.objects.all()
    director_qs = ORGANIZATION_DIRECTOR.objects.all()

    president_data = OrganizationPresidentSerializer(president_qs, many=True).data
    vice_president_data = Organization_vicePresidentSerializer(vice_president_qs, many=True).data
    director_data = Organization_directorerializer(director_qs, many=True).data

    return Response({
        "president": president_data,
        "vicePresidents": vice_president_data,
        "directors": director_data,
    })
@api_view(['POST'])
def organizational_add(request):
    organ_type = request.POST.get('position')
    name = request.POST.get('name')
    try:
        image_file = request.FILES.get('image')
        if image_file:
            ext = os.path.splitext(image_file.name)[1]  # 확장자 유지
            new_filename = f"{uuid.uuid4().hex}{ext}"
            image_file.name = new_filename  # 이미지 이름 변경
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
        # 주요 경력 목록 추출
    careers = []
    for key in request.POST:
        if key.startswith('career_'):
            careers.append(request.POST[key])
    if organ_type == '이사장':
        organizational = ORGANIZATION_PRESIDENT.objects.create(
            name=name,
            image=image_file,
            position='이사장'
        )
        organizational.save()
        for carer_text in careers:
            carees = ORGANIZATION_PRESIDENT_PROFILE.objects.create(
                title=carer_text,
                ORGANIZATION_PRESIDENT = organizational
            )
            carees.save()
    if organ_type == '부이사장':
        organizational = ORGANIZATION_VICE_PRESIDENT.objects.create(
            name=name,
            image=image_file,
            position='부이사장'
        )
        organizational.save()
        for carer_text in careers:
            carees = ORGANIZATION_VICE_PRESIDENT_PROFILE.objects.create(
                title=carer_text,
                ORGANIZATION_VICE_PRESIDENT=organizational
            )
            carees.save()
    else:
        organizational = ORGANIZATION_DIRECTOR.objects.create(
            name=name,
            image=image_file,
            position=str(organ_type)
        )
        organizational.save()
        for carer_text in careers:
            carees = ORGANIZATION_DIRECTOR_PROFILE.objects.create(
                title=carer_text,
                ORGANIZATION_DIRECTOR=organizational
            )
            carees.save()
    return Response(status=status.HTTP_201_CREATED)
@api_view(['POST'])
def create_organizational_chart(request):
    serializer = or_chart_serializer(data=request.data)
    try:
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#조직도 content 생성
@api_view(['POST'])
def create_organizational_title(request):
    serializer = OrTitleSetSerializer(data=request.data)
    try:
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def upload_image(request):
    image = request.FILES.get('file')

    if not image:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    # 고유한 파일 이름 생성
    ext = os.path.splitext(image.name)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join('uploads', filename)

    # 파일 저장
    saved_path = default_storage.save(filepath, image)

    # 🔥 Cloudflare R2 URL 가져오기
    image_url = default_storage.url(saved_path)

    return Response({'url': image_url}, status=status.HTTP_201_CREATED)