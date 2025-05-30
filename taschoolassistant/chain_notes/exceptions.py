from rest_framework import status
from rest_framework.exceptions import APIException


class CannotChangeChainNoteStatus(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = "Cannot change chain note status"
    default_code = "cannot_change_chain_note_status"


class ChainNoteAlreadyStartedException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = "Cannot change chain note after it already started"
    default_code = "chain_note_already_started"


class ChainNoteTurnHasFinishedException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = "Chain note turn has finished"
    default_code = "chain_note_turn_has_finished"


class ChainNoteTurnAlreadySkippedException(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = "Cannot skip chain note turn after it already skipped"
    default_code = "chain_note_turn_already_skipped"


class LongPollingTimeoutException(APIException):
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    default_detail = "Long polling timeout"
    default_code = "long_polling_timeout"