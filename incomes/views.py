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
    IncomeSerializer
)

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