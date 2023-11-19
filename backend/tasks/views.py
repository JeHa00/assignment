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
from django.utils import timezone
from django.db.models import Q

from common.http_exceptions import CommonHttpException
from common.enums import MarkAsCompletion
from common.permissions import IsAuthorized
from tasks.serializers import TaskSerializer, TaskDetailSerializer
from tasks.models import Task


class TaskListView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    user_team = None

    @extend_schema(
        tags=["Task"],
        request=TaskSerializer,
        responses=TaskSerializer,
        summary="업무 목록 조회 - 유저의 소속 팀에 해당되는 업무와 그 업무의 하위 업무 정보들을 조회한다.",
    )
    def get(self, request, *args, **kwargs) -> TaskSerializer:
        """로그인한 유저의 team에 해당되는 업무와 하위 업무들을 조회한다.
        하위 업무 정보에는 id, 완료 유무, 완료 날짜, 팀 정보가 포함된다.

        Returns:

            - Response (200 OK): 해당 task를 생성한 유저 정보, team에 속한 하위 업무, 업무를 전달
        """
        self.user_team = request.user.team
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Task.objects.prefetch_related("subtasks").filter(
            Q(team=self.user_team) | Q(subtasks__team=self.user_team),
        )


class TaskCreateView(CreateAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Task"],
        request=TaskDetailSerializer,
        responses=TaskDetailSerializer,
        summary="업무 추가",
    )
    def post(
        self,
        request,
        *args,
        **kwargs,
    ) -> Response:
        """주어진 정보를 바탕으로 업무를 추가한다.

        Args:

            - title (str): 업무 제목

            - content (str): 업무 내용

            - team (str): 소속 팀
                - DANBIE: "단비"
                - DARAE: "다래"
                - BLABLA: "블라블라"
                - CHEOLLO: "철로"
                - DANGI: "땅이"
                - HAETAE: "해태"
                - SUPI: "수피"

        Returns:

            - Response (201 CREATED): 새로 생성된 Task 정보를 직렬화하여 전달
        """
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(create_user=self.request.user)


class TaskView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated, IsAuthorized]

    def check_and_handle_not_found_error(
        self,
        request: Request,
        pk: int,
    ) -> Task:
        """pk에 해당하는 하위 업무(Task)가 존재하면 조회된 업무를 반환하고 없으면 에러를 발생시킨다.

        Args:

            - request (Request): Request 정보

            - pk (int): Task의 pk

        Raises:

            - HTTPException (404 NOT FOUND): pk에 해당되는 task를 못 찾을 경우
                - code: TASK_NOT_FOUND_ERROR

        Returns:

            - Task: 조회된 Task 정보 반환
        """
        selected_task = Task.objects.filter(pk=pk).last()

        if not selected_task:
            raise CommonHttpException.TASK_NOT_FOUND_ERROR

        return selected_task

    @extend_schema(
        tags=["Task"],
        request=TaskDetailSerializer,
        responses=TaskDetailSerializer,
        summary="특정 업무 조회",
    )
    def get(
        self,
        request: Request,
        pk: int,
        *args,
        **kwargs,
    ) -> TaskDetailSerializer:
        """pk에 해당하는 특정 업무(Task)를 조회한다.

        Args:

            - pk (int): Task의 pk로 패스 파라미터에 담아 전달한다.

        Raises:

            - HTTPException (404 NOT FOUND): pk에 해당되는 task를 못 찾을 경우
                - code: TASK_NOT_FOUND_ERROR

        Returns:

            - Response (200 OK): pk에 해당하는 task를 직렬화하여 반환
        """
        self.check_and_handle_not_found_error(request, pk)
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Task"],
        request=TaskDetailSerializer,
        responses=TaskDetailSerializer,
        summary="특정 업무 삭제",
    )
    def delete(
        self,
        request: Request,
        pk: int,
        *args,
        **kwargs,
    ) -> Response:
        """pk에 해당하는 업무를 삭제한다.

        Args:

            - pk (int): Task의 pk

        Raises:

            - HTTPException (403 FORBIDDEN): 삭제 권한이 없는 경우
                - code: permission_denied

            - HTTPException (404 NOT FOUND): pk에 해당되는 업무(Task)를 못 찾을 경우
                - code: TASK_NOT_FOUND_ERROR

        Returns:

            - Response (204 NO CONTENT): 성공 메세지 반환
        """
        self.check_and_handle_not_found_error(request, pk)
        return super().delete(request, pk, *args, **kwargs)

    @extend_schema(
        tags=["Task"],
        request=TaskDetailSerializer,
        responses=TaskDetailSerializer,
        summary="특정 업무 정보 수정",
    )
    def put(
        self,
        request: Request,
        pk: int,
        *args,
        **kwargs,
    ) -> Response:
        """pk에 해당하는 업무를 수정한다.

        Args:

            - pk (int): Task의 pk

        Raises:

            - HTTPException (400 BAD REQUEST): 변경하려는 내용이 필수 필드지만 값이 없을 경우

            - HTTPException (403 FORBIDDEN): 수정 권한이 없는 경우
                - code: permission_denied

            - HTTPException (404 NOT FOUND): pk에 해당되는 task를 못 찾을 경우
                - code: TASK_NOT_FOUND_ERROR

        Returns:

            - Response (200 OK): 수정된 업무를 직렬화하여 반환
        """
        self.check_and_handle_not_found_error(request, pk)
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Task"],
        request=TaskDetailSerializer,
        responses=TaskDetailSerializer,
        summary="특정 업무 정보 수정",
    )
    def patch(
        self,
        request: Request,
        pk: int,
        *args,
        **kwargs,
    ) -> Response:
        """pk에 해당하는 업무를 수정한다.

        Args:

            - pk (int): Task의 pk로 패스 파라미터에 담아 전달한다.

        Raises:

            - HTTPException (400 BAD REQUEST): 변경하려는 내용이 필수 필드지만 값이 없을 경우

            - HTTPException (403 FORBIDDEN): 수정 권한이 없는 경우
                - code: permission_denied

            - HTTPException (404 NOT FOUND): pk에 해당되는 task를 못 찾을 경우
                - code: TASK_NOT_FOUND_ERROR

        Returns:

            - Response (200 OK): 수정된 업무를 직렬화하여 반환
        """
        self.check_and_handle_not_found_error(request, pk)
        return super().patch(request, *args, **kwargs)


class MarkAsCompletionView(APIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Task"],
        request=TaskDetailSerializer,
        responses=TaskDetailSerializer,
        summary="완료표시 - 해당 Task 객체를 완료 상태로 변경",
    )
    def patch(self, request: Request, pk: int) -> Response:
        """pk 정보에 해당되는 Task의 완료 유무 상태(is_completed)를 완료 상태로 변경한다.
        직접 완료처리를 하는 것 외에도 하위 업무 모두가 완료처리 되면 업무도 완료처리 된다.

        Args:

            - pk (int): Task의 pk로 패스 파라미터에 담아 전달한다.

        Raises:

            - HTTPException (404 NOT FOUND): pk에 해당되는 task를 못 찾을 경우
                - code: TASK_NOT_FOUND_ERROR

            - HTTPException (403 FORBIDDEN): 수정 권한이 없는 경우
                - code: permission_denied

        Returns:

            - Response (200 OK): 성공 메세지 반환
        """
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
