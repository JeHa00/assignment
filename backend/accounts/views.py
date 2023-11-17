from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema
from django.contrib.auth.hashers import check_password
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from common.http_exceptions import CommonHttpException, WRONG_PASSWORD
from accounts.serializers import SignupSerializer, LoginSerializer, UserSerializer
from accounts.models import User


class SignupView(CreateAPIView):
    serializer_class = SignupSerializer

    @extend_schema(
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
            username (str): 로그인 시 입력할 이름
            password (str): 로그인 시 입력할 비밀번호
            team (User.TeamChoices): 소속 팀
                - DANBIE: "단비"
                - DARAE: "다래"
                - BLABLA: "블라블라"
                - CHEOLLO: "철로"
                - DANGI: "땅이"
                - HAETAE: "해태"
                - SUPI: "수피"

        Returns:
            Response: 성공 시, 201을 보내고 실패하면 400 코드를 보낸다.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @extend_schema(
        request=LoginSerializer,
        responses=LoginSerializer,
        summary="로그인 - username, password 정보 필요",
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        username = request.data.get("username")
        password = request.data.get("password")

        user = User.objects.filter(username=username).last()

        if user is None:
            raise CommonHttpException.USER_NOT_FOUND_ERROR

        if not check_password(password, user.password):
            raise WRONG_PASSWORD

        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        user_data = {
            "user_id": user.id,
            "username": LoginSerializer(user).data.get("username"),
        }

        response = Response(
            {
                "user_data": user_data,
                "message": "LOGIN_SUCCESS",
                "token_information": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie("access_token", access_token, httponly=True)
        response.set_cookie("refresh_token", refresh_token, httponly=True)
        return response


class LogoutView(APIView):
    @extend_schema(
        request=UserSerializer,
        responses=UserSerializer,
        summary="로그아웃: 토큰 정보 삭제",
    )
    def delete(self, request: Request) -> Response:
        response = Response(
            {"message": "logout success"},
            status=status.HTTP_202_ACCEPTED,
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
