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

# apps/project
from .models import Income, IncomeURL, IncomeCategory
from .serializers import (
    IncomeListSerializer,
    IncomeDetailSerializer,
    IncomeCreateSerializer,
    IncomeSearchListSerializer,
    IncomeShareUrlSerializer,
    IncomeCategorySerializer,
)
from account_books.models import AccountBook
from payhere.permissions import IsOwner
from payhere.utils import IncomeCalcUtil, UrlUtil

# Swagger Parameter
day_param_config = openapi.Parameter(
    "date",
    in_=openapi.IN_QUERY,
    description="년 월 일 입력 (Ex:YYYY-MM-DD)",
    type=openapi.TYPE_STRING,
)

month_param_config = openapi.Parameter(
    "date",
    in_=openapi.IN_QUERY,
    description="년 월 입력 (Ex:YYYY-MM)",
    type=openapi.TYPE_STRING,
)

encode_key_param_config = openapi.Parameter(
    "encode_key",
    in_=openapi.IN_QUERY,
    description="단축 URL 고유 키",
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


class IncomeListView(APIView):
    """일간 수익 내역 리스트 조회
    
    get_objects: 객체를 조회해 사용자만 접근 가능하도록 검증 후 객체 반환합니다.
    get: url 매개변수 date(YYYY-MM-DD)로 받으면 일간 수익 리스트를 조회합니다.
        return: id, money, income_detail, payment_method
    """
    permission_classes = [IsOwner]

    def get_objects(self, date):
        account_book = get_object_or_404(AccountBook, date_at=date)
        self.check_object_permissions(self.request, account_book)
        incomes = account_book.incomes
        return incomes

    @swagger_auto_schema(
        manual_parameters=[day_param_config],
        operation_summary="일간 수익 리스트 조회",
        responses={200: "성공", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        date = request.GET.get("date", None)
        incomes = self.get_objects(date)
        serializer = IncomeListSerializer(incomes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IncomeCreateView(APIView):
    """수익 내역 생성
    
    get_objects: 객체를 조회해 사용자만 접근 가능하도록 검증 후 객체 반환합니다.
    post: money, income_detail, payment_method, memo, category를 입력받아 수익 내역을 생성합니다.
        add_total_money_income 함수를 통해 상위 가계부의 전체금액에 수익 금액만큼 더한 값이 반영됩니다. 
    """
    permission_classes = [IsOwner]

    def get_objects(self, account_book_id):
        account_book = get_object_or_404(AccountBook, id=account_book_id)
        self.check_object_permissions(self.request, account_book)
        return account_book

    @swagger_auto_schema(
        request_body=IncomeCreateSerializer,
        operation_summary="수익 내역 생성",
        responses={201: "성공", 400: "인풋값 에러", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def post(self, request, account_book_id):
        account_book = self.get_objects(account_book_id)
        serializer = IncomeCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user, account_book=account_book)
            IncomeCalcUtil.add_total_money_income(
                account_book, int(request.data["money"])
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IncomeDetailView(APIView):
    """특정 수익 조회, 복제, 수정, 삭제
    
    get_objects: 객체를 조회해 사용자만 접근 가능하도록 검증 후 객체 반환합니다.
    get: 특정 수익 내역을 조회합니다.
        return id, money, income_detail, payment_method, memo, category
    post: 특정 객체를 가져와 null 값으로 만들어 새롭게 저장하여 복제합니다.
        add_total_money_income 함수를 통해 상위 가계부의 전체금액에 수익 금액만큼 더한 값이 반영됩니다. 
    put: 특정 수익 내역을 수정하며 money를 입력받지 않을 경우 KeyError 발생으로 예외처리를 했습니다.
        mix_total_money_income 함수를 통해 상위 가계부의 전체금액에 수익 금액만큼 빼고 더한 값이 반영됩니다.
    delete: 특정 수익 내역을 삭제합니다.
        sub_total_money_income 함수를 통해 상위 가계부의 전체 금액에 수익 금액만큼 뺀 값이 반영됩니다.
    """
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
        IncomeCalcUtil.add_total_money_income(
            income.account_book, income.money
            )
        return Response({"message": "복사 완료"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=IncomeCreateSerializer,
        operation_summary="특정 수익 수정",
        responses={200: "성공",400: "인풋값 에러",403: "권한 없음",404: "찾을 수 없음",500: "서버 에러"},
    )
    def put(self, request, income_id):
        try:
            income = self.get_objects(income_id)
            income_money = income.money
            serializer = IncomeCreateSerializer(income, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                IncomeCalcUtil.mix_total_money_income(
                    income.account_book, income_money, int(request.data["money"])
                )
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
        IncomeCalcUtil.sub_total_money_income(
            income.account_book, income.money
            )
        income.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IncomeShareUrlCreateView(APIView):
    """특정 수익 내역 공유 단축 URL 생성
    
    get_objects: 객체를 조회해 사용자만 접근 가능하도록 검증 후 객체 반환합니다.
    post: 객체를 가져와 get_share_link 함수 를 통해 uuid와 uidb64로 이루어진 
        단축 link를 반환하며 get_share_link_expired_at 함수로 만료일을 반환하여 저장합니다.
        수익 내역이 이미 공유 링크가 있을 경우 예외처리했습니다.
    """
    permission_classes = [IsOwner]

    def get_objects(self, income_id):
        income = get_object_or_404(Income, id=income_id)
        self.check_object_permissions(self.request, income)
        return income

    @swagger_auto_schema(
        operation_summary="특정 수익 내역 공유 단축 URL 생성",
        responses={201: "성공", 208: "자원 존재함", 403: "권한 없음", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def post(self, request, income_id):
        try:
            income = self.get_objects(income_id)
            shared_url = UrlUtil.get_share_link(request, income)
            expired_at = UrlUtil.get_share_link_expired_at()
            IncomeURL.objects.create(shared_url=shared_url, expired_at=expired_at, income_id=income.id)
            return Response({"단축 URL(1일 제한)": shared_url}, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({"message": "해당 수익 내역의 공유 링크가 존재합니다. "},status=status.HTTP_208_ALREADY_REPORTED)


class IncomeShareUrlView(APIView):
    """특정 수익 내역 공유 단축 URL 조회
    
    get: url 매개변수로 key를 받아 get_query_id 함수로 decode하여 query의 id값을 반환 후
        조회하며 만료일이 지났으면 에러를 발생하며 아닐 시 역직렬화 하여 데이터를 반환합니다.
        return money, income_detail, payment_method, memo, owner, date_at, category
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[encode_key_param_config],
        operation_summary="특정 수익 공유 단축 URL 조회",
        responses={200: "성공", 400: "시간 만료", 401: "인증 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        encode_key = request.GET.get("key", None)
        income_id = UrlUtil.get_query_id(encode_key)
        income_url = get_object_or_404(IncomeURL, income_id=income_id)
        if income_url.expired_at < timezone.now():
            return Response({"message": "만료된 URL 입니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = IncomeShareUrlSerializer(income_url.income)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IncomeCategoryView(APIView):
    """수익 카테고리 리스트 조회
    
    get: 반복문을 통해 고정된 카테고리를 하위 카테고리가 상위 카테고리에 종속되도록
        만든 다음 반환합니다. 
        return main_category_name, sub_category_name
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="수익 카테고리 리스트 조회",
        responses={200: "성공", 401: "인증 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, reuqest):
        category_data = {}
        for i in range(1, 4):
            main_category = get_object_or_404(IncomeCategory, id=i)
            sub_categories = main_category.get_descendants(include_self=False)
            sub_categories_serializer = IncomeCategorySerializer(sub_categories, many=True)
            category_data[f"({i}) {main_category.name}"] = sub_categories_serializer.data
        return Response(category_data, status=status.HTTP_200_OK)


class IncomeCategorySearchView(APIView):
    """월간 수익 카테고리 리스트 조회
    
    get: url 매개변수로 date, main, sub을 받아 카테고리에 맞게 쿼리를 조회하여 반환하며
        기본값으로 main과 sub이 없을 시 date를 기준으로 월간의 모든 수익 내역들을 반환합니다. 
        또한 매개변수 date를 잘못 입력 할 시 예외처리를 하였습니다. 
        return id, money, income_detail, payment_method, date_at
    """
    permission_classes = [IsAuthenticated]


    @swagger_auto_schema(
        manual_parameters=[month_param_config, main_param_config, sub_param_config],
        operation_summary="월간 수익 카테고리 검색 조회",
        responses={200: "성공", 400: "매개변수 에러", 401: "인증 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        try:
            date = request.GET.get("date", None).split("-")
            main = request.GET.get("main", None)
            sub = request.GET.get("sub", None)
            
            year = date[0]
            month = date[1]

            if main or sub:
                select_incomes = (
                    Income.objects.select_related("account_book").select_related("category").filter \
                    (account_book__in=get_list_or_404(AccountBook, date_at__year=year, date_at__month=month, owner=request.user),
                    category__in=get_list_or_404(IncomeCategory, Q(name=main) | Q(name=sub))))
                select_serializer = IncomeSearchListSerializer(select_incomes, many=True)
                return Response(select_serializer.data, status=status.HTTP_200_OK)

            all_incomes = Income.objects.select_related("account_book").filter \
                (account_book__in=get_list_or_404(AccountBook,date_at__year=year, date_at__month=month, owner=request.user))
            all_serializer = IncomeSearchListSerializer(all_incomes, many=True)
            return Response(all_serializer.data, status=status.HTTP_200_OK)

        except IndexError:
            return Response({"message": "올바른 매개변수의 날짜를 입력해주세요.(Ex: YYYY-MM)"}, status=status.HTTP_400_BAD_REQUEST,)


class IncomeCategoryStatView(APIView):
    """월간 수익 내역 통계
    
    get: url 매개변수로 date 받아 쿼리를 조회한 후 get_category 함수로 상위 카테고리를 기준으로 찾아 
        중복된 카테고리를 제거 후 리스트를 반복문으로 카테고리가 존재하면 get_amount_for_category
        존재하지 않으면 get_amount_for_category_null을 통해 해당 수익 내역 총액 데이터를 반환합니다.
        또한 매개변수 date를 잘못 입력 할 시 예외처리를 하였습니다. 
        return main_category_name, amount
    """
    permission_classes = [IsAuthenticated]

    def get_amount_for_category_null(self, income_list):
        incomes = income_list.filter(category__isnull=True)

        amount = 0

        for income in incomes:
            amount += income.money
        return {"amount": str(amount)}

    def get_amount_for_category(self, category, income_list):
        incomes = income_list.filter(category__in=IncomeCategory.objects.get(name=category).get_descendants(include_self=True))

        amount = 0

        for income in incomes:
            amount += income.money
        return {"amount": str(amount)}

    def get_category(self, income):
        try:
            if not income.category.parent:
                return income.category

        except AttributeError:
            return None

    @swagger_auto_schema(
        manual_parameters=[month_param_config],
        operation_summary="월간 수익 내역 통계",
        responses={200: "성공", 400: "매개변수 에러", 401: "인증 에러", 404: "찾을 수 없음", 500: "서버 에러"},
    )
    def get(self, request):
        try:
            date = request.GET.get("date", None).split("-")
            
            year = date[0]
            month = date[1]

            incomes = (
                Income.objects.select_related("account_book").select_related("category").filter \
                (account_book__in=get_list_or_404(AccountBook, date_at__year=year, date_at__month=month, owner=request.user)))

            final = {}
            categories = list(set(map(self.get_category, incomes)))

            for category in categories:
                if category == None:
                    final["없음"] = self.get_amount_for_category_null(incomes)
                else:
                    final[str(category)] = self.get_amount_for_category(category, incomes)
            return Response({"category_data": final}, status=status.HTTP_200_OK)

        except IndexError:
            return Response({"message": "올바른 매개변수의 날짜를 입력해주세요.(Ex: YYYY-MM)"}, status=status.HTTP_400_BAD_REQUEST)
