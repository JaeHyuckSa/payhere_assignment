# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404

# django
from django.core.exceptions import ValidationError

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# expenses
from .serializers import ExpenseSerializer

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