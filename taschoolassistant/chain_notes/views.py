import asyncio
import random
from datetime import timedelta

from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.db import transaction
from django.shortcuts import get_object_or_404, aget_object_or_404
from django.utils import timezone
from django_q.tasks import schedule
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated

from taschoolassistant.chain_notes.exceptions import (
    ChainNoteAlreadyStartedException,
    ChainNoteTurnHasFinishedException,
    LongPollingTimeoutException,
)
from taschoolassistant.chain_notes.models import ChainNote, ChainNoteTurn
from taschoolassistant.chain_notes.serializers import (
    ChainNoteParamSerializer,
    ChainNoteSerializer,
    UpdateChainNoteSerializer,
    ChainNoteTurnSerializer,
)
from taschoolassistant.chain_notes.tasks import (
    check_chain_note_finished,
    check_chain_note_finished_name,
)
from taschoolassistant.core.utils.response import ApiResponse
from taschoolassistant.courses.models import CourseParticipant, CourseSession


class ChainNoteView(APIView):
    permission_classes = [IsAuthenticated]

    async def get(self, request):
        def _():
            param_serializer = ChainNoteParamSerializer(data=request.query_params)
            param_serializer.is_valid(raise_exception=True)

            course_session_id = param_serializer.validated_data.get("course_session_id")
            chain_note = get_object_or_404(
                ChainNote.objects.select_related("course_session"), course_session_id=course_session_id
            )

            try:
                # check if user is participant of the course
                course_instructor = (
                    CourseParticipant.objects.get_by_course_id_and_user_teacher_id(
                        chain_note.course_session.course_id, request.user.id
                    )
                )
            except CourseParticipant.DoesNotExist:
                raise PermissionDenied(
                    "User is not an instructor of this course",
                    "not_instructor_of_this_course",
                )

            chain_note_serializer_out = ChainNoteSerializer(chain_note)

            return ApiResponse.success(
                data=chain_note_serializer_out.data,
                message="Chain Note successfully retrieved",
            )
        return await sync_to_async(_)()

    async def post(self, request):
        def logic():
            serializer = ChainNoteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # check if user is instructor of the course
            course_session = serializer.validated_data.get("course_session")

            try:
                # check if user is instructor of the course
                course_instructor = (
                    CourseParticipant.objects.get_by_course_id_and_user_teacher_id(
                        course_session.course_id, request.user.id
                    )
                )
            except CourseParticipant.DoesNotExist:
                raise PermissionDenied(
                    "User is not an instructor of this course",
                    "not_instructor_of_this_course",
                )
            serializer.save()

            return ApiResponse.success(
                data=serializer.data,
                message="Chain Note successfully created",
                status_code=status.HTTP_201_CREATED,
            )

        return await sync_to_async(logic)()


class ChainNoteViewById(APIView):
    permission_classes = [IsAuthenticated]

    async def get(self, request, pk):
        def logic():
            chain_note: ChainNote = get_object_or_404(
                ChainNote.objects.select_related("course_session"), pk=pk
            )

            # check if user is instructor of the course session
            try:
                # check if user is instructor of the course
                course_instructor = (
                    CourseParticipant.objects.get_by_course_id_and_user_teacher_id(
                        chain_note.course_session.course_id, request.user.id
                    )
                )
            except CourseParticipant.DoesNotExist:
                raise PermissionDenied(
                    "User is not an instructor of this course",
                    "not_instructor_of_this_course",
                )

            chain_note_serializer_out = ChainNoteSerializer(chain_note)

            return ApiResponse.success(
                data=chain_note_serializer_out.data,
                message="Chain Note successfully retrieved",
            )

        return await sync_to_async(logic)()

    async def put(self, request, pk):
        def logic():
            chain_note: ChainNote = get_object_or_404(
                ChainNote.objects.select_related("course_session"), pk=pk
            )

            # check if user is instructor of the course session
            try:
                # check if user is instructor of the course
                course_instructor = (
                    CourseParticipant.objects.get_by_course_id_and_user_teacher_id(
                        chain_note.course_session.course_id,
                        request.user.id
                    )
                )
            except CourseParticipant.DoesNotExist:
                raise PermissionDenied(
                    "User is not an instructor of this course",
                    "not_instructor_of_this_course",
                )

            serializer = UpdateChainNoteSerializer(chain_note, data=request.data)
            serializer.is_valid(raise_exception=True)

            if chain_note.status != ChainNote.Status.DRAFT:
                raise ChainNoteAlreadyStartedException()

            serializer.save()

            return ApiResponse.success(
                data=serializer.data,
                message="Chain Note successfully updated",
            )

        return await sync_to_async(logic)()


