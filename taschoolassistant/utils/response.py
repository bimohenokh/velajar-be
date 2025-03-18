from rest_framework.response import Response
from rest_framework import status


class ApiResponse:
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """
        Standardized success response.
        """
        return Response({
            "status": "success",
            "message": message,
            "data": data
        }, status=status_code)

    @staticmethod
    def error(message="An error occurred", status_code=status.HTTP_400_BAD_REQUEST, errors=None):
        """
        Standardized error response.
        """
        return Response({
            "status": "error",
            "message": message,
            "errors": errors
        }, status=status_code)
