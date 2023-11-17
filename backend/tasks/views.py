from datetime import datetime

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, exceptions
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView

# Create your views here.
from common.http_exceptions import CommonHttpException
from tasks.serializers import TaskSerializer
from tasks.models import Task


class TaskView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


class MarkAsCompletionView(APIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, pk: int) -> Response:
        selected_task = Task.objects.filter(id=pk).last()

        if not selected_task:
            raise CommonHttpException.TASK_NOT_FOUND_ERROR

        if selected_task.create_user.id != request.user.id:
            raise exceptions.PermissionDenied

        selected_task.completed_at = datetime.now()

        serializer = self.serializer_class(selected_task, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "success to mark as completion"},
            status=status.HTTP_200_OK,
        )


# Task 상세 정보 조회


# Task 전체 목록 조회
