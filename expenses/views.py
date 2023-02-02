# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny

# django
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# expenses
from .models import Expense, ExpenseURL
from .serializers import ExpenseCreateSerializer, ExpenseSerializer, ExpenseShareUrlSerializer
from .utils import ExpenseUrlUtil, ExpenseCalcUtil


# account_books
from account_books.models import AccountBook

# payhere
from payhere.permissions import IsOwner


class ExpenseListView(APIView):
    permission_classes = [IsOwner]
    
    date_param_config = openapi.Parameter(
        "date",
        in_=openapi.IN_QUERY,
        description="년 월 일 입력 (Ex:YYYY-MM-DD)",
        type=openapi.TYPE_STRING,
    )
    
    def get_objects(self, date):
        account_book = get_object_or_404(AccountBook, date_at=date)
        self.check_object_permissions(self.request, account_book)
        expense = account_book.expenses
        return expense
    
    @swagger_auto_schema(
        manual_parameters=[date_param_config],
        operation_summary="해당 일자 지출 조회",
        responses={200: "성공", 400: "매개변수 에러", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        try:
            date = request.GET.get("date")
            expense = self.get_objects(date)
            serializer = ExpenseSerializer(expense, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ValidationError:
            return Response({"message":"올바른 매개변수의 날짜를 입력해주세요.(Ex: YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)


class ExpenseCreateView(APIView):
    permission_classes = [IsOwner]
    
    def get_objects(self, account_book_id):
        account_book = get_object_or_404(AccountBook, id=account_book_id)
        self.check_object_permissions(self.request, account_book)
        return account_book
    
    @swagger_auto_schema(
        request_body=ExpenseCreateSerializer,
        operation_summary="해당 일자 지출 생성",
        responses={201: "성공", 400: "인풋값 에러", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def post(self, request, account_book_id):
        account_book = self.get_objects(account_book_id)
        serializer = ExpenseCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user, account_book=account_book)
            ExpenseCalcUtil.sub_total_money_expense(account_book, request.data["money"])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDetailView(APIView):
    permission_classes = [IsOwner]
    
    def get_objects(self, expense_id):
        expense = get_object_or_404(Expense, id=expense_id)
        self.check_object_permissions(self.request, expense)
        return expense
    
    @swagger_auto_schema(
        operation_summary="특정 지출 조회",
        responses={200: "성공", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request, expense_id):
        expense = self.get_objects(expense_id)
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="특정 지출 복제",
        responses={200: "성공", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def post(self, reuqest, expense_id):
        expense = self.get_objects(expense_id)
        expense.id = None
        expense.save()
        ExpenseCalcUtil.sub_total_money_expense(expense.account_book, expense.money)
        return Response({"message":"복사 완료"}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=ExpenseCreateSerializer,
        operation_summary="특정 지출 수정",
        responses={200: "성공", 400: "인풋값 에러", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def put(self, request, expense_id):
        expense = self.get_objects(expense_id)
        serializer = ExpenseCreateSerializer(expense, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            ExpenseCalcUtil.mix_total_money_expense(expense.account_book, expense.money, request.data["money"])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="특정 지출 삭제",
        responses={204: "성공", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def delete(self, request, expense_id):
        expense = self.get_objects(expense_id)
        ExpenseCalcUtil.add_total_money_expense(expense.account_book, expense.money)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseShareUrlCreateView(APIView):
    permission_classes = [IsOwner]
    
    def get_objects(self, expense_id):
        expense = get_object_or_404(Expense, id=expense_id)
        self.check_object_permissions(self.request, expense)
        return expense
    
    @swagger_auto_schema(
        operation_summary="특정 지출 공유 URL 생성",
        responses={201: "성공", 208: "자원 존재함", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def post(self, request, expense_id):
        try:
            expense = self.get_objects(expense_id)
            shared_url = ExpenseUrlUtil.get_expense_link(request, expense)
            expired_at = ExpenseUrlUtil.get_expense_link_expired_at(expense)
            ExpenseURL.objects.create(shared_url=shared_url, expired_at=expired_at, expense_id=expense.id)            
            return Response({"단축 URL(1일 제한)":shared_url}, status=status.HTTP_201_CREATED)
    
        except IntegrityError:
            return Response({"message":"해당 지출 내역의 공유 링크가 존재합니다. "}, status=status.HTTP_208_ALREADY_REPORTED)


class ExpenseShareUrlView(APIView):
    permission_classes = [AllowAny]
    
    encode_key_param_config = openapi.Parameter(
        "encode_key",
        in_=openapi.IN_QUERY,
        description="단축 URL 고유 키",
        type=openapi.TYPE_STRING,
    )
        
    @swagger_auto_schema(
        manual_parameters=[encode_key_param_config],
        operation_summary="특정 지출 공유 URL 조회",
        responses={201: "성공", 208: "자원 존재함", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        encode_key = request.GET.get("key")
        expense_id = ExpenseUrlUtil.get_expense_id(encode_key)
        expense_url = get_object_or_404(ExpenseURL, expense_id=expense_id)
        if expense_url.expired_at < timezone.now():
            return Response({"message":"만료된 URL 입니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ExpenseShareUrlSerializer(expense_url.expense)
        return Response(serializer.data, status=status.HTTP_200_OK)