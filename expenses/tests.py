# rest_framework
from rest_framework.test import APITestCase

# django
from django.urls import reverse

# expenses
from .models import Expense, ExpenseURL

# users
from users.models import User

# account_book
from account_books.models import AccountBook


class ExpenseListAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.other_user_data = {"email": "test1235@test.com", "password": "Test1235!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.other_user = User.objects.create_user("test1235@test.com", "test12345", "Test1235!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        for _ in range(1, 11):
            Expense.objects.create(
                money=30000, 
                expense_detail="(주) 소고기 짱 좋아",
                payment_method="현금",
                memo="소고기 많이 먹음",
                owner=cls.user,
                account_book=cls.account_book,
            )
        
    def setUp(self):
        self.user_access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.other_user_access_token = self.client.post(reverse("auth-signin"), self.other_user_data).data["access"]
    
    # 해당 일자 지출 리스트 조회 성공
    def test_expense_list_success(self):
        response = self.client.get(
            path=f"{reverse('expense-list')}?date=2023-02-01",
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # 해당 일자 지출 리스트 조회 실패 (비회원)
    def test_expense_list_anonymous_fail(self):
        response = self.client.get(
            path=f"{reverse('expense-list')}?date=2023-02-01",
        )
        self.assertEqual(response.status_code, 403)
        
    # 해당 일자 지출 리스트 조회 실패 (다른 회원)
    def test_expense_list_other_user_fail(self):
        response = self.client.get(
            path=f"{reverse('expense-list')}?date=2023-02-01",
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)

    # 해당 일자 지출 리스트 조회 실패 (가계부 찾을 수 없음)
    def test_expense_list_param_fail(self):
        response = self.client.get(
            path=f"{reverse('expense-list')}?date=2023-02-19",
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)


class ExpenseCreateAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.other_user_data = {"email": "test1235@test.com", "password": "Test1235!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.other_user = User.objects.create_user("test1235@test.com", "test12345", "Test1235!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        cls.expense_data = {
                "money":30000, 
                "expense_detail":"(주) 소고기 짱 좋아",
                "payment_method":"현금",
                "memo":"소고기 많이 먹음",
        }
    
    def setUp(self):
        self.user_access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.other_user_access_token = self.client.post(reverse("auth-signin"), self.other_user_data).data["access"]
        
    # 해당 일자 지출 생성 성공
    def test_expense_create_success(self):
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data=self.expense_data
        )
        self.assertEqual(response.status_code, 201)
        
    # 해당 일자 지출 생성 실패 (money가 invalid일 때)
    def test_expense_create_invalid_fail(self):
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":"돈"}
        )
        self.assertEqual(response.status_code, 400)
    
    # 해당 일자 지출 생성 실패 (money가 blank일 때)
    def test_expense_create_blank_fail(self):
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":""}
        )
        self.assertEqual(response.status_code, 400)
        
    # 해당 일자 지출 생성 실패 (money가 required일 때)
    def test_expense_create_required_fail(self):
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 400)
    
    # 해당 일자 지출 생성 실패 (비회원)
    def test_expense_create_anonymous_fail(self):
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
        
    # 해당 일자 지출 생성 실패 (다른 회원)
    def test_expense_create_other_user_fail(self):
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
    
    # 해당 일자 지출 생성 실패 (가계부 찾을 수 없음)
    def test_expense_create_exist_fail(self):
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)


class ExpenseDetailAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.other_user_data = {"email": "test1235@test.com", "password": "Test1235!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.other_user = User.objects.create_user("test1235@test.com", "test12345", "Test1235!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        cls.expense = Expense.objects.create(
            money=30000, 
            expense_detail="(주) 소고기 짱 좋아", 
            payment_method="현금", 
            memo="소고기 많이 먹음", 
            account_book=cls.account_book,
            owner=cls.user,
        )
    
    def setUp(self):
        self.user_access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.other_user_access_token = self.client.post(reverse("auth-signin"), self.other_user_data).data["access"]
        
    # 특정 지출 조회 성공
    def test_expense_detail_get_success(self):
        response = self.client.get(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # 특정 지출 조회 실패 (비회원)
    def test_expense_detail_get_anonymous_fail(self):
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 지출 조회 실패 (다른 회원)
    def test_expense_detail_get_other_user_fail(self):
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 지출 조회 실패 (지출 내역 찾을 수 없음)
    def test_expense_detail_get_exist_fail(self):
        response = self.client.get(
            path=reverse("expense-detail", kwargs={"expense_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)
    
    # 특정 지출 복제 성공
    def test_expense_detail_post_success(self):
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # 특정 지출 복제 실패 (비회원)
    def test_expense_detail_post_anonymous_fail(self):
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 지출 복제 실패 (다른 회원)
    def test_expense_detail_post_other_user_fail(self):
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 지출 복제 실패 (지출 내역 찾을 수 없음)
    def test_expense_detail_post_exist_fail(self):
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)
        
    # 특정 지출 수정 성공
    def test_expense_detail_put_success(self):
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":40000}
        )
        self.assertEqual(response.status_code, 200)
    
    # 특정 지출 수정 성공 (money가 required일 때)
    def test_expense_detail_put_required_success(self):
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
    
    # 특정 지출 수정 실패 (money가 blank일 때)
    def test_expense_detail_put_blank_fail(self):
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":""}
        )
        self.assertEqual(response.status_code, 400)
    
    # 특정 지출 수정 실패 (money가 invalid일 때)
    def test_expense_detail_put_invalid_fail(self):
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":"돈"}
        )
        self.assertEqual(response.status_code, 400)
    
