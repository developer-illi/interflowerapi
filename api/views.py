import datetime

from rest_framework import viewsets
from .serializers import *
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
import os
from django.core.files.storage import default_storage
from django.db import transaction
from api.utils import image_utile


def parse_date_or_now(value, fallback=None):
    """관리자 폼이 보내온 날짜 문자열을 datetime 으로. 비었거나 못 읽으면 fallback.

    이전에는 date 필드가 auto_now 라 무슨 값을 넣든 무시됐지만,
    이제 실제로 저장되므로 파싱에 실패했을 때 NULL 이 들어가지 않도록 방어한다.
    """
    if fallback is None:
        fallback = timezone.now()
    if isinstance(value, datetime.datetime):
        return value
    if not value:
        return fallback

    parsed = parse_datetime(str(value))
    if parsed is None:
        day = parse_date(str(value))
        if day is not None:
            parsed = datetime.datetime.combine(day, datetime.time.min)
    if parsed is None:
        return fallback
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_default_timezone())
    return parsed

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
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
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

        content_text = request.POST.get('text')
        image_file = image_utile.process_request_image(request)

        # History_content 생성
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
        return Response({"detail": "해당 ID의 연혁이 존재하지 않습니다.", "error": "해당 ID의 연혁이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError:
        raise  # 이미지 검증 실패 등은 DRF 핸들러가 {'detail': ...} 로 정리한다
    except Exception as e:
        return Response({"detail": str(e), "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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

@api_view(['DELETE'])
def del_his_event(request, id):
    try:
        ori_content = History_event.objects.get(id=id)
    except History_event.DoesNotExist:
        raise NotFound(detail="해당 이벤트가 존재하지 않습니다.")

    ori_content.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

#국내/국외전시
# 이전에는 'domestic' 이외의 모든 값(오타/누락 포함)이 조용히 국외전시로 폴백됐다.
DOMESTIC_TYPES = {'domestic'}
INTERNATIONAL_TYPES = {'international', 'overseas'}  # overseas 는 하위호환


@api_view(['GET'])
def Local_DataSet(request):
    get_data_type = (request.GET.get('type') or '').strip().lower()

    if get_data_type in DOMESTIC_TYPES:
        data_set = Local.objects.all().order_by('id')
        serializers = LocalSetSerializer(data_set, many=True)
    elif get_data_type in INTERNATIONAL_TYPES:
        data_set = Overseas.objects.all().order_by('id')
        serializers = OverseasSetSerializer(data_set, many=True)
    else:
        return Response(
            {'detail': "invalid type. 'domestic' 또는 'international' 만 허용합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response(serializers.data)

@api_view(['POST'])
def domesticAdd(request):
    try:
        image_file = image_utile.process_request_image(request)
    except ValidationError:
        raise  # 이미지 검증 실패 등은 DRF 핸들러가 {'detail': ...} 로 정리한다
    except Exception as e:
        return Response({"detail": str(e), "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    Local.objects.create(
        title=request.POST.get('title'),
        subTitle=request.POST.get('subTitle'),
        content=request.POST.get('content'),
        headerImage=image_file
    )
    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def domesticContnentAdd(request, id):
    try:
        domestic = Local.objects.get(id=id)
        image_file = image_utile.process_request_image(request)
    except Local.DoesNotExist:
        return Response({"detail": "해당 전시가 존재하지 않습니다.", "error": "해당 전시가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError:
        raise  # 이미지 검증 실패 등은 DRF 핸들러가 {'detail': ...} 로 정리한다
    except Exception as e:
        return Response({"detail": str(e), "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    Local_content.objects.create(
        title=request.POST.get('title'),
        date=timezone.now(),
        description=request.POST.get('content'),
        image=image_file,
        local=domestic
    )
    return Response(status=status.HTTP_201_CREATED)


@api_view(['POST'])
def overseasAdd(request):
    try:
        image_file = image_utile.process_request_image(request)
    except ValidationError:
        raise  # 이미지 검증 실패 등은 DRF 핸들러가 {'detail': ...} 로 정리한다
    except Exception as e:
        return Response({"detail": str(e), "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    Overseas.objects.create(
        title=request.POST.get('title'),
        sub_title=request.POST.get('subTitle'),
        content=request.POST.get('content'),
        headerImage=image_file
    )
    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def overseasContnentAdd(request, id):
    try:
        main_data = Overseas.objects.get(id=id)
        image_file = image_utile.process_request_image(request)
    except Overseas.DoesNotExist:
        return Response({"detail": "해당 전시가 존재하지 않습니다.", "error": "해당 전시가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError:
        raise  # 이미지 검증 실패 등은 DRF 핸들러가 {'detail': ...} 로 정리한다
    except Exception as e:
        return Response({"detail": str(e), "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    Overseas_content.objects.create(
        title=request.POST.get('title'),
        date=timezone.now(),
        description=request.POST.get('content'),
        image=image_file,
        overseas=main_data
    )
    return Response(status=status.HTTP_201_CREATED)

#국내 전시 컨탠츠 생성
@api_view(['POST'])
def create_local_content(request):
    serializers = Local_ContentSetSerializer(request.data)
    if serializers.is_valid():
        serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


# 국내전시 수정/삭제
@api_view(['PATCH'])
def domestic_update(request, id):
    try:
        local = Local.objects.get(id=id)
    except Local.DoesNotExist:
        raise NotFound(detail="해당 국내전시가 존재하지 않습니다.")

    local.title = request.POST.get('title', local.title)
    local.subTitle = request.POST.get('subTitle', local.subTitle)
    local.content = request.POST.get('content', local.content)
    image = image_utile.process_request_image(request)
    if image:
        local.headerImage = image
    local.save()
    return Response({'message': '수정 완료'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def domestic_delete(request, id):
    try:
        local = Local.objects.get(id=id)
    except Local.DoesNotExist:
        raise NotFound(detail="해당 국내전시가 존재하지 않습니다.")
    local.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def domestic_content_delete(request, id):
    try:
        item = Local_content.objects.get(id=id)
    except Local_content.DoesNotExist:
        raise NotFound(detail="해당 항목이 존재하지 않습니다.")
    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# 국외전시 수정/삭제
@api_view(['PATCH'])
def overseas_update(request, id):
    try:
        overseas = Overseas.objects.get(id=id)
    except Overseas.DoesNotExist:
        raise NotFound(detail="해당 국외전시가 존재하지 않습니다.")

    overseas.title = request.POST.get('title', overseas.title)
    overseas.sub_title = request.POST.get('subTitle', overseas.sub_title)
    overseas.content = request.POST.get('content', overseas.content)
    image = image_utile.process_request_image(request)
    if image:
        overseas.headerImage = image
    overseas.save()
    return Response({'message': '수정 완료'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def overseas_delete(request, id):
    try:
        overseas = Overseas.objects.get(id=id)
    except Overseas.DoesNotExist:
        raise NotFound(detail="해당 국외전시가 존재하지 않습니다.")
    overseas.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def overseas_content_delete(request, id):
    try:
        item = Overseas_content.objects.get(id=id)
    except Overseas_content.DoesNotExist:
        raise NotFound(detail="해당 항목이 존재하지 않습니다.")
    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# 자격증 수정/삭제
@api_view(['PATCH'])
def license_update(request, id):
    try:
        license = License.objects.get(id=id)
    except License.DoesNotExist:
        raise NotFound(detail="해당 자격증이 존재하지 않습니다.")

    license.title = request.POST.get('title', license.title)
    license.content = request.POST.get('content', license.content)
    header_image = image_utile.process_request_image(request)
    if header_image:
        license.headerImage = header_image
    license.save()

    try:
        license_content = license.license_certification
        license_content.information = request.POST.get('licenseInfo', license_content.information)
        license_content.hyperlink = request.POST.get('link', license_content.hyperlink)
        sub_image = image_utile.process_request_image(request, field='subImage')
        if sub_image:
            license_content.image = sub_image
        license_content.save()
    except License_content.DoesNotExist:
        pass

    return Response({'message': '수정 완료'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def license_delete(request, id):
    try:
        license = License.objects.get(id=id)
    except License.DoesNotExist:
        raise NotFound(detail="해당 자격증이 존재하지 않습니다.")
    license.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

#주력사업
@api_view(['POST'])
def activitiesAdd(request):
    try:
        image_file = image_utile.process_request_image(request)
    except ValidationError:
        raise  # 이미지 검증 실패 등은 DRF 핸들러가 {'detail': ...} 로 정리한다
    except Exception as e:
        return Response({"detail": str(e), "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    Contests.objects.create(
        title=request.POST.get('title'),
        content=request.POST.get('content'),
        headerImage=image_file
    )
    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def acticontentAdd(request, id):
    try:
        main_data = Contests.objects.get(id=id)
        image_file = image_utile.process_request_image(request)
    except Contests.DoesNotExist:
        return Response({"detail": "해당 사업이 존재하지 않습니다.", "error": "해당 사업이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError:
        raise  # 이미지 검증 실패 등은 DRF 핸들러가 {'detail': ...} 로 정리한다
    except Exception as e:
        return Response({"detail": str(e), "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    title = request.POST.get('title')
    date = parse_date_or_now(request.POST.get('date'))

    acti_content = Contests_content.objects.create(
        mainImage=image_file,
        title=title,
        date=date,
        location=request.POST.get('location'),
        content=request.POST.get('content'),
        contests=main_data
    )
    Contents_gallery.objects.create(
        id=acti_content.id,
        title=title,
        date=date,
        description=request.POST.get('description'),
        image=image_file,
        target_content=main_data
    )
    Content_florist.objects.create(
        name=request.POST.get('florists'),
        target_content=acti_content
    )
    return Response(status=status.HTTP_201_CREATED)

#대외사업 데이터 조회
@api_view(['GET'])
def Overseas_DataSet(request):
    overseas = Overseas.objects.all().order_by('id')
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
    license = License.objects.all().order_by('id')
    serializers = LicenseSetSerializer(license, many=True)
    return Response(serializers.data)

@api_view(['POST'])
def licenseAdd(request):
    try:
        image_file = image_utile.process_request_image(request)
        sub_image = image_utile.process_request_image(request, field='subImage')
    except ValidationError:
        raise  # 이미지 검증 실패 등은 DRF 핸들러가 {'detail': ...} 로 정리한다
    except Exception as e:
        return Response({"detail": str(e), "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    license = License.objects.create(
        title=request.POST.get('title'),
        content=request.POST.get('content'),
        headerImage=image_file
    )
    License_content.objects.create(
        image=sub_image,
        information=request.POST.get('licenseInfo'),
        hyperlink=request.POST.get('link'),
        license=license
    )
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
    detail_data = Contests_content.objects.get(id=id)
    serializers = ContestsContentSerializer(detail_data)
    return Response(serializers.data)


@api_view(['PATCH'])
def activity_update(request, id):
    try:
        activity = Contests.objects.get(id=id)
    except Contests.DoesNotExist:
        raise NotFound(detail="해당 주요사업이 존재하지 않습니다.")

    activity.title = request.POST.get('title', activity.title)
    activity.content = request.POST.get('content', activity.content)

    image = image_utile.process_request_image(request)
    if image:
        activity.headerImage = image
    activity.save()

    return Response({'message': '수정 완료'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def activity_delete(request, id):
    try:
        activity = Contests.objects.get(id=id)
    except Contests.DoesNotExist:
        raise NotFound(detail="해당 주요사업이 존재하지 않습니다.")

    activity.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
def acticontent_update(request, id):
    try:
        acti_content = Contests_content.objects.get(id=id)
    except Contests_content.DoesNotExist:
        raise NotFound(detail="해당 활동 내역이 존재하지 않습니다.")

    title = request.POST.get('title', acti_content.title)
    date = parse_date_or_now(request.POST.get('date'), fallback=acti_content.date)
    location = request.POST.get('location', acti_content.location)
    content = request.POST.get('content', acti_content.content)
    description = request.POST.get('description')
    florists = request.POST.get('florists')

    acti_content.title = title
    acti_content.date = date
    acti_content.location = location
    acti_content.content = content

    image = image_utile.process_request_image(request)
    if image:
        acti_content.mainImage = image
    acti_content.save()

    # 같은 id로 함께 생성된 갤러리도 동기화
    try:
        gallery = Contents_gallery.objects.get(id=id)
        gallery.title = title
        gallery.date = date
        if description is not None:
            gallery.description = description
        if image:
            gallery.image = image
        gallery.save()
    except Contents_gallery.DoesNotExist:
        pass

    # 플로리스트는 전체 교체 (생성 시에도 단일 row 생성)
    if florists is not None:
        Content_florist.objects.filter(target_content=acti_content).delete()
        Content_florist.objects.create(name=florists, target_content=acti_content)

    return Response({'message': '수정 완료'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def acticontent_delete(request, id):
    try:
        acti_content = Contests_content.objects.get(id=id)
    except Contests_content.DoesNotExist:
        raise NotFound(detail="해당 활동 내역이 존재하지 않습니다.")

    # 같은 id로 생성된 갤러리 row도 함께 제거 (FK가 Contests라 자동 CASCADE 안 됨)
    Contents_gallery.objects.filter(id=id).delete()
    acti_content.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


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
        content = News.objects.filter(type=get_type)
    else:
        content = News.objects.all()
    # 정렬이 없어 DB가 주는 임의 순서로 나갔다. 최신 우선으로 고정. (P0-3)
    content = content.order_by('-date', '-id')
    serializers = NewsContentSetSerializer(content, many=True)
    return Response(serializers.data)

@api_view(['POST'])
def news_add(request):
    title = request.POST.get('title')
    category = request.POST.get('category')
    sub_title = request.POST.get('sub_title')
    content = request.POST.get('content')
    image = request.FILES.get('image')
    if image:
        image = image_utile.resize_image(image)

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

@api_view(['PATCH'])
def news_update(request, id):
    try:
        news = News.objects.get(id=id)
    except News.DoesNotExist:
        raise NotFound(detail="해당 뉴스가 존재하지 않습니다.")

    news.title = request.POST.get('title', news.title)
    news.type = request.POST.get('category', news.type)
    news.content = request.POST.get('sub_title', news.content)

    image = image_utile.process_request_image(request)
    if image:
        news.image = image
    news.save()

    try:
        news_content = News_content.objects.get(news=news)
        news_content.title = news.title
        news_content.type = news.type
        news_content.content = request.POST.get('content', news_content.content)
        news_content.save()
    except News_content.DoesNotExist:
        pass

    return Response({'message': '수정 완료'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def del_news(request, id):
    try:
        ori_content = News.objects.get(id=id)
    except News.DoesNotExist:
        raise NotFound(detail="해당 뉴스가 존재하지 않습니다.")

    ori_content.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

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
        ).order_by('-date', '-id')
    else:
        content = Notice.objects.all().order_by('-date', '-id')

    # attachments / notice_content 를 행마다 조회하지 않도록 미리 가져온다
    content = content.prefetch_related('attachments').select_related('notice_content')

    serializers = NoticeSetSerializer(content, many=True)
    return Response(serializers.data)

def _save_notice_attachments(notice, uploaded_files):
    """multipart 의 files 키로 올라온 파일들을 검증 후 저장."""
    saved = []
    for uploaded in uploaded_files:
        image_utile.validate_attachment(uploaded)  # 위반 시 ValidationError(400)
        original_name = uploaded.name
        uploaded.name = image_utile.generate_unique_filename(original_name)
        saved.append(Notice_attachment.objects.create(
            notice=notice,
            file=uploaded,
            name=original_name,   # 한글 원본 파일명 보존
            size=uploaded.size,
        ))
    return saved


@api_view(['POST'])
def notice_add(request):
    title = request.POST.get('title')
    content = request.POST.get('content')

    if not title:
        return Response({'detail': '제목은 필수입니다.'}, status=status.HTTP_400_BAD_REQUEST)

    uploaded_files = request.FILES.getlist('files')
    for uploaded in uploaded_files:
        image_utile.validate_attachment(uploaded)

    with transaction.atomic():
        now = timezone.now()
        notice = Notice.objects.create(title=title, date=now)
        Notice_content.objects.create(
            title=title,
            date=now,
            content=content,
            notice=notice,
        )
        _save_notice_attachments(notice, uploaded_files)

    return Response(
        {'id': notice.id, 'attachmentCount': notice.attachments.count()},
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
def Notice_detail(request, id):
    try:
        notice = Notice.objects.get(id=id)
        set_up_data = notice.notice_content  # OneToOneField 이므로 역참조 사용
        serializer = NoticeContentSerializer(set_up_data)
        return Response(serializer.data)
    except Notice.DoesNotExist:
        return Response({"detail": "Notice not found", "error": "Notice not found"}, status=404)
    except Notice_content.DoesNotExist:
        return Response({"detail": "Notice content not found", "error": "Notice content not found"}, status=404)

@api_view(['PATCH'])
def notice_update(request, id):
    try:
        notice = Notice.objects.get(id=id)
    except Notice.DoesNotExist:
        raise NotFound(detail="해당 공지가 존재하지 않습니다.")

    uploaded_files = request.FILES.getlist('files')
    for uploaded in uploaded_files:
        image_utile.validate_attachment(uploaded)

    with transaction.atomic():
        title = request.POST.get('title', notice.title)
        notice.title = title
        # date 는 건드리지 않는다. 수정만으로 등록일이 오늘로 튀면 목록 정렬이 망가진다.
        notice.save()

        try:
            notice_content = notice.notice_content
        except Notice_content.DoesNotExist:
            notice_content = Notice_content(notice=notice, date=notice.date)

        notice_content.title = title
        # content 는 NOT NULL 이라 None 이 들어가면 IntegrityError
        notice_content.content = request.POST.get('content', notice_content.content) or ''
        notice_content.save()

        # 첨부는 덧붙이는 방식. 개별 삭제는 notice_attachment_delete 사용.
        _save_notice_attachments(notice, uploaded_files)

    return Response({
        'message': '수정 완료',
        'id': notice.id,
        'attachments': NoticeAttachmentSerializer(notice.attachments.all(), many=True).data,
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def notice_delete(request, id):
    try:
        notice = Notice.objects.get(id=id)
    except Notice.DoesNotExist:
        raise NotFound(detail="해당 공지가 존재하지 않습니다.")

    # CASCADE 로 행만 지우면 R2 객체가 고아로 남으므로 파일부터 정리
    for attachment in notice.attachments.all():
        if attachment.file:
            attachment.file.delete(save=False)

    notice.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def notice_attachment_delete(request, id):
    try:
        attachment = Notice_attachment.objects.get(id=id)
    except Notice_attachment.DoesNotExist:
        raise NotFound(detail="해당 첨부파일이 존재하지 않습니다.")

    if attachment.file:
        attachment.file.delete(save=False)
    attachment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


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
        image_file = image_utile.process_request_image(request)
    except ValidationError:
        raise  # 이미지 검증 실패 등은 DRF 핸들러가 {'detail': ...} 로 정리한다
    except Exception as e:
        return Response({"detail": str(e), "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_organizational_title(request):
    serializer = OrTitleSetSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def upload_image(request):
    image = image_utile.process_request_image(request, field='file')
    if not image:
        return Response({'detail': 'No file provided', 'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    filepath = os.path.join('uploads', image.name)
    saved_path = default_storage.save(filepath, image)
    image_url = default_storage.url(saved_path)

    return Response({'url': image_url}, status=status.HTTP_201_CREATED)