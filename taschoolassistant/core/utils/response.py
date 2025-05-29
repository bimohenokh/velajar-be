from rest_framework.response import Response
from rest_framework import status

from taschoolassistant.core.serializers import StandardOutSerializer


class ApiResponse:
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """
        Standardized success response.
        """
        if status_code == status.HTTP_204_NO_CONTENT:
            return Response(
                status=status_code,
            )

        return Response(
            StandardOutSerializer({
                "status": status_code,
                "message": message,
                "data": data,
            }).data,
            status=status_code
        )
