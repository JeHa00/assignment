from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import CreateAPIView
from rest_framework import status

from accounts.serializers import UserSerializer
from accounts.models import User


class SignupView(CreateAPIView):
    serializer_class = UserSerializer

    @extend_schema(
        request=UserSerializer,
        responses=UserSerializer,
        summary="회원가입 - username, password, team 소속 정보 필요",
    )
    def post(
        self,
        request,
    ) -> HttpResponse:
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
            HttpResponse: 성공 시, 201을 보내고 실패하면 400 코드를 보낸다.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return HttpResponse(serializer.data, status=status.HTTP_201_CREATED)

        return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
