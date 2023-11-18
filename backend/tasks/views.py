from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.views import APIView
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView,
)
from django.utils import timezone

from common.http_exceptions import CommonHttpException
from common.enums import MarkAsCompletion
from common.permissions import IsAuthorized
from tasks.serializers import TaskSerializer
from tasks.models import Task


class TaskListCreateView(ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Task"],
        request=TaskSerializer,
        responses=TaskSerializer,
        summary="새로운 Task 객체 생성",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @extend_schema(
        tags=["Task"],
        request=TaskSerializer,
        responses=TaskSerializer,
        summary="Task 객체 목록 조회",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(create_user=self.request.user)
        return super().perform_create(serializer)

    def get_queryset(self):
        return (
            Task.objects.filter(create_user=self.request.user)
            .order_by("-created_at")
            .all()
        )


class TaskView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAuthorized]

    def check_and_handle_not_found_error(
        self,
        request: Request,
        pk: int,
    ):
        selected_task = Task.objects.filter(pk=pk).last()

        if not selected_task:
            raise CommonHttpException.TASK_NOT_FOUND_ERROR

        return selected_task

    @extend_schema(
        tags=["Task"],
        request=TaskSerializer,
        responses=TaskSerializer,
        summary="특정 Task 객체 조회",
    )
    def get(self, request: Request, pk: int, *args, **kwargs):
        self.check_and_handle_not_found_error(request, pk)
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Task"],
        request=TaskSerializer,
        responses=TaskSerializer,
        summary="특정 Task 객체 삭제",
    )
    def delete(self, request: Request, pk: int, *args, **kwargs):
        self.check_and_handle_not_found_error(request, pk)
        return super().delete(request, pk, *args, **kwargs)

    @extend_schema(
        tags=["Task"],
        request=TaskSerializer,
        responses=TaskSerializer,
        summary="특정 Task 객체 정보 수정",
    )
    def put(self, request: Request, pk: int, *args, **kwargs):
        self.check_and_handle_not_found_error(request, pk)
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Task"],
        request=TaskSerializer,
        responses=TaskSerializer,
        summary="특정 Task 객체 정보 수정",
    )
    def patch(self, request: Request, pk: int, *args, **kwargs):
        self.check_and_handle_not_found_error(request, pk)
        return super().patch(request, *args, **kwargs)


class MarkAsCompletionView(APIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Task"],
        request=TaskSerializer,
        responses=TaskSerializer,
        summary="완료표시 - 해당 Task 객체를 완료 상태로 변경",
    )
    def patch(self, request: Request, pk: int) -> Response:
        selected_task = Task.objects.filter(id=pk).last()

        if not selected_task:
            raise CommonHttpException.TASK_NOT_FOUND_ERROR

        if selected_task.create_user.id != request.user.id:
            raise exceptions.PermissionDenied

        initial_data = {
            MarkAsCompletion.is_completed: True,
            MarkAsCompletion.completed_at: timezone.localtime(timezone.now()),
        }

        serializer = self.serializer_class(
            selected_task,
            data=initial_data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "success to mark as completion"},
            status=status.HTTP_200_OK,
        )
