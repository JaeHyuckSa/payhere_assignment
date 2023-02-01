# rest_framework
from rest_framework.test import APITestCase

# django
from django.urls import reverse

# users
from .models import User


class UserSignupAPIViewTestCase(APITestCase):

    # 회원가입 성공
    def test_signup_success(self):
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "test1234",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 201)

    # 회원가입 실패(이메일 빈칸)
    def test_signup_email_blank_fail(self):
        url = reverse("auth-signup")
        user_data = {
            "email": "",
            "nickname": "test1234",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    # 회원가입 실패(이메일 형식)
    def test_signup_email_invalid_fail(self):
        url = reverse("auth-signup")
        user_data = {
            "email": "test",
            "nickname": "test1234",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    # 회원가입 실패(이메일 중복)
    def test_signup_email_unique_fail(self):
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

    # 회원가입 실패(닉네임 빈칸)
    def test_signup_nickname_blank_fail(self):
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    # 회원가입 실패(닉네임 유효성검사)
    def test_signup_nickname_validation_fail(self):
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "n!!!!!!!!!",
            "password": "Test1234!",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    # 회원가입 실패(닉네임 중복)
    def test_signup_nickname_unique_fail(self):
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

    # 회원가입 실패(비밀번호 빈칸)
    def test_signup_password_blank_fail(self):
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "test1234",
            "password": "",
            "repassword": "Test1234!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    # 회원가입 실패(비밀번호확인 빈칸)
    def test_signup_password_confirm_blank_fail(self):
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "test1234",
            "password": "Test1234!",
            "repassword": "",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    # 회원가입 실패(비밀번호, 비밀번호 확인 일치)
    def test_signup_password_same_fail(self):
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "test1234",
            "password": "Test1234!",
            "repassword": "Test12345!",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)

    # 회원가입 실패(비밀번호 유효성 검사)
    def test_signup_password_validation_fail(self):
        url = reverse("auth-signup")
        user_data = {
            "email": "test@test.com",
            "nickname": "test1234",
            "password": "t1",
            "repassword": "t1",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
class UserLoginAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.user_success_data = {"email": "test1234@test.com", "password": "Test1234!"}
        self.user_fail_data = {"email": "test1234@test.com", "password": "Test1234!!"}
        self.user = User.objects.create_user("test1234@test.com", "test1234", "Test1234!")

    def setUp(self):
        self.access_token = self.client.post(reverse("auth-signin"), self.user_success_data).data["access"]
        self.refresh_token = self.client.post(reverse("auth-signin"), self.user_success_data).data["refresh"]

    # (access_token)로그인 성공
    def test_access_token_login_success(self):
        response = self.client.post(reverse("auth-signin"), self.user_success_data)
        self.assertEqual(response.status_code, 200)

    # (access_token)로그인 실패
    def test_access_token_login_fail(self):
        response = self.client.post(reverse("auth-signin"), self.user_fail_data)
        self.assertEqual(response.status_code, 401)

    # (refresh_token)로그인 성공
    def test_refresh_token_login_success(self):
        response = self.client.post(
            path=reverse("auth-signin-refresh"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": self.refresh_token},
        )
        self.assertEqual(response.status_code, 200)

    # (refresh_token)로그인 실패(refresh 입력안했을 때)
    def test_refresh_token_login_fail(self):
        response = self.client.post(
            path=reverse("auth-signin-refresh"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    # (refresh_token)로그인 실패(access 토큰 넣었을 때)
    def test_refresh_token_login_invalid_fail(self):
        response = self.client.post(
            path=reverse("auth-signin-refresh"),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            data={"refresh": self.access_token},
        )
        self.assertEqual(response.status_code, 401)
