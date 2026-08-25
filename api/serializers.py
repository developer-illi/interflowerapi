# myapp/serializers.py

from rest_framework import serializers
from .models import *


def safe_file_url(file_field):
    """파일이 실제로 붙어 있을 때만 URL을 반환.

    ImageField 가 비어 있는데 .url 에 접근하면 ValueError 가 나고,
    그 한 건 때문에 목록 API 전체가 500 이 된다.
    (운영 DB api_local_content id=93 → GET /exhibition?type=domestic 전체 장애)
    """
    if not file_field:
        return None
    try:
        return file_field.url
    except (ValueError, AttributeError):
        return None

#인삿말
class Greeting_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Association_greeting
        fields = '__all__'
class Greeting_name_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Greeting_user
        fields = '__all__'
#연혁

class Greeting_Dataset(serializers.ModelSerializer):
    writer = Greeting_name_Serializer(source='greeting_user', many=True, read_only=True)

    class Meta:
        model = Association_greeting
        fields = '__all__'

class HistoryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = History_event
        fields = '__all__'

class History_content_Serializer(serializers.ModelSerializer):
    class Meta:
        model = History_content
        fields = '__all__'
class HistoryContentSerializer(serializers.ModelSerializer):
    event = HistoryEventSerializer(source='history_event_set', many=True, read_only=True)
    class Meta:
        model = History_content
        fields = '__all__'

class History_Set_Serializer(serializers.ModelSerializer):
    class Meta:
        model = History_set_up
        fields = '__all__'

class HistorySetUpSerializer(serializers.ModelSerializer):
    contents = HistoryContentSerializer(source='history_content_set', many=True, read_only=True)

    class Meta:
        model = History_set_up
        fields = '__all__'

#조직도
class OrganizationPresidentSerializer(serializers.ModelSerializer):
    # 연결된 프로필들을 포함 (related_name이 없다면 소문자모델명_set 사용됨)
    description = serializers.SerializerMethodField()

    class Meta:
        model = ORGANIZATION_PRESIDENT
        fields = ['image', 'name', 'position', 'description']

    def get_description(self, obj):
        description = ORGANIZATION_PRESIDENT_PROFILE.objects.filter(ORGANIZATION_PRESIDENT=obj)
        return [p.title for p in description]

class Organization_vicePresidentSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = ORGANIZATION_VICE_PRESIDENT
        fields = ['image', 'name', 'position', 'description']

    def get_description(self, obj):
        description = ORGANIZATION_VICE_PRESIDENT_PROFILE.objects.filter(ORGANIZATION_VICE_PRESIDENT=obj)
        return [p.title for p in description]

class Organization_directorerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = ORGANIZATION_DIRECTOR
        fields = ['image', 'name', 'position', 'description']

    def get_description(self, obj):
        description = ORGANIZATION_DIRECTOR_PROFILE.objects.filter(ORGANIZATION_DIRECTOR=obj)
        return [p.title for p in description]

class or_chart_serializer(serializers.ModelSerializer):
    class Meta:
        model = Organizational_chart
        fields = '__all__'

class OrTitleSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizational_title
        fields = '__all__'

class OrChartSetSerializer(serializers.ModelSerializer):
    organizational = OrTitleSetSerializer(source='organizational_title_set', many=True)
    class Meta:
        model = Organizational_chart
        fields = '__all__'

#국내전시

#국내전시 컨탠츠

class Local_ContentSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Local_content
        fields = '__all__'
class Local_imgContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Local_content
        fields = ['image']

class LocalSetSerializer(serializers.ModelSerializer):
    # mainImageList = Local_ContentSetSerializer(source='local_mainImg', many=True, read_only=True)
    mainImageList = serializers.SerializerMethodField()
    galleryList = serializers.SerializerMethodField()

    class Meta:
        model = Local
        fields = '__all__'
    def get_mainImageList(self, obj):
        urls = [safe_file_url(img.image) for img in obj.local_mainImg.all()]
        return [url for url in urls if url]

    def get_galleryList(self, obj):
        # mainImageList 값과 동일하게 반환 (모델 Meta.ordering 으로 최신순)
        return Local_ContentSetSerializer(obj.local_mainImg.all(), many=True).data

#국외전시

#국외전시 컨탠츠
class OverseasContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Overseas_content
        fields = '__all__'


#국외전시 메인 데이터셋
class Overseas_img_serializer(serializers.ModelSerializer):

    class Meta:
        model = Overseas_content
        fields = ['image']

class Overseas_Set_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Overseas
        fields = '__all__'
