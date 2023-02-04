# rest_framework
from rest_framework.test import APITestCase

# django
from django.urls import reverse
from django.core.management import call_command

# python
import random

# income
from .models import Income, IncomeURL

# users
from users.models import User

# account_book
from account_books.models import AccountBook


class IncomeListAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.other_user_data = {"email": "test1235@test.com", "password": "Test1235!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.other_user = User.objects.create_user("test1235@test.com", "test12345", "Test1235!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        for _ in range(1, 11):
            Income.objects.create(
                money=3000000, 
                income_detail="(주) IT 회사",
                payment_method="현금",
                memo="돈 많이 받았다!",
                owner=cls.user,
                account_book=cls.account_book,
            )
        
    def setUp(self):
        self.user_access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.other_user_access_token = self.client.post(reverse("auth-signin"), self.other_user_data).data["access"]
    
    # 해당 일자 수익 리스트 조회 성공
    def test_income_list_success(self):
        response = self.client.get(
            path=f"{reverse('income-list')}?date=2023-02-01",
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # 해당 일자 수익 리스트 조회 실패 (비회원)
    def test_income_list_anonymous_fail(self):
        response = self.client.get(
            path=f"{reverse('income-list')}?date=2023-02-01",
        )
        self.assertEqual(response.status_code, 403)
        
    # 해당 일자 수익 리스트 조회 실패 (다른 회원)
    def test_income_list_other_user_fail(self):
        response = self.client.get(
            path=f"{reverse('income-list')}?date=2023-02-01",
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)

    # 해당 일자 수익 리스트 조회 실패 (가계부 찾을 수 없음)
    def test_income_list_param_fail(self):
        response = self.client.get(
            path=f"{reverse('income-list')}?date=2023-02-19",
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)


class IncomeCreateAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.other_user_data = {"email": "test1235@test.com", "password": "Test1235!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.other_user = User.objects.create_user("test1235@test.com", "test12345", "Test1235!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        cls.income_data = {
                "money":3000000, 
                "income_detail":"(주) IT 회사",
                "payment_method":"현금",
                "memo":"돈 많이 받았다!",
        }
    
    def setUp(self):
        self.user_access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.other_user_access_token = self.client.post(reverse("auth-signin"), self.other_user_data).data["access"]
        
    # 해당 일자 수익 생성 성공
    def test_income_create_success(self):
        response = self.client.post(
            path=reverse("income-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data=self.income_data
        )
        self.assertEqual(response.status_code, 201)
        
    # 해당 일자 수익 생성 실패 (money가 invalid일 때)
    def test_income_create_invalid_fail(self):
        response = self.client.post(
            path=reverse("income-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":"돈"}
        )
        self.assertEqual(response.status_code, 400)
    
    # 해당 일자 수익 생성 실패 (money가 blank일 때)
    def test_income_create_blank_fail(self):
        response = self.client.post(
            path=reverse("income-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":""}
        )
        self.assertEqual(response.status_code, 400)
        
    # 해당 일자 수익 생성 실패 (money가 required일 때)
    def test_income_create_required_fail(self):
        response = self.client.post(
            path=reverse("income-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 400)
    
    # 해당 일자 수익 생성 실패 (비회원)
    def test_income_create_anonymous_fail(self):
        response = self.client.post(
            path=reverse("income-create", kwargs={"account_book_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
        
    # 해당 일자 수익 생성 실패 (다른 회원)
    def test_income_create_other_user_fail(self):
        response = self.client.post(
            path=reverse("income-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
    
    # 해당 일자 수익 생성 실패 (가계부 찾을 수 없음)
    def test_income_create_exist_fail(self):
        response = self.client.post(
            path=reverse("income-create", kwargs={"account_book_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)


class IncomeDetailAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.other_user_data = {"email": "test1235@test.com", "password": "Test1235!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.other_user = User.objects.create_user("test1235@test.com", "test12345", "Test1235!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        cls.income = Income.objects.create(
            money=3000000, 
            income_detail="(주) IT 회사",
            payment_method="현금",
            memo="돈 많이 받았다!",
            owner=cls.user,
            account_book=cls.account_book,
        )
    
    def setUp(self):
        self.user_access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.other_user_access_token = self.client.post(reverse("auth-signin"), self.other_user_data).data["access"]
        
    # 특정 수익 조회 성공
    def test_income_detail_get_success(self):
        response = self.client.get(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # 특정 수익 조회 실패 (비회원)
    def test_income_detail_get_anonymous_fail(self):
        response = self.client.post(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 수익 조회 실패 (다른 회원)
    def test_income_detail_get_other_user_fail(self):
        response = self.client.post(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 수익 조회 실패 (수익 내역 찾을 수 없음)
    def test_income_detail_get_exist_fail(self):
        response = self.client.get(
            path=reverse("income-detail", kwargs={"income_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)
    
    # 특정 수익 복제 성공
    def test_income_detail_post_success(self):
        response = self.client.post(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # 특정 수익 복제 실패 (비회원)
    def test_income_detail_post_anonymous_fail(self):
        response = self.client.post(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 수익 복제 실패 (다른 회원)
    def test_income_detail_post_other_user_fail(self):
        response = self.client.post(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 수익 복제 실패 (수익 내역 찾을 수 없음)
    def test_income_detail_post_exist_fail(self):
        response = self.client.post(
            path=reverse("income-detail", kwargs={"income_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)
        
    # 특정 수익 수정 성공
    def test_income_detail_put_success(self):
        response = self.client.put(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":40000}
        )
        self.assertEqual(response.status_code, 200)
    
    # 특정 수익 수정 성공 (money가 required일 때)
    def test_income_detail_put_required_success(self):
        response = self.client.put(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
    
    # 특정 수익 수정 실패 (money가 blank일 때)
    def test_income_detail_put_blank_fail(self):
        response = self.client.put(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":""}
        )
        self.assertEqual(response.status_code, 400)
    
    # 특정 수익 수정 실패 (money가 invalid일 때)
    def test_income_detail_put_invalid_fail(self):
        response = self.client.put(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":"돈"}
        )
        self.assertEqual(response.status_code, 400)
    
    # 특정 수익 수정 실패 (비회원)
    def test_income_detail_put_anonymous_fail(self):
        response = self.client.put(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            data={"money":40000}
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 수익 수정 실패 (다른 회원)
    def test_income_detail_put_other_user_fail(self):
        response = self.client.put(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
            data={"money":40000}
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 수익 수정 실패 (수익 내역 찾을 수 없음)
    def test_income_detail_put_exist_fail(self):
        response = self.client.put(
            path=reverse("income-detail", kwargs={"income_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":40000}
        )
        self.assertEqual(response.status_code, 404)
        
    # 특정 수익 삭제 성공
    def test_income_detail_delete_success(self):
        response = self.client.delete(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 204)
        
    # 특정 수익 삭제 실패 (비회원)
    def test_income_detail_delete_anonymous_fail(self):
        response = self.client.delete(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 수익 삭제 실패 (다른 회원)
    def test_income_detail_delete_other_user_fail(self):
        response = self.client.delete(
            path=reverse("income-detail", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 수익 삭제 실패 (수익 내역 찾을 수 없음)
    def test_income_detail_delete_exist_fail(self):
        response = self.client.delete(
            path=reverse("income-detail", kwargs={"income_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)


class IncomeShareUrlCreateAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.other_user_data = {"email": "test1235@test.com", "password": "Test1235!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.other_user = User.objects.create_user("test1235@test.com", "test12345", "Test1235!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        for _ in range(2):
            cls.income = Income.objects.create(
                    money=3000000, 
                    income_detail="(주) IT 회사",
                    payment_method="현금",
                    memo="돈 많이 받았다!",
                    owner=cls.user,
                    account_book=cls.account_book,
                )
        cls.income_url = IncomeURL.objects.create(shared_url="http://testserver/MQd17c80f", expired_at="2024-02-03", income=cls.income)
    
    def setUp(self):
        self.user_access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.other_user_access_token = self.client.post(reverse("auth-signin"), self.other_user_data).data["access"]

    # 특정 수익 공유 단축 URL 생성 성공
    def test_income_share_url_create_success(self):
        response = self.client.post(
            path=reverse("income-share-url-create", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 201)
    
    # 특정 수익 공유 단축 URL 생성 실패 (중복)
    def test_income_share_url_create_unique_fail(self):
        response = self.client.post(
            path=reverse("income-share-url-create", kwargs={"income_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 208)
        
    # 특정 수익 공유 단축 URL 생성 실패 (비회원)
    def test_income_share_url_create_anonymous_fail(self):
        response = self.client.post(
            path=reverse("income-share-url-create", kwargs={"income_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 수익 공유 단축 URL 생성 실패 (다른 회원)
    def test_income_share_url_create_other_user_fail(self):
        response = self.client.post(
            path=reverse("income-share-url-create", kwargs={"income_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
    
    # 특정 수익 공유 단축 URL 생성 실패 (수익 내역 찾을 수 없음)
    def test_income_share_url_create_exist_fail(self):
        response = self.client.post(
            path=reverse("income-detail", kwargs={"income_id": "3"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)


class IncomeShareUrlAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        for _ in range(1, 3):
            cls.income = Income.objects.create(
                money=3000000, 
                income_detail="(주) IT 회사",
                payment_method="현금",
                memo="돈 많이 받았다!",
                owner=cls.user,
                account_book=cls.account_book,
            )
        IncomeURL.objects.create(
            shared_url="http://testserver/MQd17c80f",
            expired_at="2023-02-02", 
            income_id=1,
        )
        IncomeURL.objects.create(
            shared_url="http://testserver/Mgd17c80f",
            expired_at="2024-02-10", 
            income_id=2,
        )
    
    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
    
    # 특정 수익 공유 단축 URL 조회 성공 
    def test_income_share_url_success(self):
        response = self.client.get(
            path=f"{reverse('income-share-url')}?key=Mgd17c80f",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
    
    # 특정 수익 공유 단축 URL 조회 실패 (시간 만료됨)
    def test_income_share_url_time_limit_fail(self):
        response = self.client.get(
            path=f"{reverse('income-share-url')}?key=MQd17c80f",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)
        
    # 특정 수익 공유 단축 URL 조회 실패 (비회원)
    def test_income_share_url_anonymous_fail(self):
        response = self.client.get(
            path=f"{reverse('income-share-url')}?key=Mgd17c80f",
        )
        self.assertEqual(response.status_code, 401)
    
    # 특정 수익 공유 단축 URL 조회 실패 (수익 내역 찾을 수 없음)
    def test_income_share_url_exist_fail(self):
        response = self.client.get(
            path=f"{reverse('income-share-url')}?key=ddddddd",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)


class IncomeCategoryAPIViewTestCase(APITestCase):
    
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        call_command('loaddata', 'json_data/income_category_data.json')
        
    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        
    # 수익 카테고리 리스트 조회 성공
    def test_income_category_success(self):
        response = self.client.get(
            path=reverse("income-category"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # 수익 카테고리 리스트 조회 실패 (비회원)
    def test_income_category_anonymous_fail(self):
        response = self.client.get(
            path=reverse("income-category"),
        )
        self.assertEqual(response.status_code, 401)


class IncomeCategorySearchAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        call_command('loaddata', 'json_data/income_category_data.json')
        for _ in range(101):
            cls.income = Income.objects.create(
                    money=3000000, 
                    income_detail="(주) IT 회사",
                    payment_method="현금",
                    memo="돈 많이 받았다!",
                    owner=cls.user,
                    account_book=cls.account_book,
                    category_id=random.randint(1, 7),
                )
        
    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]

    # 수익 카테고리 검색 조회 성공 
    def test_income_category_search_success(self):
        response = self.client.get(
            path=f"{reverse('income-category-search')}?date=2023-02&main=근로소득&sub=금융소득",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # 수익 카테고리 검색 조회 성공 (해당 월별 가계부의 모든 쿼리)
    def test_income_category_search_all_success(self):
        response = self.client.get(
            path=f"{reverse('income-category-search')}?date=2023-02",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # 수익 카테고리 검색 조회 실패 (카테고리 매개변수 잘못됨)
    def test_income_category_search_date_param_fail(self):
        response = self.client.get(
            path=f"{reverse('income-category-search')}?date=202302&main=근로소득&sub=금융소득",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)
    
    # 수익 카테고리 검색 조회 실패 (비회원)
    def test_income_category_search_anonymous_fail(self):
        response = self.client.get(
            path=f"{reverse('income-category-search')}?date=2023-02&main=근로소득&sub=금융소득",
        )
        self.assertEqual(response.status_code, 401)
    
    # 수익 카테고리 검색 조회 실패 (수익 내역 없음)
    def test_income_category_search_tag_param_fail(self):
        response = self.client.get(
            path=f"{reverse('income-category-search')}?date=2023-02&main=근로/소득&sub=금융/소득",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)


class IncomeCategoryStatAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        call_command('loaddata', 'json_data/income_category_data.json')
        for _ in range(101):
            cls.income = Income.objects.create(
                    money=3000000, 
                    income_detail="(주) IT 회사",
                    payment_method="현금",
                    memo="돈 많이 받았다!",
                    owner=cls.user,
                    account_book=cls.account_book,
                    category_id=random.randint(1, 7),
                )
        
    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        
    # 수익 통계 조회 성공 
    def test_income_category_stat_success(self):
        response = self.client.get(
            path=f"{reverse('income-caregory-stat')}?date=2023-02",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # 수익 통계 조회 실패 (카테고리 매개변수 잘못됨)
    def test_income_category_stat_param_fail(self):
        response = self.client.get(
            path=f"{reverse('income-caregory-stat')}?date=202302",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)
        
    # 수익 통계 조회 실패 (비회원)
    def test_income_category_stat_anonymous_fail(self):
        response = self.client.get(
            path=f"{reverse('income-caregory-stat')}?date=2023-02",
        )
        self.assertEqual(response.status_code, 401)
        
    # 수익 통계 조회 실패 (가계부 찾을 수 없음)
    def test_income_category_stat_exist_fail(self):
        response = self.client.get(
            path=f"{reverse('income-caregory-stat')}?date=2023-04",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)