class StartChainNoteView(APIView):
    permission_classes = [IsAuthenticated]

    # TODO tambahin background task pas Chain Note selesai
    async def post(self, request, pk):
        chain_note: ChainNote = await aget_object_or_404(
            ChainNote.objects.select_related("course_session"), pk=pk
        )

        try:
            # check if user is instructor of the course
            course_instructor = await CourseParticipant.objects.aget_by_course_id_and_user_teacher_id(
                chain_note.course_session.course_id,
                request.user.id
            )
        except CourseParticipant.DoesNotExist:
            raise PermissionDenied("User is not an instructor of this course", "not_instructor_of_this_course")


        if chain_note.status != ChainNote.Status.DRAFT:
            raise ChainNoteAlreadyStartedException()

        serializer = ChainNoteSerializer(chain_note, data=request.data, partial=True)

        await sync_to_async(
            lambda: serializer.is_valid(raise_exception=True), thread_sensitive=True
        )()
        serializer.validated_data["status"] = ChainNote.Status.ONGOING.value

        @sync_to_async
        @transaction.atomic
        def perform_transactional_update():
            serializer.save()

            # Prepare chain note turns
            new_chain_note_turns = []
            current_time = timezone.now()
            compensation_delay = timedelta(seconds=1)
            start_time = current_time + compensation_delay

            for student in course_students:
                new_chain_note_turns.append(
                    ChainNoteTurn(
                        chain_note_id=chain_note.id,
                        participant_id=student.id,
                        started_at=start_time,
                    )
                )
                start_time += chain_note.duration_per_participant

            # Save all turns
            ChainNoteTurn.objects.bulk_create(new_chain_note_turns)

            # Menjalankan task yang akan mengecek apakah Chain Note sudah selesai
            # jika sudah selesai, akan mengubah status Chain Note menjadi FINISHED
            schedule(
                f"{check_chain_note_finished.__module__}.{check_chain_note_finished.__name__}",
                pk,
                schedule_type="I",  # Interval
                minutes=0,
                repeats=-1,  # run indefinitely
                name=check_chain_note_finished_name(pk),
            )

        # Fetch course participants (excluding instructors)
        course_id = chain_note.course_session.course_id
        course_students: list[CourseParticipant] = [
            _
            async for _ in CourseParticipant.objects.filter(course_id=course_id)
            .exclude(courseinstructor__isnull=False)
            .all()
        ]

        # Shuffle the list
        random.shuffle(course_students)

        # Run the transactional DB operations inside a sync function
        await perform_transactional_update()

        return ApiResponse.success(
            data=serializer.data,
            message="Chain Note successfully started",
        )


