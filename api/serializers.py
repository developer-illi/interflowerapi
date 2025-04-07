# myapp/serializers.py

from rest_framework import serializers
from .models import *

#인삿말
class Greeting_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Association_greeting
        fields = '__all__'

#연혁
class HistoryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = History_event
        fields = '__all__'
class HistoryContentSerializer(serializers.ModelSerializer):
    event = HistoryEventSerializer(source='history_event_set', many=True, read_only=True)
    class Meta:
        model = History_content
        fields = '__all__'

class HistorySetUpSerializer(serializers.ModelSerializer):
    contents = HistoryContentSerializer(source='history_content_set', many=True, read_only=True)

    class Meta:
        model = History_set_up
        fields = '__all__'

#조직도
class Organizational_titleSetSerializer(serializers.ModelSerializer):
    class Meta:
         model = Organizational_title
         fields = '__all__'
class OrganizationalSetSerializer(serializers.ModelSerializer):
    contents = Organizational_titleSetSerializer(source='Organizational_title', many=True, read_only=True)

    class Meta:
        model = Organizational_chart
        fields = '__all__'

#국내전시

#국내전시 컨탠츠
class Local_ContentSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Local_content
        fields = '__all__'


#국내전시 메인 데이터셋
class LocalSetSerializer(serializers.ModelSerializer):
    contents = Local_ContentSetSerializer(source='Local_content', many=True, read_only=True)

    class Meta:
        model = Local
        fields = '__all__'


#국외전시

#국외전시 컨탠츠
class OverseasContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Overseas_content
        fields = '__all__'


#국외전시 메인 데이터셋
class OverseasSetSerializer(serializers.ModelSerializer):
    contents = OverseasContentSerializer(source='Overseas_content')

    class Meta:
        model = Overseas
        fields = '__all__'

#자격증

#자격증 컨탠츠
class LicenseContentSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = License_content
        fields = '__all__'


#자격증 메인 데이터셋
class LicenseSetSerializer(serializers.ModelSerializer):
    contents = LicenseContentSetSerializer(source='License_content', many=True, read_only=True)
    class Meta:
        model = License
        fields = '__all__'


#대외활동

#대외활동 계시판
class ContestsBulletinboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contests_Block
        fields = '__all__'


#대외활동 컨탠츠
class ContestsContentSerializer(serializers.ModelSerializer):
    contents = ContestsBulletinboardSerializer(source='Contests_Block', many=True, read_only=True)
    class Meta:
        model = Contests_content
        fields = '__all__'

#대외활동 메인 데이터셋
class ContestsSetSerializer(serializers.ModelSerializer):
    contents = ContestsContentSerializer(source='Content_content', many=True, read_only=True)
    class Meta:
        model = Contests
        fields = '__all__'


#나중에 참고 자료
# 협회소식

#협회소식 content
class NewsContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = News_content
        fields = ['block_type', 'content', 'order']


#협회소식 메인 Data_Set
class NewsContentSetSerializer(serializers.ModelSerializer):
    blocks = NewsContentSerializer(many=True, read_only=True)  # blocks는 related_name

    class Meta:
        model = News
        fields = ['title', 'type', 'content', 'created_at', 'category', 'blocks']

# class NewsContentSetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = News_content
#         fields = '__all__'
#
# class NewsSetSerializer(serializers.ModelSerializer):
#     contents = NewsContentSetSerializer(source='News_content', many=True, read_only=True)
#     class Meta:
#         model = News
#         fields = '__all__'