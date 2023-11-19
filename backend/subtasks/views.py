from typing import List

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
        responses=List[SubtaskSerializer],
        summary="하위 업무 목록 조회 - 로그인한 유저의 team에 해당되는 하위 업무들을 조회",
    )
    def get(
        self,
        request,
        *args,
        **kwargs,
    ) -> Response:
        """로그인한 유저의 team에 해당되는 하위 업무들을 조회한다.
        Subtask의 모든 정보가 포함되어 전달된다.
        - id, team, is_completed, completed_at

        Returns:
            Response (200 OK): 직렬화된 Subtask 정보가 list에 담겨져 반환
        """
        return super().get(
            request,
            *args,
            **kwargs,
        )

    def get_queryset(self) -> List[SubTask]:
        """
        Subtask에서 로그인한 유저의 팀에 해당하는 하위 업무들을 조회하여 생성 날짜를 기준으로 내림차순으로 반환
        """
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
        summary="하위 업무 추가 - task 정보와 7개의 팀 중 한 team 정보 필요",
    )
    def post(
        self,
        request,
        *args,
        **kwargs,
    ) -> SubtaskSerializer:
        """주어진 task, team 정보를 바탕으로 하위 업무를 추가한다.

        Args:
            - task_id (int): api path parameter로 전달
            - team (str): 소속 팀
                - DANBIE: "단비"
                - DARAE: "다래"
                - BLABLA: "블라블라"
                - CHEOLLO: "철로"
                - DANGI: "땅이"
                - HAETAE: "해태"
                - SUPI: "수피"

        Raises:
            - HTTPException (404 NOT FOUND): task_id에 해당되는 task를 못 찾을 경우
                - code: TASK_NOT_FOUND_ERROR

        Returns:
            Response (201 CREATED): 새로 생성된 Subtask 정보를 직렬화하여 전달
        """
        selected_task = Task.objects.filter(id=kwargs.get("task_id")).last()
        if not selected_task:
            raise CommonHttpException.TASK_NOT_FOUND_ERROR
        self.selected_task = selected_task
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        생성하려는 하위업무의 상위 업무 Task 정보를 serializer에 전달하여 새로운 Subtask 객체를 생성한다.
        """
        serializer.save(task=self.selected_task)


class SubtaskView(RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated, IsAuthorized]

    def check_and_handle_not_found_error(
        self,
        request: Request,
        pk: int,
    ) -> SubTask:
        """pk에 해당하는 Subtask가 존재하면 조회된 Subtask를 반환하고 없으면 에러를 발생시킨다.

        Args:
            request (Request): Request 정보
            pk (int): Subtask의 pk

        Raises:
            - HTTPException (404 NOT FOUND): pk에 해당되는 subtask를 못 찾을 경우
                - code: SUBTASK_NOT_FOUND_ERROR

        Returns:
            SubTask: 조회된 Subtask 정보 반환
        """
        selected_subtask = SubTask.objects.filter(pk=pk).last()

        if not selected_subtask:
            raise CommonHttpException.SUBTASK_NOT_FOUND_ERROR

        return selected_subtask

    @extend_schema(
        tags=["Subtask"],
        request=SubtaskSerializer,
        responses=SubtaskSerializer,
        summary="특정 하위 업무 조회",
    )
    def get(
        self,
        request: Request,
        pk: int,
        *args,
        **kwargs,
    ) -> SubtaskSerializer:
        """pk에 해당하는 특정 하위 업무 Subtask를 조회한다.

        Args:
            pk (int): Subtask의 pk로 패스 파라미터에 담아 전달한다.

        Raises:
            - HTTPException (404 NOT FOUND): pk에 해당되는 subtask를 못 찾을 경우
                - code: SUBTASK_NOT_FOUND_ERROR

        Returns:
            Response (200 OK): pk에 해당하는 Subtask를 직렬화하여 반환
        """
        self.check_and_handle_not_found_error(request, pk)
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Subtask"],
        request=SubtaskSerializer,
        responses=SubtaskSerializer,
        summary="특정 하위 업무 삭제 - 단, 하위 업무가 완료상태이면 삭제 불가능",
    )
    def delete(
        self,
        request: Request,
        pk: int,
        *args,
        **kwargs,
    ) -> Response:
        """pk에 해당하는 하위 업무를 삭제한다. 단 하위 업무가 완료 상태면 삭제할 수 없다.

        Args:
            pk (int): Subtask의 pk로 패스 파라미터에 담아 전달한다.

        Raises:
            - HTTPException (400 BAD REQUEST): 조회된 하위 업무가 완료된 경우
                - code: COMPLETED_SUBTASK_ERROR
            - HTTPException (403 FORBIDDEN): 삭제 권한이 없는 경우
                - code: permission_denied
            - HTTPException (404 NOT FOUND): pk에 해당되는 subtask를 못 찾을 경우
                - code: SUBTASK_NOT_FOUND_ERROR

        Returns:
            Response (204 NO CONTENT): 성공 메세지 반환
        """
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
        summary="특정 하위 업무 정보 수정",
    )
    def put(
        self,
        request: Request,
        pk: int,
        *args,
        **kwargs,
    ) -> Response:
        """pk에 해당하는 하위 업무를 수정한다.

        Args:
            pk (int): Subtask의 pk로 패스 파라미터에 담아 전달한다.

        Raises:
            - HTTPException (400 BAD REQUEST): 변경하려는 내용이 필수 필드지만 값이 없을 경우
            - HTTPException (403 FORBIDDEN): 수정 권한이 없는 경우
                - code: permission_denied
            - HTTPException (404 NOT FOUND): pk에 해당되는 subtask를 못 찾을 경우
                - code: SUBTASK_NOT_FOUND_ERROR

        Returns:
            Response (200 OK): 수정된 하위업무를 직렬화하여 반환
        """
        self.check_and_handle_not_found_error(request, pk)
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Subtask"],
        request=SubtaskSerializer,
        responses=SubtaskSerializer,
        summary="특정 하위 업무 정보 수정",
    )
    def patch(self, request: Request, pk: int, *args, **kwargs) -> Response:
        """pk에 해당하는 하위 업무를 수정한다.

        Args:
            pk (int): Subtask의 pk로 패스 파라미터에 담아 전달한다.

        Raises:
            - HTTPException (400 BAD REQUEST): 변경하려는 내용이 필수 필드지만 값이 없을 경우
            - HTTPException (403 FORBIDDEN): 수정 권한이 없는 경우
                - code: permission_denied
            - HTTPException (404 NOT FOUND): pk에 해당되는 subtask를 못 찾을 경우
                - code: SUBTASK_NOT_FOUND_ERROR

        Returns:
            Response (200 OK): 수정된 하위업무를 직렬화하여 반환
        """
        self.check_and_handle_not_found_error(request, pk)
        return super().patch(request, *args, **kwargs)


class MarkAsCompletionView(APIView):
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Subtask"],
        request=SubtaskSerializer,
        responses=SubtaskSerializer,
        summary="완료표시 - 주어진 정보에 해당하는 하위 업무를 완료 상태로 변경",
    )
    def patch(self, request: Request, pk: int) -> Response:
        """pk 정보에 해당되는 하위 업무(Subtask)의 완료 유무 상태(is_completed)를 완료 상태로 변경한다.

        Args:
            pk (int): Subtask의 pk로 패스 파라미터에 담아 전달한다.

        Raises:
            - HTTPException (404 NOT FOUND): pk에 해당되는 subtask를 못 찾을 경우
                - code: SUBTASK_NOT_FOUND_ERROR
            - HTTPException (403 FORBIDDEN): 수정 권한이 없는 경우
                - code: permission_denied

        Returns:
            Response (200 OK): 성공 메세지 반환
        """
        selected_subtask = SubTask.objects.filter(id=pk).last()

        if not selected_subtask:
            raise CommonHttpException.SUBTASK_NOT_FOUND_ERROR

        if selected_subtask.team != request.user.team:
            raise exceptions.PermissionDenied

        initial_data = {
            MarkAsCompletion.is_completed: True,
            MarkAsCompletion.completed_at: timezone.localtime(timezone.now()),
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
