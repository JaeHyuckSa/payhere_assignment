# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404

# django
from django.shortcuts import get_list_or_404
from django.core.exceptions import ValidationError

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# account_books
from .models import AccountBook
from .serializers import (AccountBookSerializer, AccountBookCreateSerializer)

# payhere
from payhere.permissions import IsOwner


class AccountBookView(APIView):
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
        operation_summary="월별 가계부 조회",
        responses={200: "성공", 400: "매개변수 에러", 401: "인증 오류", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        try:
            date = request.GET.get("date").split('-')
            year = date[0]
            month = date[1]
            account_book = get_list_or_404(AccountBook, date_at__year=year, date_at__month=month, owner=request.user.id)
            serializer = AccountBookSerializer(account_book, many=True)
            account_book_data = {
                "date": f"{year}-{month}",
                "account_book": serializer.data
            }
            return Response(account_book_data, status=status.HTTP_200_OK)
        
        except IndexError:
            return Response({"message":"올바른 매개변수의 날짜를 입력해주세요.(Ex: YYYY-MM)"}, status=status.HTTP_400_BAD_REQUEST)


class AccountBookDateSetView(APIView):
    permission_classes = [IsAuthenticated]
    
    from_param_config = openapi.Parameter(
        "from",
        in_=openapi.IN_QUERY,
        description="년 월 일 입력 (Ex:YYYY-MM-DD)",
        type=openapi.TYPE_STRING,
    )
    
    to_param_config = openapi.Parameter(
        "to",
        in_=openapi.IN_QUERY,
        description="년 월 일 입력 (Ex:YYYY-MM-DD)",
        type=openapi.TYPE_STRING,
    )
    
    @swagger_auto_schema(
        manual_parameters=[from_param_config, to_param_config],
        operation_summary="가계부 날짜 범위 설정",
        responses={200: "성공", 400: "매개변수 에러", 401: "인증 오류", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        try:
            from_date = request.GET.get("from")
            to_date = request.GET.get("to")
            account_book = get_list_or_404(AccountBook, date_at__range=[from_date, to_date], owner=request.user.id)
            serializer = AccountBookSerializer(account_book, many=True)
            account_book_date_range_data = {
                "date_range": f"{from_date} ~ {to_date}",
                "account_book": serializer.data
            }
            return Response(account_book_date_range_data, status=status.HTTP_200_OK)
        
        except ValidationError:
            return Response({"message":"올바른 매개변수의 날짜를 입력해주세요.(Ex: YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)


class AccountBookDetailView(APIView):
    permission_classes = [IsOwner]
    
    def get_objects(self, account_book_id):
        account_book = get_object_or_404(AccountBook, id=account_book_id)
        self.check_object_permissions(self.request, account_book)
        return account_book
    
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