class OverseasSetSerializer(serializers.ModelSerializer):
    mainImageList = serializers.SerializerMethodField()
    galleryList = serializers.SerializerMethodField()
    # 프론트는 camelCase(subTitle)를 읽는데 이 모델만 sub_title 이라 표시가 안 됐다.
    # 기존 sub_title 키는 하위호환으로 그대로 두고 subTitle 을 추가한다. (P2-1)
    subTitle = serializers.CharField(source='sub_title', read_only=True)

    class Meta:
        model = Overseas
        fields = '__all__'

    def get_mainImageList(self, obj):
        request = self.context.get('request')
        urls = []
        for img in obj.overseas_mainImg.all():
            url = safe_file_url(img.image)
            if not url:
                continue
            urls.append(request.build_absolute_uri(url) if request else url)
        return urls

    def get_galleryList(self, obj):
        # mainImageList 값과 동일하게 반환 (모델 Meta.ordering 으로 최신순)
        return OverseasContentSerializer(obj.overseas_mainImg.all(), many=True).data

#자격증

#자격증 컨탠츠
class LicenseContentSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = License_content
        fields = '__all__'



#자격증 메인 데이터셋
class License_Set_Serializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = '__all__'

class LicenseSetSerializer(serializers.ModelSerializer):
    certification = serializers.SerializerMethodField()

    class Meta:
        model = License
        fields = '__all__'

    def get_certification(self, obj):
        certification = getattr(obj, 'license_certification', None)
        if certification:
            return LicenseContentSetSerializer(certification).data
        return None

#대외활동

#대외활동 컨탠츠

class ContentFloristSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content_florist
        fields = ['name']
class Content_img_data_serializer(serializers.ModelSerializer):
    class Meta:
        model = Contests_content
        fields = ['mainImage']

class ContestsContentSerializer(serializers.ModelSerializer):
    florists = serializers.SerializerMethodField()

    class Meta:
        model = Contests_content
        fields = '__all__'
    def get_florists(self, obj):
        return list(obj.content_florist.values_list('name', flat=True))
class Cotent_gallerySerializer(serializers.ModelSerializer):
    class Meta:
        ordering = ['id']
        model = Contents_gallery

        fields = '__all__'

class ContestsSerializer(serializers.ModelSerializer):
    activity_detail = ContestsContentSerializer(source='contest_title', many=True, read_only=True)
    florists = serializers.ModelSerializer
    galleryList = serializers.SerializerMethodField()
    # galleryList = Cotent_gallerySerializer(source='content_gallery', many=True, read_only=True)

    class Meta:
        model = Contests
        fields = '__all__'
    def get_florists(self, obj):
        return ContentFloristSerializer(obj.content_florist.all(), many=True).data

    def get_galleryList(self, obj):
        return Cotent_gallerySerializer(
            obj.content_gallery.order_by('-date', '-id'),
            many=True
        ).data

#나중에 참고 자료
#협회소식

#협회소식 content
class NewsContent_Set_Serializer(serializers.ModelSerializer):
    class Meta:
        model = News_content
        fields = '__all__'


#협회소식 메인 Data_Set
class News_Set_Serializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'


class News_id_data_serializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    sub_title = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = News_content
        fields = '__all__'

    def get_sub_title(self, obj):
        return obj.news.content

    def get_image(self, obj):
        if obj.news.image:
            return obj.news.image.url
        return None

class NewsContentSetSerializer(serializers.ModelSerializer):
    # source 가 'News_content' 로 잘못돼 있어 read_only 특성상 에러 없이
    # blocks 필드가 응답에서 통째로 빠져 있었다. related_name 은 'blocks'.
    blocks = NewsContent_Set_Serializer(many=True, read_only=True)
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = News
        fields = '__all__'

class NoticeAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Notice_attachment
        fields = ['id', 'name', 'url', 'size']

    def get_url(self, obj):
        return safe_file_url(obj.file)


class NoticeContentSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = Notice_content
        fields = '__all__'

    def get_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    def get_attachments(self, obj):
        return NoticeAttachmentSerializer(obj.notice.attachments.all(), many=True).data

class Notice_Set_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
class NoticeSetSerializer(serializers.ModelSerializer):
    notice = NoticeContentSerializer(source='notice_content', read_only=True)
    date = serializers.SerializerMethodField()
    attachmentCount = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = '__all__'

    def get_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    def get_attachmentCount(self, obj):
        return obj.attachments.count()

# class ORGANIZATION_PRESIDENT_Serialzer(serializers.ModelSerializer):
#     ORGANIZATION_PRESIDENT =

