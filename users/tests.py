# rest_framework
from rest_framework.test import APITestCase

# django
from django.urls import reverse

# users
from .models import User


class SignupAPIViewTestCase(APITestCase):
    """SignupView의 API를 검증하는 클래스 (11개)
    post method case: 11개
    """
    def test_signup_success(self):
        """
        SignupView의 post 함수를 겸증하는 함수
        case: 성공
        """
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "test1234",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 201)

    def test_signup_email_blank_fail(self):
        """
        SignupView의 post 함수를 겸증하는 함수
        case: 실패(이메일 빈칸일 때)
        """
        url = reverse("auth-signup")
        user_data = {
            "email": "",
            "nickname": "test1234",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    def test_signup_email_invalid_fail(self):
        """
        SignupView의 post 함수를 겸증하는 함수
        case: 실패(이메일 형식이 아닐 때)
        """
        url = reverse("auth-signup")
        user_data = {
            "email": "test",
            "nickname": "test1234",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    def test_signup_email_unique_fail(self):
        """
        SignupView의 post 함수를 겸증하는 함수
        case: 실패(이메일 중복일 때)
        """
        User.objects.create_user("test@test.com", "test1234", "Test1234!")
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "test123",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    def test_signup_nickname_blank_fail(self):
        """
        SignupView의 post 함수를 겸증하는 함수
        case: 실패(닉네임이 빈칸일 때)
        """
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    def test_signup_nickname_validation_fail(self):
        """
        SignupView의 post 함수를 겸증하는 함수
        case: 실패(닉네임 유효성 검사)
        """
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "n!!!!!!!!!",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    def test_signup_nickname_unique_fail(self):
        """
        SignupView의 post 함수를 겸증하는 함수
        case: 실패(닉네임 중복일 때)
        """
        User.objects.create_user("test@test.com", "test1234", "Test1234!")
        url = reverse("auth-signup")
        user_data = {
            "email": "test1@test.com",
            "nickname": "test1234",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    def test_signup_password_blank_fail(self):
        """
        SignupView의 post 함수를 겸증하는 함수
        case: 실패(비밀번호 빈칸일 때)
        """
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "test1234",
            "password": "",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    def test_signup_password_confirm_blank_fail(self):
        """
        SignupView의 post 함수를 겸증하는 함수
        case: 실패(비밀번호 재확인이 빈칸일 때)
        """
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "test1234",
            "password": "Test1234!",
            "repassword": "",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    def test_signup_password_same_fail(self):
        """
        SignupView의 post 함수를 겸증하는 함수
        case: 실패(비밀번호와 재확인이 일치하지 않을 때)
        """
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "test1234",
            "password": "Test1234!",
            "repassword": "Test12345!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    def test_signup_password_validation_fail(self):
        """
        SignupView의 post 함수를 겸증하는 함수
        case: 실패(비밀번호 유효성 검사)
        """
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "test1234",
            "password": "t1",
            "repassword": "t1",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)


class SigninAPIViewTestCase(APITestCase):
    """CustomTokenObtainPairView와 TokenRefreshView의 API를 검증하는 클래스 (5개)
    CustomTokenObtainPairView post method case: 2개
    TokenRefreshView post method case: 3개
    """
    @classmethod
    def setUpTestData(cls):
        cls.user_success_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user_fail_data = {"email": "test1234@test.com", "password": "Test1234!!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")

    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_success_data).data["access"]
        self.refresh_token = self.client.post(reverse("auth-signin"), self.user_success_data).data["refresh"]

    def test_access_token_login_success(self):
        """
        CustomTokenObtainPairView의 post 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.post(reverse("auth-signin"), self.user_success_data)
        self.assertEqual(response.status_code, 200)

    def test_access_token_login_fail(self):
        """
        CustomTokenObtainPairView의 post 함수를 겸증하는 함수
        case: 실패(입력값 오류)
        """
        response = self.client.post(reverse("auth-signin"), self.user_fail_data)
        self.assertEqual(response.status_code, 401)

    def test_refresh_token_login_success(self):
        """
        TokenRefreshView의 post 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.post(
            path=reverse("auth-signin-refresh"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": self.refresh_token},
        )
        self.assertEqual(response.status_code, 200)

    def test_refresh_token_login_fail(self):
        """
        TokenRefreshView의 post 함수를 겸증하는 함수
        case: 실패(refresh token 입력안했을 때)
        """
        response = self.client.post(
            path=reverse("auth-signin-refresh"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_refresh_token_login_invalid_fail(self):
        """
        TokenRefreshView의 post 함수를 겸증하는 함수
        case: 실패(access token으로 넣었을 때)
        """
        response = self.client.post(
            path=reverse("auth-signin-refresh"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": self.access_token},
        )
        self.assertEqual(response.status_code, 401)


class TokenVerifyAPIViewTestCase(APITestCase):
    """TokenVerifyView의 API를 검증하는 클래스 (3개)
    post method case: 3개
    """
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")

    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.refresh_token = self.client.post(reverse("auth-signin"), self.user_data).data["refresh"]

    def test_access_token_verify_success(self):
        """
        TokenVerifyView의 post 함수를 겸증하는 함수
        case: 성공(access token 유효할 때)
        """
        response = self.client.post(
            path=reverse("auth-verify"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"token": self.access_token},
        )
        self.assertEqual(response.status_code, 200)

    def test_refresh_token_verify_success(self):
        """
        TokenVerifyView의 post 함수를 겸증하는 함수
        case: 성공(refresh token 유효할 때)
        """
        response = self.client.post(
            path=reverse("auth-verify"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"token": self.refresh_token},
        )
        self.assertEqual(response.status_code, 200)

    def test_token_verify_fail(self):
        """
        TokenVerifyView의 post 함수를 겸증하는 함수
        case: 실패(token이 유효하지 않을 때)
        """
        response = self.client.post(
            path=reverse("auth-verify"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"token": f"{self.access_token}123"},
        )
        self.assertEqual(response.status_code, 401)


class SignoutAPIViewTestCase(APITestCase):
    """SignoutView의 API를 검증하는 클래스 (3개)
    post method case: 3개
    """
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {"email": "test1234@test.com", "password": "Test1234!"}
        cls.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")

    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_data).data["access"]
        self.refresh_token = self.client.post(reverse("auth-signin"), self.user_data).data["refresh"]

    def test_refresh_token_logout_success(self):
        """
        SignoutView의 post 함수를 겸증하는 함수
        case: 성공
        """
        response = self.client.post(
            path=reverse("auth-signout"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": self.refresh_token},
        )
        self.assertEqual(response.status_code, 200)

    def test_refresh_token_logout_fail(self):
        """
        SignoutView의 post 함수를 겸증하는 함수
        case: 실패(refresh token을 입력안했을 때)
        """
        response = self.client.post(
            path=reverse("auth-signout"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_refresh_token_logout_invalid_fail(self):
        """
        SignoutView의 post 함수를 겸증하는 함수
        case: 실패(access token을 입력했을 때)
        """
        response = self.client.post(
            path=reverse("auth-signout"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": self.access_token},
        )
        self.assertEqual(response.status_code, 400)