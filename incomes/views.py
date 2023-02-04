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

# incomes
from .models import Income, IncomeURL, IncomeCategory
from .serializers import (
    IncomeListSerializer,  
    IncomeDetailSerializer,
    IncomeCreateSerializer,
    IncomeCategorySerializer,
    IncomeSearchListSerializer,
    IncomeShareUrlSerializer
)
from .utils import IncomeCalcUtil, IncomeUrlUtil

# account_books
from account_books.models import AccountBook

# payhere
from payhere.permissions import IsOwner

class IncomeListView(APIView):
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
        income = account_book.incomes
        return income
    
    @swagger_auto_schema(
        manual_parameters=[date_param_config],
        operation_summary="해당 일자 수익 리스트 조회",
        responses={200: "성공", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        date = request.GET.get("date", None)
        income = self.get_objects(date)
        serializer = IncomeListSerializer(income, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IncomeCreateView(APIView):
    permission_classes = [IsOwner]
    
    def get_objects(self, account_book_id):
        account_book = get_object_or_404(AccountBook, id=account_book_id)
        self.check_object_permissions(self.request, account_book)
        return account_book
    
    @swagger_auto_schema(
        request_body=IncomeCreateSerializer,
        operation_summary="해당 일자 수익 생성",
        responses={201: "성공", 400: "인풋값 에러", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def post(self, request, account_book_id):
        account_book = self.get_objects(account_book_id)
        serializer = IncomeCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user, account_book=account_book)
            IncomeCalcUtil.add_total_money_income(account_book, int(request.data["money"]))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IncomeDetailView(APIView):
    permission_classes = [IsOwner]
    
    def get_objects(self, income_id):
        income = get_object_or_404(Income, id=income_id)
        self.check_object_permissions(self.request, income)
        return income
    
    @swagger_auto_schema(
        operation_summary="특정 수익 조회",
        responses={200: "성공", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request, income_id):
        income = self.get_objects(income_id)
        serializer = IncomeDetailSerializer(income)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="특정 수익 복제",
        responses={200: "성공", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def post(self, reuqest, income_id):
        income = self.get_objects(income_id)
        income.id = None
        income.save()
        IncomeCalcUtil.add_total_money_income(income.account_book, income.money)
        return Response({"message":"복사 완료"}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=IncomeCreateSerializer,
        operation_summary="특정 수익 수정",
        responses={200: "성공", 400: "인풋값 에러", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def put(self, request, income_id):
        try:
            income = self.get_objects(income_id)
            income_money = income.money
            serializer = IncomeCreateSerializer(income, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                IncomeCalcUtil.mix_total_money_income(income.account_book, income_money, int(request.data["money"]))
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        except KeyError:
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="특정 수익 삭제",
        responses={204: "성공", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def delete(self, request, income_id):
        income = self.get_objects(income_id)
        IncomeCalcUtil.sub_total_money_income(income.account_book, income.money)
        income.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IncomeShareUrlCreateView(APIView):
    permission_classes = [IsOwner]
    
    def get_objects(self, income_id):
        income = get_object_or_404(Income, id=income_id)
        self.check_object_permissions(self.request, income)
        return income
    
    @swagger_auto_schema(
        operation_summary="특정 수익 공유 단축 URL 생성",
        responses={201: "성공", 208: "자원 존재함", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def post(self, request, income_id):
        try:
            income = self.get_objects(income_id)
            shared_url = IncomeUrlUtil.get_income_link(request, income)
            expired_at = IncomeUrlUtil.get_income_link_expired_at(income)
            IncomeURL.objects.create(shared_url=shared_url, expired_at=expired_at, income_id=income.id)
            return Response({"단축 URL(1일 제한)":shared_url}, status=status.HTTP_201_CREATED)
    
        except IntegrityError:
            return Response({"message":"해당 수익 내역의 공유 링크가 존재합니다. "}, status=status.HTTP_208_ALREADY_REPORTED)


class IncomeShareUrlView(APIView):
    permission_classes = [IsAuthenticated]
    
    encode_key_param_config = openapi.Parameter(
        "encode_key",
        in_=openapi.IN_QUERY,
        description="단축 URL 고유 키",
        type=openapi.TYPE_STRING,
    )
    
    @swagger_auto_schema(
        manual_parameters=[encode_key_param_config],
        operation_summary="특정 수익 공유 단축 URL 조회",
        responses={200: "성공", 400: "시간 만료", 401: "인증 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        encode_key = request.GET.get("key", None)
        income_id = IncomeUrlUtil.get_income_id(encode_key)
        income_url = get_object_or_404(IncomeURL, income_id=income_id)
        if income_url.expired_at < timezone.now():
            return Response({"message":"만료된 URL 입니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = IncomeShareUrlSerializer(income_url.income)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IncomeCategoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="수익 카테고리 리스트 조회",
        responses={200: "성공", 401: "인증 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, reuqest):
        category_data = {}
        for i in range(1, 4):
            main_category = get_object_or_404(IncomeCategory, id=i)
            sub_category = main_category.get_descendants(include_self=False)
            sub_category_serializer = IncomeCategorySerializer(sub_category, many=True)
            category_data[f"({i}) {main_category.name}"] = sub_category_serializer.data
        return Response(category_data, status=status.HTTP_200_OK)


class IncomeCategorySearchView(APIView):
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
        operation_summary="수익 카테고리 검색 조회",
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
                income = Income.objects.select_related('account_book').select_related("category").filter \
                (account_book__in=AccountBook.objects.filter(date_at__year=year, date_at__month=month, owner=request.user),
                category__in=get_list_or_404(IncomeCategory, Q(name=main) | Q(name=sub)))
                serializer = IncomeSearchListSerializer(income, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            income = Income.objects.select_related('account_book').filter \
            (account_book__in=AccountBook.objects.filter(date_at__year=year, date_at__month=month, owner=request.user))
            serializer = IncomeSearchListSerializer(income, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except IndexError:
            return Response({"message":"올바른 매개변수의 날짜를 입력해주세요.(Ex: YYYY-MM)"}, status=status.HTTP_400_BAD_REQUEST)


class IncomeCategoryStatView(APIView):
    permission_classes = [IsAuthenticated]
    
    date_param_config = openapi.Parameter(
        "date",
        in_=openapi.IN_QUERY,
        description="년 월 입력 (Ex:YYYY-MM)",
        type=openapi.TYPE_STRING,
    )
    
    
    def get_amount_for_category_null(self, income):
        income = income.filter(category__isnull=True)
        
        amount = 0
        
        for income in income:
            amount += income.money
        return {"amount":str(amount)}
    
    def get_amount_for_category(self, category, income):   
        income = income.filter(category__in=IncomeCategory.objects.get(name=category).get_descendants(include_self=True))
        
        amount = 0
        
        for income in income:
            amount += income.money
        return {"amount":str(amount)}

    def get_category(self, income):
        try:
            if not income.category.parent:
                return income.category

        except AttributeError:
            return None
    
    @swagger_auto_schema(
        manual_parameters=[date_param_config],
        operation_summary="수익 내역 월별 통계",
        responses={200: "성공", 400: "매개변수 에러", 401: "인증 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        try:
            date = request.GET.get("date", None).split('-')
            year = date[0]
            month = date[1]
            
            income = Income.objects.select_related('account_book').select_related('category').filter \
            (account_book__in=get_list_or_404(AccountBook, date_at__year=year, date_at__month=month, owner=request.user))
            
            final = {}
            category = list(set(map(self.get_category, income)))
            
            for category in category:
                if category == None:
                    final["없음"]=self.get_amount_for_category_null(income)
                else:
                    final[str(category)]=self.get_amount_for_category(category, income)
            return Response({"category_data":final}, status=status.HTTP_200_OK)
        
        except IndexError:
            return Response({"message":"올바른 매개변수의 날짜를 입력해주세요.(Ex: YYYY-MM)"}, status=status.HTTP_400_BAD_REQUEST)