class CurrentChainNoteTurnView(APIView):
    permission_classes = [IsAuthenticated]

    CHAIN_NOTE_FINISHED_RESPONSE = {
        "is_chain_note_finished": True,
    }

    async def get(self, request, pk):
        # check if user is participant of the course
        chain_note = await ChainNote.objects.select_related("course_session").aget(
            pk=pk
        )
        try:
            course_participant = (
                await CourseParticipant.objects.aget_by_course_id_and_user_id(
                    chain_note.course_session.course_id, request.user.id
                )
            )
        except CourseParticipant.DoesNotExist:
            raise PermissionDenied("User is not a participant of this course", "not_participant_of_this_course")

        last_known_turn_id = request.query_params.get("last_known_turn_id")
        last_known_turn_id = int(last_known_turn_id) if last_known_turn_id else None
        timeout_seconds = 30
        poll_interval = 1  # seconds

        chain_note = await aget_object_or_404(ChainNote, pk=pk)

        start_time = timezone.now()
        while (timezone.now() - start_time).seconds < timeout_seconds:
            # if ChainNote has ended
            if chain_note.is_ended:
                return ApiResponse.success(
                    data=self.CHAIN_NOTE_FINISHED_RESPONSE,
                    message="Chain Note has ended",
                    status_code=status.HTTP_200_OK,
                )

            # if ChainNote has not started
            elif chain_note.has_not_started:
                pass

            # if user dont have last known turn id
            # buat short polling juga bisa
            elif not last_known_turn_id:
                current_turn = (
                    await ChainNoteTurn.objects.aget_current_turn_by_chain_note(
                        chain_note
                    )
                )

                if current_turn is None:
                    return ApiResponse.success(
                        data=self.CHAIN_NOTE_FINISHED_RESPONSE,
                        message="Chain Note has ended",
                        status_code=status.HTTP_200_OK,
                    )

                serializer = ChainNoteTurnSerializer(current_turn)
                return ApiResponse.success(
                    data=serializer.data,
                    message="Chain Note Turn successfully retrieved",
                    status_code=status.HTTP_200_OK,
                )

            # if user given last_known_turn_id different with current turn return current turn ddata
            elif last_known_turn_id:
                current_turn = (
                    await ChainNoteTurn.objects.aget_current_turn_by_chain_note(
                        chain_note
                    )
                )

                if current_turn is None:
                    return ApiResponse.success(
                        data=self.CHAIN_NOTE_FINISHED_RESPONSE,
                        message="Chain Note has ended",
                        status_code=status.HTTP_200_OK,
                    )

                if current_turn.pk != last_known_turn_id:
                    serializer = ChainNoteTurnSerializer(current_turn)
                    return ApiResponse.success(
                        data=serializer.data,
                        message="Chain Note Turn successfully retrieved",
                        status_code=status.HTTP_200_OK,
                    )

                else:
                    pass

            # wait before looping again
            await asyncio.sleep(poll_interval)

        # longpolling timeout
        raise LongPollingTimeoutException()


class SkipChainNoteTurnView(APIView):
    permission_classes = [IsAuthenticated]

    async def post(self, request, chain_note_pk):

        @sync_to_async
        def _():
            # Check if the user is a participant of the course
            chain_note = ChainNote.objects.select_related("course_session").get(pk=chain_note_pk)
            try:
                course_participant = CourseParticipant.objects.get_by_course_id_and_user_id(chain_note.course_session.course_id, request.user.id)
            except CourseParticipant.DoesNotExist:
                raise PermissionDenied("User is not a participant of this course", "not_participant_of_this_course")


            available_turns = list(
                               ChainNoteTurn
                               .objects
                               .filter_available_turn_by_chain_note(chain_note)
                               .select_related("participant__participant"))

            if len(available_turns) == 0:
                raise ChainNoteTurnHasFinishedException()

            current_turn = available_turns[0]
            # Only the turn owner or instructor can skip the turn
            if current_turn.participant.participant_id != request.user.id and not course_participant.is_teacher:
                raise PermissionDenied("You are not allowed to skip this turn")

            current_turn.is_skipped = True
            compensation_delay = timedelta(seconds=1)
            remaining_time = current_turn.finished_at - timezone.now() + compensation_delay
            for turn in available_turns[1:]:
                turn.started_at -= remaining_time

            ChainNoteTurn.objects.bulk_update(available_turns,
                                              ["is_skipped", "started_at"])

        await _()

        return ApiResponse.success(
            message="Chain Note Turn successfully skipped",
            status_code=status.HTTP_204_NO_CONTENT,
        )






