import time
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start

        if request.path.startswith('/api/'):
            logger.info(
                'api_request',
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status': response.status_code,
                    'duration_ms': round(duration * 1000),
                    'user_id': request.user.id if request.user.is_authenticated else None,
                }
            )

        return response
