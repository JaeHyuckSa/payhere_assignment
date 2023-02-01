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