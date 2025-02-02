# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404

# django
from django.shortcuts import get_list_or_404

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# account_books
from .models import AccountBook
from .serializers import (
    AccountBookListSerializer,
    AccountBookDetailSerializer,
    AccountBookCreateSerializer,
)

# payhere
from payhere.permissions import IsOwner


class AccountBookView(APIView):
    """가계부 생성, 가계부 월간 조회
    
    post: 날짜가 중복되지 않는 가계부를 생성합니다.
    get: url 매개변수로 date(YYYY-MM)를 받으면 월간 가계부 조회합니다.
        return: id, date_at, day_total_money
    """
    permission_classes = [IsAuthenticated]

    date_param_config = openapi.Parameter(
        "date",
        in_=openapi.IN_QUERY,
        description="년 월 입력 (Ex:YYYY-MM)",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(
        request_body=AccountBookCreateSerializer,
        operation_summary="가계부 생성",
        responses={201: "성공", 400: "인풋값 에러", 401: "인증 오류", 500: "서버 에러"},
    )
    def post(self, request):
        serializer = AccountBookCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[date_param_config],
        operation_summary="월간 가계부 조회",
        responses={200: "성공", 400: "매개변수 에러", 401: "인증 오류", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        try:
            date = request.GET.get("date", None).split("-")
            year = date[0]
            month = date[1]
            account_books = get_list_or_404(AccountBook, date_at__year=year, date_at__month=month, owner=request.user.id)
            serializer = AccountBookListSerializer(account_books, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except IndexError:
            return Response({"message": "올바른 매개변수의 날짜를 입력해주세요.(Ex: YYYY-MM)"},status=status.HTTP_400_BAD_REQUEST)


class AccountBookDetailView(APIView):
    """가계부 상세조회, 수정, 삭제
    
    get: 지출/수익내역을 포함하는 일별 가계부 상세 조회합니다.
        return id, date_at, day_total_money, expenses, incomes
    put: 날짜가 중복되지 않는 특정 가계부를 수정합니다.
    delete: 특정 가계부를 삭제합니다.
    """
    permission_classes = [IsOwner]

    def get_objects(self, account_book_id):
        account_book = get_object_or_404(AccountBook, id=account_book_id)
        self.check_object_permissions(self.request, account_book)
        return account_book

    @swagger_auto_schema(
        operation_summary="일별 가게부 상세 조회",
        responses={200: "성공", 403: "권한 오류", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request, account_book_id):
        account_book = self.get_objects(account_book_id)
        serializer = AccountBookDetailSerializer(account_book)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=AccountBookCreateSerializer,
        operation_summary="가계부 수정",
        responses={200: "성공", 400: "인풋값 에러", 403: "권한 오류", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def put(self, request, account_book_id):
        account_book = self.get_objects(account_book_id)
        serializer = AccountBookCreateSerializer(account_book, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="가계부 삭제",
        responses={204: "성공", 403: "권한 오류", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def delete(self, request, account_book_id):
        account_book = self.get_objects(account_book_id)
        account_book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
