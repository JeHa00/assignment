from datetime import datetime

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

# Create your views here.
from common.http_exceptions import CommonHttpException
from tasks.serializers import TaskSerializer
from common.enums import MarkAsCompletion
from tasks.models import Task


class TaskListCreateView(ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    # ModelClass = self.Meta.model
    # instance = ModelClass._default_manager.create(**validated_data)

    def check_resource_and_authorization(
        self,
        request: Request,
        pk: int,
        *args,
        **kwargs,
    ):
        selected_task = Task.objects.filter(pk=pk).last()

        if not selected_task:
            raise CommonHttpException.TASK_NOT_FOUND_ERROR

        if selected_task.create_user.id != request.user.id:
            raise exceptions.PermissionDenied

        return selected_task

    def retrieve(self, request: Request, pk: int, *args, **kwargs):
        self.check_resource_and_authorization(request, pk)
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request: Request, pk: int, *args, **kwargs):
        selected_task = self.check_resource_and_authorization(
            request, pk, *args, **kwargs
        )

        selected_task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request: Request, pk: int, *args, **kwargs):
        self.check_resource_and_authorization(request, pk)
        return super().put(request, *args, **kwargs)


class MarkAsCompletionView(APIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, pk: int) -> Response:
        selected_task = Task.objects.filter(id=pk).last()

        if not selected_task:
            raise CommonHttpException.TASK_NOT_FOUND_ERROR

        if selected_task.create_user.id != request.user.id:
            raise exceptions.PermissionDenied

        initial_data = {
            MarkAsCompletion.is_completed: True,
            MarkAsCompletion.completed_at: datetime.now(),
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
