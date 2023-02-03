# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

# django
from django.db import IntegrityError
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_list_or_404 

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# expenses
from .models import Expense, ExpenseURL, ExpenseCategory
from .serializers import (
    ExpenseListSerializer,  
    ExpenseDetailSerializer,
    ExpenseCreateSerializer,
    ExpenseCategorySerializer,
    ExpenseSearchListSerializer,
    ExpenseShareUrlSerializer,
)
from .utils import ExpenseCalcUtil, ExpenseUrlUtil

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
        operation_summary="해당 일자 지출 리스트 조회",
        responses={200: "성공", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        date = request.GET.get("date", None)
        expense = self.get_objects(date)
        serializer = ExpenseListSerializer(expense, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
            ExpenseCalcUtil.sub_total_money_expense(account_book, int(request.data["money"]))
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
        serializer = ExpenseDetailSerializer(expense)
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
        try:
            expense = self.get_objects(expense_id)
            expense_money = expense.money
            serializer = ExpenseCreateSerializer(expense, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                ExpenseCalcUtil.mix_total_money_expense(expense.account_book, expense_money, int(request.data["money"]))
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        except KeyError:
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="특정 지출 삭제",
        responses={204: "성공", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def delete(self, request, expense_id):
        expense = self.get_objects(expense_id)
        ExpenseCalcUtil.add_total_money_expense(expense.account_book, expense.money)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseCategoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="지출 카테고리 리스트 조회",
        responses={201: "성공", 401: "인증 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, reuqest):
        category_data = {}
        for i in range(1, 15):
            main_category = get_object_or_404(ExpenseCategory, id=i)
            sub_category = main_category.get_descendants(include_self=False)
            sub_category_serializer = ExpenseCategorySerializer(sub_category, many=True)
            category_data[f"({i}) {main_category.name}"] = sub_category_serializer.data
        return Response(category_data, status=status.HTTP_200_OK)


class ExpenseCategorySearchView(APIView):
    permission_classes = [IsAuthenticated]
    
    date_param_config = openapi.Parameter(
        "date",
        in_=openapi.IN_QUERY,
        description="년 월 입력 (Ex:YYYY-MM)",
        type=openapi.TYPE_STRING,
    )

    main_param_config = openapi.Parameter(
        "main",
        in_=openapi.IN_QUERY,
        description="메인 카테고리 입력",
        type=openapi.TYPE_STRING,
    )
    
    sub_param_config = openapi.Parameter(
        "sub",
        in_=openapi.IN_QUERY,
        description="서브 카테고리 입력",
        type=openapi.TYPE_STRING,
    )
    
    @swagger_auto_schema(
        manual_parameters=[date_param_config, main_param_config, sub_param_config],
        operation_summary="지출 카테고리 검색 조회",
        responses={200: "성공", 400: "매개변수 에러", 401: "인증 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        try:
            date = request.GET.get("date", None).split('-')
            main = request.GET.get("main", None)
            sub = request.GET.get("sub", None)
            year = date[0]
            month = date[1]
            
            if main or sub:
                expense = Expense.objects.select_related('account_book').select_related("category").filter \
                (account_book__in=AccountBook.objects.filter(date_at__year=year, date_at__month=month, owner=request.user),
                category__in=get_list_or_404(ExpenseCategory, Q(name=main) | Q(name=sub)))
                serializer = ExpenseSearchListSerializer(expense, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            expense = Expense.objects.select_related('account_book').filter \
            (account_book__in=AccountBook.objects.filter(date_at__year=year, date_at__month=month, owner=request.user))
            serializer = ExpenseSearchListSerializer(expense, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except IndexError:
            return Response({"message":"올바른 매개변수의 날짜를 입력해주세요.(Ex: YYYY-MM)"}, status=status.HTTP_400_BAD_REQUEST)


class ExpenseShareUrlCreateView(APIView):
    permission_classes = [IsOwner]
    
    def get_objects(self, expense_id):
        expense = get_object_or_404(Expense, id=expense_id)
        self.check_object_permissions(self.request, expense)
        return expense
    
    @swagger_auto_schema(
        operation_summary="특정 지출 공유 단축 URL 생성",
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
    permission_classes = [IsAuthenticated]
    
    encode_key_param_config = openapi.Parameter(
        "encode_key",
        in_=openapi.IN_QUERY,
        description="단축 URL 고유 키",
        type=openapi.TYPE_STRING,
    )
    
    @swagger_auto_schema(
        manual_parameters=[encode_key_param_config],
        operation_summary="특정 지출 공유 단축 URL 조회",
        responses={200: "성공", 400: "시간 만료", 401: "인증 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        encode_key = request.GET.get("key", None)
        expense_id = ExpenseUrlUtil.get_expense_id(encode_key)
        expense_url = get_object_or_404(ExpenseURL, expense_id=expense_id)
        if expense_url.expired_at < timezone.now():
            return Response({"message":"만료된 URL 입니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ExpenseShareUrlSerializer(expense_url.expense)
        return Response(serializer.data, status=status.HTTP_200_OK)