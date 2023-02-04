# rest_framework
from rest_framework.test import APITestCase

# django
from django.urls import reverse

# apps
from .models import AccountBook
from users.models import User



class AccountBookAPIViewTestCase(APITestCase):
    """AccountBookView의 API를 검증하는 클래스 (10개)
    post method case: 6개
    get method case: 4개
    """
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")
        for i in range(1, 11):
            AccountBook.objects.create(date_at=f"2023-02-{i}", owner=cls.user)

    def setUp(self):
        self.access_token = self.client.post(
            reverse("auth-signin"), self.user_data
        ).data["access"]

    def test_account_book_post_success(self):
        """
        AccountBookView의 post 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.post(
            path=reverse("account-book"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"date_at": "2023-02-11"},
        )
        self.assertEqual(response.status_code, 201)

    def test_account_book_post_unique_fail(self):
        """
        AccountBookView의 post 함수를 겸증하는 함수
        case: 실패(날짜 중복)
        """
        response = self.client.post(
            path=reverse("account-book"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"date_at": "2023-02-01"},
        )
        self.assertEqual(response.status_code, 400)

    def test_account_book_post_invalid_fail(self):
        """
        AccountBookView의 post 함수를 겸증하는 함수
        case: 실패(date_at이 날짜 형식이 아닐때)
        """
        response = self.client.post(
            path=reverse("account-book"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"date_at": "123456"},
        )
        self.assertEqual(response.status_code, 400)

    def test_account_book_post_blank_fail(self):
        """
        AccountBookView의 post 함수를 겸증하는 함수
        case: 실패(date_at이 빈칸일 때)
        """
        response = self.client.post(
            path=reverse("account-book"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"date_at": ""},
        )
        self.assertEqual(response.status_code, 400)

    def test_account_book_post_required_fail(self):
        """
        AccountBookView의 post 함수를 겸증하는 함수
        case: 실패(date_at이 필드가 존재하지 않을 때)
        """
        response = self.client.post(
            path=reverse("account-book"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_account_book_post_anonymous_fail(self):
        """
        AccountBookView의 post 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.post(
            path=reverse("account-book"),
            data={"date_at": "2023-02-15"},
        )
        self.assertEqual(response.status_code, 401)

    def test_account_book_get_success(self):
        """
        AccountBookView의 get 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.get(
            path=f"{reverse('account-book')}?date=2023-02",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_account_book_get_param_fail(self):
        """
        AccountBookView의 get 함수를 겸증하는 함수
        case: 실패(url 매개변수 설정 잘못되었을 때)
        """
        response = self.client.get(
            path=f"{reverse('account-book')}?date=202302",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_account_book_get_anonymous_fail(self):
        """
        AccountBookView의 get 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.get(
            path=f"{reverse('account-book')}?date=2023-02",
        )
        self.assertEqual(response.status_code, 401)

    def test_account_book_get_exist_fail(self):
        """
        AccountBookView의 get 함수를 겸증하는 함수
        case: 실패(가계부가 존재하지 않을 때)
        """
        response = self.client.get(
            path=f"{reverse('account-book')}?date=2023-03",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)


class AccountBookDetailAPIViewTestCase(APITestCase):
    """AccountBookDetailView의 API를 검증하는 클래스 (14개)
    get method case: 4개
    put method case: 6개
    delete method case: 4개
    """
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

    def test_account_book_detail_get_success(self):
        """
        AccountBookDetailView의 get 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.get(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_account_book_detail_get_anonymous_fail(self):
        """
        AccountBookDetailView의 get 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.get(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)

    def test_account_book_detail_get_other_user_fail(self):
        """
        AccountBookDetailView의 get 함수를 겸증하는 함수
        case: 실패(다른 회원일 때)
        """
        response = self.client.get(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_account_book_detail_get_exits_success(self):
        """
        AccountBookDetailView의 get 함수를 겸증하는 함수
        case: 실패(가계부가 존재하지 않을 때)
        """
        response = self.client.get(
            path=reverse("account-book-detail", kwargs={"account_book_id": "8"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)

    def test_account_book_detail_put_success(self):
        """
        AccountBookDetailView의 put 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"date_at": "2023-02-06"},
        )
        self.assertEqual(response.status_code, 200)

    def test_account_book_detail_put_unique_fail(self):
        """
        AccountBookDetailView의 put 함수를 겸증하는 함수
        case: 실패(날짜 중복되었을 때)
        """
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"date_at": "2023-02-05"},
        )
        self.assertEqual(response.status_code, 400)

    def test_account_book_detail_put_invalid_fail(self):
        """
        AccountBookDetailView의 put 함수를 겸증하는 함수
        case: 실패(날짜 형식이 아닐 때)
        """
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"date_at": "123456"},
        )
        self.assertEqual(response.status_code, 400)

    def test_account_book_detail_put_anonymous_fail(self):
        """
        AccountBookDetailView의 put 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            data={"date_at": "2023-02-06"},
        )
        self.assertEqual(response.status_code, 403)

    def test_account_book_detail_put_other_user_fail(self):
        """
        AccountBookDetailView의 put 함수를 겸증하는 함수
        case: 실패(다른 회원일 떼)
        """
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
            data={"date_at": "2023-02-06"},
        )
        self.assertEqual(response.status_code, 403)

    def test_account_book_detail_put_exist_fail(self):
        """
        AccountBookDetailView의 put 함수를 겸증하는 함수
        case: 실패(가계부가 존재하지 않을 때)
        """
        response = self.client.put(
            path=reverse("account-book-detail", kwargs={"account_book_id": "15"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
            data={"date_at": "2023-02-06"},
        )
        self.assertEqual(response.status_code, 404)

    def test_account_book_detail_delete_success(self):
        """
        AccountBookDetailView의 delete 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.delete(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 204)

    def test_account_book_detail_delete_anonymous_fail(self):
        """
        AccountBookDetailView의 delete 함수를 겸증하는 함수
        case: 실패(비회원일 때)
        """
        response = self.client.delete(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
        )
        self.assertEqual(response.status_code, 403)

    def test_account_book_detail_delete_other_user_fail(self):
        """
        AccountBookDetailView의 delete 함수를 겸증하는 함수
        case: 실패(다른 회원일 때)
        """
        response = self.client.delete(
            path=reverse("account-book-detail", kwargs={"account_book_id": "1"}),
            HTTP_AUTHORIZATION=f"Bearer {self.other_user_access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_account_book_detail_delete_exist_fail(self):
        """
        AccountBookDetailView의 delete 함수를 겸증하는 함수
        case: 실패(가계부가 존재하지 않을 때)
        """
        response = self.client.delete(
            path=reverse("account-book-detail", kwargs={"account_book_id": "15"}),
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, 404)
