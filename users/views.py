# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import  AllowAny

# rest_framework_simplejwt
from rest_framework_simplejwt.views import TokenObtainPairView

# drf_yasg
from drf_yasg.utils import swagger_auto_schema

# users
from .serializers import (
    CustomTokenObtainPairSerializer,
    SignupSerializer,
)


class SingupView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=SignupSerializer,
        operation_summary="회원가입",
        responses={201: "성공", 400: "인풋값 에러", 500: "서버 에러"},
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입이 되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
