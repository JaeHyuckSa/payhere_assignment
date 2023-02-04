# rest_framework
from rest_framework.test import APITestCase

# django
from django.urls import reverse
from django.core.management import call_command

# python
import random

# apps
from .models import Expense, ExpenseURL
from users.models import User
from account_books.models import AccountBook


class ExpenseListAPIViewTestCase(APITestCase):
    """ExpenseListView의 API를 검증하는 클래스 (4개)
    get method case: 4개
    """

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

    def test_expense_list_success(self):
        """
        ExpenseListView의 get 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.get(
            path=f"{reverse('expense-list')}?date=2023-02-01",
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_expense_list_anonymous_fail(self):
        """
        ExpenseListView의 get 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-list')}?date=2023-02-01",
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_list_other_user_fail(self):
        """
        ExpenseListView의 get 함수를 겸증하는 함수
        case: 실패(다른 회원일 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-list')}?date=2023-02-01",
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_list_param_fail(self):
        """
        ExpenseListView의 get 함수를 겸증하는 함수
        case: 실패(가계부 찾을 수 없음)
        """
        response = self.client.get(
            path=f"{reverse('expense-list')}?date=2023-02-19",
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)


class ExpenseCreateAPIViewTestCase(APITestCase):
    """ExpenseCreateView의 API를 검증하는 클래스 (7개)
    post method case: 7개
    """

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.other_user_data = {"email": "test1235@test.com", "password": "Test1235!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.other_user = User.objects.create_user("test1235@test.com", "test12345", "Test1235!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        cls.expense_data = {
            "money": 30000,
            "expense_detail": "(주) 소고기 짱 좋아",
            "payment_method": "현금",
            "memo": "소고기 많이 먹음",
        }

    def setUp(self):
        self.user_access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.other_user_access_token = self.client.post(reverse("auth-signin"), self.other_user_data).data["access"]

    def test_expense_create_success(self):
        """
        ExpenseCreateView의 post 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data=self.expense_data,
        )
        self.assertEqual(response.status_code, 201)

    def test_expense_create_invalid_fail(self):
        """
        ExpenseCreateView의 post 함수를 겸증하는 함수
        case: 실패(money 형식이 안 맞을 때)
        """
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money": "돈"},
        )
        self.assertEqual(response.status_code, 400)

    def test_expense_create_blank_fail(self):
        """
        ExpenseCreateView의 post 함수를 겸증하는 함수
        case: 실패(money 빈칸일 때)
        """
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money": ""},
        )
        self.assertEqual(response.status_code, 400)

    def test_expense_create_required_fail(self):
        """
        ExpenseCreateView의 post 함수를 겸증하는 함수
        case: 실패(money 필드가 없을 때)
        """
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_expense_create_anonymous_fail(self):
        """
        ExpenseCreateView의 post 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_create_other_user_fail(self):
        """
        ExpenseCreateView의 post 함수를 겸증하는 함수
        case: 실패(다른 회원일 때)
        """
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_create_exist_fail(self):
        """
        ExpenseCreateView의 post 함수를 겸증하는 함수
        case: 실패(가계부를 찾을 수 없음)
        """
        response = self.client.post(
            path=reverse("expense-create", kwargs={"account_book_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)


class ExpenseDetailAPIViewTestCase(APITestCase):
    """ExpenseDetailView의 API를 검증하는 클래스 (19개)
    get method case: 4개
    post method case: 4개
    put method case: 7개
    delete method case: 4개
    """

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

    def test_expense_detail_get_success(self):
        """
        ExpenseDetailView의 get 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.get(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_expense_detail_get_anonymous_fail(self):
        """
        ExpenseDetailView의 get 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_detail_get_other_user_fail(self):
        """
        ExpenseDetailView의 get 함수를 겸증하는 함수
        case: 실패(다른 회원일 때)
        """
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_detail_get_exist_fail(self):
        """
        ExpenseDetailView의 get 함수를 겸증하는 함수
        case: 실패(지출 내역 찾을 수 없을 때)
        """
        response = self.client.get(
            path=reverse("expense-detail", kwargs={"expense_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)

    def test_expense_detail_post_success(self):
        """
        ExpenseDetailView의 post 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_expense_detail_post_anonymous_fail(self):
        """
        ExpenseDetailView의 post 함수를 겸증하는 함수
        case: 실패(비회원 일 때)
        """
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_detail_post_other_user_fail(self):
        """
        ExpenseDetailView의 post 함수를 겸증하는 함수
        case: 실패(다른 회원 일 때)
        """
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_detail_post_exist_fail(self):
        """
        ExpenseDetailView의 post 함수를 겸증하는 함수
        case: 실패(지출 내역 찾을 수 없을 때)
        """
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)

    def test_expense_detail_put_success(self):
        """
        ExpenseDetailView의 put 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money": 40000},
        )
        self.assertEqual(response.status_code, 200)

    def test_expense_detail_put_required_success(self):
        """
        ExpenseDetailView의 put 함수를 겸증하는 함수
        case: 성공(money 필드가 없을 때)
        """
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_expense_detail_put_blank_fail(self):
        """
        ExpenseDetailView의 put 함수를 겸증하는 함수
        case: 실패(money가 빈칸일 때)
        """
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money": ""},
        )
        self.assertEqual(response.status_code, 400)

    def test_expense_detail_put_invalid_fail(self):
        """
        ExpenseDetailView의 put 함수를 겸증하는 함수
        case: 실패(money가 불일치할 때)
        """
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money": "돈"},
        )
        self.assertEqual(response.status_code, 400)

    def test_expense_detail_put_anonymous_fail(self):
        """
        ExpenseDetailView의 put 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            data={"money": 40000},
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_detail_put_other_user_fail(self):
        """
        ExpenseDetailView의 put 함수를 겸증하는 함수
        case: 실패(다른 회원일 때)
        """
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
            data={"money": 40000},
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_detail_put_exist_fail(self):
        """
        ExpenseDetailView의 put 함수를 겸증하는 함수
        case: 실패(지출 내역을 찾을 수 없을 때)
        """
        response = self.client.put(
            path=reverse("expense-detail", kwargs={"expense_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"money": 40000},
        )
        self.assertEqual(response.status_code, 404)

    def test_expense_detail_delete_success(self):
        """
        ExpenseDetailView의 delete 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.delete(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 204)

    def test_expense_detail_delete_anonymous_fail(self):
        """
        ExpenseDetailView의 delete 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.delete(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_detail_delete_other_user_fail(self):
        """
        ExpenseDetailView의 delete 함수를 겸증하는 함수
        case: 실패(다른 회원일 때)
        """
        response = self.client.delete(
            path=reverse("expense-detail", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_detail_delete_exist_fail(self):
        """
        ExpenseDetailView의 delete 함수를 겸증하는 함수
        case: 실패(지출 내역을 찾을 수 없을 때)
        """
        response = self.client.delete(
            path=reverse("expense-detail", kwargs={"expense_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)


class ExpenseShareUrlCreateAPIViewTestCase(APITestCase):
    """ExpenseShareUrlCreateView의 API를 검증하는 클래스 (5개)
    post method case: 5개
    """

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
        cls.expense_url = ExpenseURL.objects.create(
            shared_url="http://testserver/MQd17c80f",
            expired_at="2023-02-03",
            expense=cls.expense,
        )

    def setUp(self):
        self.user_access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.other_user_access_token = self.client.post(reverse("auth-signin"), self.other_user_data).data["access"]

    def test_expense_share_url_create_success(self):
        """
        ExpenseShareUrlCreateView의 post 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.post(
            path=reverse("expense-share-url-create", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 201)

    def test_expense_share_url_create_unique_fail(self):
        """
        ExpenseShareUrlCreateView의 post 함수를 겸증하는 함수
        case: 실패(지출 내역에 링크가 존재할 때)
        """
        response = self.client.post(
            path=reverse("expense-share-url-create", kwargs={"expense_id": "2"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 208)

    def test_expense_share_url_create_anonymous_fail(self):
        """
        ExpenseShareUrlCreateView의 post 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.post(
            path=reverse("expense-share-url-create", kwargs={"expense_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_share_url_create_other_user_fail(self):
        """
        ExpenseShareUrlCreateView의 post 함수를 겸증하는 함수
        case: 실패(다른 회원일 때)
        """
        response = self.client.post(
            path=reverse("expense-share-url-create", kwargs={"expense_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_expense_share_url_create_exist_fail(self):
        """
        ExpenseShareUrlCreateView의 post 함수를 겸증하는 함수
        case: 실패(지출내역을 찾을 수 없을 때)
        """
        response = self.client.post(
            path=reverse("expense-detail", kwargs={"expense_id": "3"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)


class ExpenseShareUrlAPIViewTestCase(APITestCase):
    """ExpenseShareUrlView의 API를 검증하는 클래스 (4개)
    get method case: 4개
    """

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

    def test_expense_share_url_success(self):
        """
        ExpenseShareUrlView의 get함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.get(
            path=f"{reverse('expense-share-url')}?key=Mgd17c80f",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_expense_share_url_time_limit_fail(self):
        """
        ExpenseShareUrlView의 get 함수를 겸증하는 함수
        case: 실패(링크가 시간 만료되었을 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-share-url')}?key=MQd17c80f",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_expense_share_url_anonymous_fail(self):
        """
        ExpenseShareUrlView의 get 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-share-url')}?key=MQd17c80f",
        )
        self.assertEqual(response.status_code, 401)

    def test_expense_share_url_exist_fail(self):
        """
        ExpenseShareUrlView의 get 함수를 겸증하는 함수
        case: 실패(지출내역을 찾을 수 없을 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-share-url')}?key=ddddddd",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)


class ExpenseCategoryAPIViewTestCase(APITestCase):
    """ExpenseCategoryView의 API를 검증하는 클래스 (2개)
    get method case: 2개
    """

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        call_command("loaddata", "json_data/expense_category_data.json")

    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]

    def test_expense_category_success(self):
        """
        ExpenseCategoryView의 get 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.get(
            path=reverse("expense-category"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_expense_category_anonymous_fail(self):
        """
        ExpenseCategoryView의 get 함수를 겸증하는 함수
        case: 실패(비회원일 떄)
        """
        response = self.client.get(
            path=reverse("expense-category"),
        )
        self.assertEqual(response.status_code, 401)


class ExpenseCategorySearchAPIViewTestCase(APITestCase):
    """ExpenseCategorySearchView의 API를 검증하는 클래스 (5개)
    get method case: 5개
    """

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        call_command("loaddata", "json_data/expense_category_data.json")
        for _ in range(101):
            cls.expense = Expense.objects.create(
                money=30000,
                expense_detail="(주) 소고기 짱 좋아",
                payment_method="현금",
                memo="소고기 많이 먹음",
                account_book=cls.account_book,
                owner=cls.user,
                category_id=random.choice([1, 16]),
            )

    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]

    def test_expense_category_search_success(self):
        """
        ExpenseCategorySearchView의 get 함수를 겸증하는 함수
        case: 성공 (검색 내용에 맞을 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-category-search')}?date=2023-02&main=식비&sub=식사/간식",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_expense_category_search_all_success(self):
        """
        ExpenseCategorySearchView의 get 함수를 겸증하는 함수
        case: 성공(모든 쿼리 불러올 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-category-search')}?date=2023-02",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_expense_category_search_date_param_fail(self):
        """
        ExpenseCategorySearchView의 get 함수를 겸증하는 함수
        case: 실패(date 매개변수가 잘못 되었을 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-category-search')}?date=202302&main=식비&sub=식사/간식",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_expense_category_search_anonymous_fail(self):
        """
        ExpenseCategorySearchView의 get 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-category-search')}?date=2023-02&main=식비&sub=식사/간식",
        )
        self.assertEqual(response.status_code, 401)

    def test_expense_category_search_tag_param_fail(self):
        """
        ExpenseCategorySearchView의 get 함수를 겸증하는 함수
        case: 실패(main, sub 매개변수가 잘못 되었을 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-category-search')}?date=2023-02&main=식/비&sub=식사//간식",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)


class ExpenseCategoryStatAPIViewTestCase(APITestCase):
    """ExpenseCategoryStatView의 API를 검증하는 클래스 (4개)
    get method case: 4개
    """

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        cls.account_book = AccountBook.objects.create(date_at=f"2023-02-01", owner=cls.user)
        call_command("loaddata", "json_data/expense_category_data.json")
        for _ in range(62):
            cls.expense = Expense.objects.create(
                money=30000,
                expense_detail="(주) 소고기 짱 좋아",
                payment_method="현금",
                memo="소고기 많이 먹음",
                account_book=cls.account_book,
                owner=cls.user,
                category_id=random.choice([1, 2, 16, 19]),
            )

    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]

    def test_expense_category_stat_success(self):
        """
        ExpenseCategoryStatView의 get 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.get(
            path=f"{reverse('expense-caregory-stat')}?date=2023-02",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_expense_category_stat_param_fail(self):
        """
        ExpenseCategoryStatView의 get 함수를 겸증하는 함수
        case: 실패(date 매개변수가 잘못 되었을 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-caregory-stat')}?date=202302",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_expense_category_stat_anonymous_fail(self):
        """
        ExpenseCategoryStatView의 get 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-caregory-stat')}?date=2023-02",
        )
        self.assertEqual(response.status_code, 401)

    def test_expense_category_stat_exist_fail(self):
        """
        ExpenseCategoryStatView의 get 함수를 겸증하는 함수
        case: 실패(지출 내역을 찾을 수 없을 때)
        """
        response = self.client.get(
            path=f"{reverse('expense-caregory-stat')}?date=2023-04",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)
