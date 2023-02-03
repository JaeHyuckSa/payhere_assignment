from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
        if not email or not nickname:
            raise ValueError("이메일과 닉네임을 작성해주세요.")

        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password=None):
        user = self.create_user(
            email,
            password=password,
            nickname=nickname,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField("이메일", max_length=255, unique=True, error_messages={"unique": "이미 사용중인 이메일입니다."})
    nickname = models.CharField("닉네임", max_length=10, unique=True, error_messages={"unique": "이미 사용중인 닉네임입니다."})
    is_active = models.BooleanField("로그인 가능 여부",default=True)
    is_admin = models.BooleanField("관리자 여부",default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        db_table = "User"
