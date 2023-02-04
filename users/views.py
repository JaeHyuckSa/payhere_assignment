# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

# rest_framework_simplejwt
from rest_framework_simplejwt.views import TokenObtainPairView

# drf_yasg
from drf_yasg.utils import swagger_auto_schema

# users
from .serializers import (
    CustomTokenObtainPairSerializer,
    SignupSerializer,
    SignoutSerializer,
)


class SingupView(APIView):
    """회원가입
    
    nickname, email, password, repassword을 받습니다.
    
    <유효성검사>
    nickname: 3 ~ 10자, 특수문자 포함 x, 중복검사
    password: 8 ~ 16자, 소문자, 숫자, 특수문자 포함
    repassword: password와 일치 확인
    email: 이메일 형식, 중복검사
    """
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
    """로그인
    
    token value:
    user_id, nickname, email
    """
    serializer_class = CustomTokenObtainPairSerializer


class SignoutView(APIView):
    """로그아웃
    
    refresh 토큰을 받으며 재사용 방지하는 blacklist에 저장됩니다.
    """

    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=SignoutSerializer,
        operation_summary="로그아웃",
        responses={200: "성공", 400: "토큰 유효하지 않음", 401: "인증 에러", 500: "서버 에러"},
    )
    def post(self, request):
        serializer = SignoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "로그아웃이 되었습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
