from rest_framework.response import Response
from rest_framework import status

from taschoolassistant.core.serializers import StandardOutSerializer, StandardErrorOutSerializer


class ApiResponse:
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """
        Standardized success response.
        """

        return Response(
            StandardOutSerializer({
                "status": status_code,
                "message": message,
                "data": data,
            }).data,
            status=status_code
        )

    @staticmethod
    def error(message="An error occurred", status_code=status.HTTP_400_BAD_REQUEST, errors=None):
        """
        Standardized error response.
        """
        return Response(
            StandardErrorOutSerializer({
                "status": status_code,
                "message": message,
                "errors": errors or {}
            }).data,
            status=status_code
        )
