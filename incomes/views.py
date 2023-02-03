# rest framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# incomes
from .models import Income, IncomeURL
from .serializers import (
    IncomeSerializer,
    IncomeCreateSerializer
)
from .utils import IncomeCalcUtil

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
        date = request.GET.get("date")
        income = self.get_objects(date)
        serializer = IncomeSerializer(income, many=True)
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
        serializer = IncomeSerializer(income)
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
            serializer = IncomeCreateSerializer(income, data=request.data, partial=True, context={"request": request})
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