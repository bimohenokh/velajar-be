from rest_framework import status
from rest_framework.exceptions import APIException


class CannotChangeChainNoteStatus(APIException):
    status_code = status.HTTP_423_LOCKED
    detail = "Chain note status can't be changed."
    default_detail = "Cannot change chain note status"
