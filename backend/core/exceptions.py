from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': True,
            'status_code': response.status_code,
            'detail': response.data,
        }
        if isinstance(response.data, dict) and 'detail' in response.data:
            error_data['message'] = str(response.data['detail'])
        elif isinstance(response.data, list):
            error_data['message'] = response.data[0] if response.data else 'An error occurred.'
        else:
            error_data['message'] = 'An error occurred.'

        response.data = error_data

    return response


class SubscriptionLimitError(Exception):
    pass


class ScrapingError(Exception):
    pass
