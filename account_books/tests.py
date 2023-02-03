# rest_framework
from rest_framework.test import APITestCase

# django
from django.urls import reverse

# users
from users.models import User

# account_book
from .models import AccountBook


class AccountBookAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        for i in range(1, 11):
            AccountBook.objects.create(date_at=f"2023-02-{i}", owner=cls.user)
        
    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
    
    # 가계부 생성 성공
    def test_account_book_post_success(self):
        response = self.client.post(
            path=reverse("account-book"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"date_at": "2023-02-11"},
        )
        self.assertEqual(response.status_code, 201)
        
    # 가계부 생성 실패(날짜 중복)
    def test_account_book_post_unique_fail(self):
        response = self.client.post(
            path=reverse("account-book"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"date_at": "2023-02-01"},
        )
        self.assertEqual(response.status_code, 400)
    
    # 가계부 생성 실패 (날짜 형식이 아닐 때)
    def test_account_book_post_invalid_fail(self):
        response = self.client.post(
            path=reverse("account-book"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"date_at": "123456"},
        )
        self.assertEqual(response.status_code, 400)
        
    # 가계부 생성 실패 (date_at이 blank)
    def test_account_book_post_blank_fail(self):
        response = self.client.post(
            path=reverse("account-book"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"date_at": ""},
        )
        self.assertEqual(response.status_code, 400)
        
    # 가계부 생성 실패 (date_at이 required)
    def test_account_book_post_required_fail(self):
        response = self.client.post(
            path=reverse("account-book"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)
    
    # 가계부 생성 실패 (비회원)
    def test_account_book_post_anonymous_fail(self):
        response = self.client.post(
            path=reverse("account-book"),
            data={"date_at": "2023-02-15"},
        )
        self.assertEqual(response.status_code, 401)
    
    # 가계부 월별 조회 성공
    def test_account_book_get_success(self):
        response = self.client.get(
            path=f"{reverse('account-book')}?date=2023-02",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
    
    # 가계부 월별 조회 실패 (매개변수 잘못 설정)
    def test_account_book_get_param_fail(self):
        response = self.client.get(
            path=f"{reverse('account-book')}?date=202302",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)
        
    # 가계부 월별 조회 실패 (비회원)
    def test_account_book_get_anonymous_fail(self):
        response = self.client.get(
            path=f"{reverse('account-book')}?date=2023-02",
        )
        self.assertEqual(response.status_code, 401)
    
    # 가계부 월별 조회 실패 (해당 날짜 가계부 없음)
    def test_account_book_get_exist_fail(self):
        response = self.client.get(
            path=f"{reverse('account-book')}?date=2023-03",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)


class AccountBookDateSetAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        for i in range(1, 11):
            AccountBook.objects.create(date_at=f"2023-02-{i}", owner=cls.user)
        
    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
    
    # 가계부 날짜 범위 설정 성공
    def test_account_book_date_set_success(self):
        response = self.client.get(
            path=f"{reverse('account-book-date-set')}?from=2023-02-01&to=2023-02-10",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    # 가계부 날짜 범위 설정 실패 (매개변수 잘못 설정)
    def test_account_book_date_set_param_fail(self):
        response = self.client.get(
            path=f"{reverse('account-book-date-set')}?from=20230215&to=20230220",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    # 가계부 날짜 범위 설정 실패 (비회원)
    def test_account_book_date_set_anonymous_fail(self):
        response = self.client.get(
            path=f"{reverse('account-book-date-set')}?from=2023-02-15&to=2023-02-20",
        )
        self.assertEqual(response.status_code, 401)

    # 가계부 날짜 범위 설정 실패 (해당 날짜 가계부 없음)
    def test_account_book_date_set_exist_fail(self):
        response = self.client.get(
            path=f"{reverse('account-book-date-set')}?from=2023-02-15&to=2023-02-20",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)


class AccountBookDetailAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.other_user_data = {"email": "test1235@test.com", "password": "Test1235!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.other_user = User.objects.create_user("test1235@test.com", "test12345", "Test1235!")
        for i in range(1, 6):
            AccountBook.objects.create(date_at=f"2023-02-{i}", owner=cls.user)
        
        
    def setUp(self):
        self.user_access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.other_user_access_token = self.client.post(reverse("auth-signin"), self.other_user_data).data["access"]
    
    # 가계부 상세 조회 성공
    def test_account_book_detail_get_success(self):
        response = self.client.get(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # 가계부 상세 조회 실패 (비회원)
    def test_account_book_detail_get_anonymous_fail(self):
        response = self.client.get(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
    
    # 가계부 수정 실패 (다른 회원)
    def test_account_book_detail_get_other_user_fail(self):
        response = self.client.get(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        print(response.data)
        self.assertEqual(response.status_code, 403)
        
    # 가계부 상세 조회 실패 (가계부 찾을 수 없음)
    def test_account_book_detail_get_exits_success(self):
        response = self.client.get(
            path=reverse("account-book-detail", kwargs={"account_book_id": "8"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)
    
    # 가계부 수정 성공
    def test_account_book_detail_put_success(self):
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"date_at": "2023-02-06"},
        )
        self.assertEqual(response.status_code, 200)

    # 가계부 수정 실패 (날짜 중복)
    def test_account_book_detail_put_unique_fail(self):
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"date_at": "2023-02-05"},
        )
        self.assertEqual(response.status_code, 400)
    
    # 가계부 수정 실패 (날짜 형식이 아닐 때)
    def test_account_book_detail_put_invalid_fail(self):
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"date_at": "123456"},
        )
        self.assertEqual(response.status_code, 400)
    
    # 가계부 수정 실패 (비회원)
    def test_account_book_detail_put_anonymous_fail(self):
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            data={"date_at": "2023-02-06"},
        )
        self.assertEqual(response.status_code, 403)
    
    # 가계부 수정 실패 (다른 회원)
    def test_account_book_detail_put_other_user_fail(self):
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
            data={"date_at": "2023-02-06"},
        )
        self.assertEqual(response.status_code, 403)
    
    # 가계부 수정 실패 (없는 가계부)
    def test_account_book_detail_put_exist_fail(self):
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "15"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"date_at": "2023-02-06"},
        )
        self.assertEqual(response.status_code, 404)
    
    # 가계부 삭제 성공
    def test_account_book_detail_delete_success(self):
        response = self.client.delete(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 204)
    
    # 가계부 삭제 실패 (비회원)
    def test_account_book_detail_delete_anonymous_fail(self):
        response = self.client.delete(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)
    
    # 가계부 삭제 실패 (다른 회원)
    def test_account_book_detail_delete_other_user_fail(self):
        response = self.client.delete(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)
    
    # 가계부 삭제 실패 (없는 가계부)
    def test_account_book_detail_delete_exist_fail(self):
        response = self.client.delete(
            path=reverse("account-book-detail", kwargs={"account_book_id": "15"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)