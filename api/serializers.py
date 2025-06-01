# myapp/serializers.py

from rest_framework import serializers
from .models import *

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
        fields = ['imgage', 'name', 'position', 'description']

    def get_description(self, obj):
        description = ORGANIZATION_VICE_PRESIDENT_PROFILE.objects.filter(ORGANIZATION_VICE_PRESIDENT=obj)
        return [p.title for p in description]

class Organization_directorerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = ORGANIZATION_DIRECTOR
        fields = ['imgage', 'name', 'position', 'description']

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
        return list(obj.local_mainImg.values_list('image', flat=True))
    def get_galleryList(self, obj):
        # mainImageList 값과 동일하게 반환
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

    class Meta:
        model = Overseas
        fields = '__all__'

    def get_mainImageList(self, obj):
        return list(obj.overseas_mainImg.values_list('image', flat=True))
    def get_galleryList(self, obj):
        # mainImageList 값과 동일하게 반환
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
            obj.content_gallery.order_by('-id'),  # ⭐ 여기서만 정렬 ⭐
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
    class Meta:
        model = News_content
        fields = '__all__'

class NewsContentSetSerializer(serializers.ModelSerializer):
    blocks = NewsContent_Set_Serializer(source='News_content', many=True, read_only=True)  # blocks는 related_name
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = News
        fields = '__all__'

class NoticeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice_content
        fields = '__all__'
class Notice_Set_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
class NoticeSetSerializer(serializers.ModelSerializer):
    notice = NoticeContentSerializer(source='notice_content', read_only=True)
    class Meta:
        model = Notice
        fields = '__all__'


# class ORGANIZATION_PRESIDENT_Serialzer(serializers.ModelSerializer):
#     ORGANIZATION_PRESIDENT =

