from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView

from taschoolassistant.chain_notes.exceptions import CannotChangeChainNoteStatus
from taschoolassistant.chain_notes.models import ChainNote
from taschoolassistant.chain_notes.serializers import (
    ChainNoteParamSerializer,
    ChainNoteSerializer,
)
from taschoolassistant.core.utils.response import ApiResponse
from taschoolassistant.courses.models import CourseSession


class ChainNoteView(APIView):
    # TODO add permission classes

    def get(self, request):
        param_serializer = ChainNoteParamSerializer(data=request.query_params)
        param_serializer.is_valid(raise_exception=True)

        # TODO check if user is participant of the course session

        course_session_id = param_serializer.validated_data.get('course_session_id')

        chain_note = get_object_or_404(ChainNote, course_session_id=course_session_id)

        chain_note_serializer_out = ChainNoteSerializer(chain_note)

        return ApiResponse.success(
            data=chain_note_serializer_out.data,
            message="Chain Note successfully retrieved",
        )

    def post(self, request):
        # course_session_id = header_serializer.validated_data.get('course_session_id')
        # course_session = get_object_or_404(CourseSession, course_session_id=course_session_id)

        # TODO check if user is instructor of the course session

        serializer = ChainNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return ApiResponse.success(
            data=serializer.data,
            message="Chain Note successfully created",
            status_code=status.HTTP_201_CREATED,
        )


class ChainNoteViewById(APIView):
    # TODO add permission classes

    def get(self, request, pk):
        chain_note = get_object_or_404(ChainNote, pk=pk)

        chain_note_serializer_out = ChainNoteSerializer(chain_note)

        return ApiResponse.success(
            data=chain_note_serializer_out.data,
            message="Chain Note successfully retrieved",
        )

    def put(self, request, pk):
        chain_note: ChainNote = get_object_or_404(ChainNote, pk=pk)

        # TODO check if user is instructor of the course session
        # current_user = request.user

        serializer = ChainNoteSerializer(chain_note, data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.data.get("status") == ChainNote.Status.DRAFT.value:
            if chain_note.status == ChainNote.Status.ONGOING or ChainNote.Status.FINISHED:
                raise CannotChangeChainNoteStatus(
                    detail="Cannot change status from ongoing or finished to draft",
                )

        serializer.save()

        if chain_note.status == ChainNote.Status.DRAFT:
            return ApiResponse.success(
                data=serializer.data,
                message="Chain Note draft successfully updated",
            )

        elif chain_note.status == ChainNote.Status.ONGOING:
            # TODO
            pass

        elif chain_note.status == ChainNote.Status.FINISHED:
            # TODO
            pass

        else :
            raise NotImplementedError()


# class ChainNoteStatusView(APIView):
#     def get(self, request, pk):
#         chain_note = get_object_or_404(ChainNote, pk=pk)
#
#         chain_note_serializer_out = ChainNoteSerializer(chain_note)
#
#         return ApiResponse.success(
#             data=chain_note_serializer_out.data,
#             message="Chain Note successfully retrieved",
#         )