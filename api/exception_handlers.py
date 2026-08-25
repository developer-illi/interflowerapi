import logging

from django.http import JsonResponse
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def _flatten_message(data):
    """DRF 가 만들어내는 제각각인 에러 본문을 사람이 읽을 문자열 하나로."""
    if isinstance(data, str):
        return data
    if isinstance(data, (list, tuple)):
        parts = [_flatten_message(item) for item in data]
        return ' '.join(p for p in parts if p)
    if isinstance(data, dict):
        for key in ('detail', 'error', 'message'):
            if key in data:
                return _flatten_message(data[key])
        parts = [f'{k}: {_flatten_message(v)}' for k, v in data.items()]
        return ' / '.join(parts)
    return str(data)


def normalize_error_body(data):
    """에러 응답을 항상 {'detail': str, 'error': str} 형태로 통일한다.

    이전에는 같은 400 이라도 본문이 네 가지 형태로 나갔다.
      {'detail': '...'} / ['...'] / {'error': "[ErrorDetail(string='...')]"} / {'error': '...'}
    프론트가 메시지를 꺼낼 방법이 없어 전부 '등록 실패' 로 뭉뚱그려졌다.
    error 키는 기존 코드 호환을 위해 함께 남긴다.
    """
    message = _flatten_message(data)
    body = {'detail': message, 'error': message}
    # 필드별 상세는 살려둔다 (폼 검증 에러 등)
    if isinstance(data, dict) and not {'detail', 'error', 'message'} & set(data):
        body['fields'] = data
    return body


def json_exception_handler(exc, context):
    """DRF 기본 핸들러가 처리하지 못한 예외까지 JSON 으로 돌려준다.

    기본 동작에서는 미처리 예외가 Django 로 전파되어 HTML 500 페이지가 나갔다.
    프론트는 JSON 파싱을 시도하다 통째로 실패하므로 화면이 백지가 된다.
    """
    response = drf_exception_handler(exc, context)
    if response is not None:
        response.data = normalize_error_body(response.data)
        return response

    view = context.get('view')
    request = context.get('request')
    logger.exception(
        'Unhandled API exception in %s (%s %s)',
        getattr(view, '__class__', type(view)).__name__,
        getattr(request, 'method', '?'),
        getattr(request, 'get_full_path', lambda: '?')(),
    )

    message = '서버 처리 중 오류가 발생했습니다.'
    return JsonResponse({'detail': message, 'error': message}, status=500)


def server_error(request, *args, **kwargs):
    """DRF 밖(일반 Django 뷰/미들웨어)에서 터진 500도 JSON 으로."""
    message = '서버 처리 중 오류가 발생했습니다.'
    return JsonResponse({'detail': message, 'error': message}, status=500)


def not_found(request, exception, *args, **kwargs):
    return JsonResponse({'detail': 'not found', 'error': 'not found'}, status=404)
