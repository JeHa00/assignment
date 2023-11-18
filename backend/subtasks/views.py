from datetime import datetime

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.views import APIView
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
    ListAPIView,
)

from common.http_exceptions import CommonHttpException, CompletedSubtaskError
from common.enums import MarkAsCompletion
from common.permissions import IsAuthorized
from tasks.models import Task
from subtasks.serializers import SubtaskSerializer
from subtasks.models import SubTask


class SubTaskListView(ListAPIView):
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Subtask"],
        request=SubtaskSerializer,
        responses=SubtaskSerializer,
        summary="Subtask 객체 목록 조회",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            SubTask.objects.filter(team=self.request.user.team)
            .order_by("-created_at")
            .all()
        )


class SubtaskCreateView(CreateAPIView):
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]
    selected_task = None

    @extend_schema(
        tags=["Subtask"],
        request=SubtaskSerializer,
        responses=SubtaskSerializer,
        summary="새로운 Subtask 객체 생성",
    )
    def post(self, request, *args, **kwargs):
        selected_task = Task.objects.filter(id=kwargs.get("task_id")).last()
        if not selected_task:
            raise CommonHttpException.TASK_NOT_FOUND_ERROR
        self.selected_task = selected_task
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(task=self.selected_task)


class SubtaskView(RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated, IsAuthorized]

    def check_and_handle_not_found_error(self, request: Request, pk: int,):
        selected_subtask = SubTask.objects.filter(pk=pk).last()

        if not selected_subtask:
            raise CommonHttpException.SUBTASK_NOT_FOUND_ERROR

        return selected_subtask

    @extend_schema(
        tags=["Subtask"],
        request=SubtaskSerializer,
        responses=SubtaskSerializer,
        summary="특정 Subtask 객체 조회",
    )
    def get(self, request: Request, pk: int, *args, **kwargs):
        self.check_and_handle_not_found_error(request, pk)
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Subtask"],
        request=SubtaskSerializer,
        responses=SubtaskSerializer,
        summary="특정 Subtask 삭제",
    )
    def delete(self, request: Request, pk: int, *args, **kwargs):
        self.check_and_handle_not_found_error(request, pk)
        return super().delete(request, pk, *args, **kwargs)

    def perform_destroy(self, instance: SubTask):
        if instance.is_completed:
            raise CompletedSubtaskError
        return instance.delete()

    @extend_schema(
        tags=["Subtask"],
        request=SubtaskSerializer,
        responses=SubtaskSerializer,
        summary="특정 Subtask 정보 수정",
    )
    def put(self, request: Request, pk: int, *args, **kwargs):
        self.check_and_handle_not_found_error(request, pk)
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Subtask"],
        request=SubtaskSerializer,
        responses=SubtaskSerializer,
        summary="특정 Subtask 정보 수정",
    )
    def patch(self, request: Request, pk: int, *args, **kwargs):
        self.check_and_handle_not_found_error(request, pk)
        return super().patch(request, *args, **kwargs)


class MarkAsCompletionView(APIView):
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Subtask"],
        request=SubtaskSerializer,
        responses=SubtaskSerializer,
        summary="완료표시 - 해당 Subtask 객체를 완료 상태로 변경",
    )
    def patch(self, request: Request, pk: int) -> Response:
        selected_subtask = SubTask.objects.filter(id=pk).last()

        if not selected_subtask:
            raise CommonHttpException.SUBTASK_NOT_FOUND_ERROR

        if selected_subtask.team != request.user.team:
            raise exceptions.PermissionDenied

        initial_data = {
            MarkAsCompletion.is_completed: True,
            MarkAsCompletion.completed_at: datetime.now(),
        }

        serializer = self.serializer_class(
            selected_subtask,
            data=initial_data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "success to mark as completion"},
            status=status.HTTP_200_OK,
        )
