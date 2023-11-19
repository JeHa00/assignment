from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema
from django.contrib.auth.hashers import check_password
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from common.http_exceptions import CommonHttpException, WrongPasswordError
from accounts.serializers import (
    SignupSerializer,
    LoginSerializer,
    UserSerializer,
)
from accounts.enums import UserInformation, TokenInformation
from accounts.models import User


class SignupView(CreateAPIView):
    serializer_class = SignupSerializer

    @extend_schema(
        tags=["Account"],
        request=SignupSerializer,
        responses=SignupSerializer,
        summary="회원가입 - username, password, team 소속 정보 필요",
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        """username, password, team 소속 정보를 입력하여 회원가입을 한다.


        Args:

            - username (str): 로그인 시 입력할 이름
            - password (str): 로그인 시 입력할 비밀번호
            - team (str): 소속 팀
                - DANBIE: "단비"
                - DARAE: "다래"
                - BLABLA: "블라블라"
                - CHEOLLO: "철로"
                - DANGI: "땅이"
                - HAETAE: "해태"
                - SUPI: "수피"

        Returns:

            - Response: 성공 시 201 CREATED를 보내고 실패하면 400 BAD_REQUEST 를 보낸다.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @extend_schema(
        tags=["Account"],
        request=LoginSerializer,
        responses=LoginSerializer,
        summary="로그인 - username, password로 로그인하여 user data, token 정보를 반환",
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        """username과 password로 로그인하여 다음 정보들을 받는다.
            - id, username
            - token 정보
            - 성공 메세지

        Args:

            - username (str): 로그인 시 입력할 이름
            - password (str): 로그인 시 입력할 비밀번호

        Raises:

            - HTTPException (404 NOT FOUND): username에 해당하는 user를 찾지 못한 경우
                - code: USER_NOT_FOUND

            - HTTPException (400 BAD REQUEST): username에 해당하는 비밀번호가 아닌 경우
                - code: WRONG_PASSWORD_ERROR

        Returns:

            - Response (200 OK): 다음 정보를 반환
                - user_data: id, username
                - token information: access, refresh token
                - message: LOGIN_SUCCESS
        """
        username = request.data.get(UserInformation.username)
        password = request.data.get(UserInformation.password)

        user = User.objects.filter(username=username).last()

        if user is None:
            raise CommonHttpException.USER_NOT_FOUND_ERROR

        if not check_password(password, user.password):
            raise WrongPasswordError

        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        user_data = {
            UserInformation.user_id: user.id,
            UserInformation.username: LoginSerializer(user).data.get(
                UserInformation.username,
            ),
        }

        response = Response(
            {
                "user_data": user_data,
                "message": "LOGIN_SUCCESS",
                TokenInformation.token: {
                    TokenInformation.access_token: access_token,
                    TokenInformation.refresh_token: refresh_token,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            TokenInformation.access_token,
            access_token,
            httponly=True,
        )
        response.set_cookie(
            TokenInformation.refresh_token,
            refresh_token,
            httponly=True,
        )
        return response


class LogoutView(APIView):
    @extend_schema(
        tags=["Account"],
        request=UserSerializer,
        responses=UserSerializer,
        summary="로그아웃 - 토큰 정보 삭제",
    )
    def delete(self, request: Request) -> Response:
        """로그아웃 하여 인증 정보인 토큰을 삭제합니다.

        Returns:

            Response (202 ACCEPTED): 로그아웃 처리가 성공하면 202 accepted를 반환
        """
        response = Response(
            {"message": "LOGOUT_SUCCESS"},
            status=status.HTTP_202_ACCEPTED,
        )
        response.delete_cookie(TokenInformation.access_token)
        response.delete_cookie(TokenInformation.refresh_token)
        return response
