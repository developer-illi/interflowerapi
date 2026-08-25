from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnlyOrAuthenticated(BasePermission):
    """조회는 누구나, 쓰기는 로그인한 관리자만.

    단 settings.ENFORCE_WRITE_AUTH 가 False 인 동안에는 쓰기도 그대로 허용한다.
    프론트가 Authorization 헤더를 붙이도록 수정되기 전에 백엔드만 먼저 배포하면
    관리자 화면의 등록/수정이 전부 401 로 죽기 때문에, 전환은 env 플래그로 분리한다.

    전환 순서:
      1) 이 코드 배포 (ENFORCE_WRITE_AUTH=False → 기존과 동일하게 동작)
      2) 관리자 계정 생성 + 프론트가 /auth/token 으로 토큰을 받아 헤더에 싣도록 수정
      3) ENFORCE_WRITE_AUTH=True 로 바꾸고 재시작
    """

    message = '관리자 로그인이 필요합니다.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not getattr(settings, 'ENFORCE_WRITE_AUTH', False):
            return True
        return bool(request.user and request.user.is_authenticated)
