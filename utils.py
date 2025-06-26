# this exception handler standardizes error responses
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging


logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Call drf default hendler
    response = exception_handler(exc, context)

    # if drf handled it, customize the response
    if response is not None:
        # log all 4xx & 5xx responses
        if response.status_code >= 400:
            view = context.get("view", None)
            logger.warning(
                f"Exception in {view.__class__.__name__ if view else 'unknown view'}: {str(exc)}"
            )

        return Response(
            {
                "error": {
                    "message": response.data.get("detail", str(response.data)),
                    "code": response.status_code,
                }
            },
            status=response.status_code,
        )

    # handle non-DRF exceptions
    logger.error(
        f"Unhandled exception in {context.get('view', 'unknown view') : {str(exc)}}",
        exc_info=True,
    )

    return Response(
        {
            "error": {
                "message": "An unexpected error occurred.",
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