    # 특정 지출 수정 실패 (비회원)
    def test_expense_detail_put_anonymous_fail(self):
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            data={"money":40000}
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 지출 수정 실패 (다른 회원)
    def test_expense_detail_put_other_user_fail(self):
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
            data={"money":40000}
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 지출 수정 실패 (지출 내역 찾을 수 없음)
    def test_expense_detail_put_exist_fail(self):
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money":40000}
        )
        self.assertEqual(response.status_code, 404)
        
    # 특정 지출 삭제 성공
    def test_expense_detail_delete_success(self):
        response = self.client.delete(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 204)
        
    # 특정 지출 삭제 실패 (비회원)
    def test_expense_detail_delete_anonymous_fail(self):
        response = self.client.delete(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 지출 삭제 실패 (다른 회원)
    def test_expense_detail_delete_other_user_fail(self):
        response = self.client.delete(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 지출 삭제 실패 (지출 내역 찾을 수 없음)
    def test_expense_detail_delete_exist_fail(self):
        response = self.client.delete(
            path=reverse("expense-detail", kwargs={"expense_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)


class ExpenseShareUrlCreateAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.other_user_data = {"email": "test1235@test.com", "password": "Test1235!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.other_user = User.objects.create_user("test1235@test.com", "test12345", "Test1235!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        for _ in range(2):
            cls.expense = Expense.objects.create(
                    money=30000, 
                    expense_detail="(주) 소고기 짱 좋아", 
                    payment_method="현금", 
                    memo="소고기 많이 먹음", 
                    account_book=cls.account_book,
                    owner=cls.user,
                )
        cls.expense_url = ExpenseURL.objects.create(shared_url="http://testserver/MQd17c80f", expired_at="2024-02-03", expense=cls.expense)
    
    def setUp(self):
        self.user_access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.other_user_access_token = self.client.post(reverse("auth-signin"), self.other_user_data).data["access"]

    # 특정 지출 공유 단축 URL 생성 성공
    def test_expense_share_url_create_success(self):
        response = self.client.post(
            path=reverse("expense-share-url-create", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 201)
    
    # 특정 지출 공유 단축 URL 생성 실패 (중복)
    def test_expense_share_url_create_unique_fail(self):
        response = self.client.post(
            path=reverse("expense-share-url-create", kwargs={"expense_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 208)
        
    # 특정 지출 공유 단축 URL 생성 실패 (비회원)
    def test_expense_share_url_create_anonymous_fail(self):
        response = self.client.post(
            path=reverse("expense-share-url-create", kwargs={"expense_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
        
    # 특정 지출 공유 단축 URL 생성 실패 (다른 회원)
    def test_expense_share_url_create_other_user_fail(self):
        response = self.client.post(
            path=reverse("expense-share-url-create", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
    
    # 특정 지출 공유 단축 URL 생성 실패 (지출 내역 찾을 수 없음)
    def test_expense_share_url_create_exist_fail(self):
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "3"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)
        

class ExpenseShareUrlAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        for _ in range(1, 3):
            cls.expense = Expense.objects.create(
                money=30000, 
                expense_detail="(주) 소고기 짱 좋아", 
                payment_method="현금", 
                memo="소고기 많이 먹음", 
                account_book=cls.account_book,
                owner=cls.user,
            )
        ExpenseURL.objects.create(
            shared_url="http://testserver/MQd17c80f",
            expired_at="2023-02-02", 
            expense_id=1,
        )
        ExpenseURL.objects.create(
            shared_url="http://testserver/Mgd17c80f",
            expired_at="2024-02-10", 
            expense_id=2,
        )
        
    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        
    # 특정 지출 공유 단축 URL 조회 성공 
    def test_expense_share_url_success(self):
        response = self.client.get(
            path=f"{reverse('expense-share-url')}?key=Mgd17c80f",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
    
    # 특정 지출 공유 단축 URL 조회 실패 (시간 만료됨)
    def test_expense_share_url_time_limit_fail(self):
        response = self.client.get(
            path=f"{reverse('expense-share-url')}?key=MQd17c80f",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)
        
    # 특정 지출 공유 단축 URL 조회 실패 (비회원)
    def test_expense_share_url_anonymous_fail(self):
        response = self.client.get(
            path=f"{reverse('expense-share-url')}?key=MQd17c80f",
        )
        self.assertEqual(response.status_code, 401)
    
    # 특정 지출 공유 단축 URL 조회 실패 (지출 내역 찾을 수 없음)
    def test_expense_share_url_exist_fail(self):
        response = self.client.get(
            path=f"{reverse('expense-share-url')}?key=ddddddd",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)