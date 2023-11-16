from django.http import HttpResponse

from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework import status

from accounts.serializers import UserSerializer


class SignupView(CreateAPIView):
    serializer_class = UserSerializer

    @extend_schema(
        request=UserSerializer,
        responses=UserSerializer,
        summary="회원가입 - username, password 정보 필요",
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return HttpResponse(serializer.data, status=status.HTTP_201_CREATED)

        return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
