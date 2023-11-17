from rest_framework import exceptions, status


class CommonHttpException:
    USER_NOT_FOUND_ERROR = exceptions.NotFound(
        detail="해당되는 유저를 찾을 수 없습니다.",
        code="USER_NOT_FOUND",
    )

    TASK_NOT_FOUND_ERROR = exceptions.NotFound(
        detail="해당되는 업무를 찾을 수 없습니다.",
        code="TASK_NOT_FOUND",
    )

    SUBTASK_NOT_FOUND_ERROR = exceptions.NotFound(
        detail="해당되는 하위 업무를 찾을 수 없습니다.",
        code="SUBTASK_NOT_FOUND",
    )


class WRONG_PASSWORD(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "입력한 비밀번호가 기존 비밀번호와 일치하지 않습니다."
    default_code = "WRONG_PASSWORD"
