# Generated by Django 4.1.5 on 2023-02-01 18:01

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        error_messages={"unique": "이미 사용중인 이메일입니다."},
                        max_length=255,
                        unique=True,
                        verbose_name="이메일",
                    ),
                ),
                (
                    "nickname",
                    models.CharField(
                        error_messages={"unique": "이미 사용중인 닉네임입니다."},
                        max_length=10,
                        unique=True,
                        verbose_name="닉네임",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="로그인 가능 여부"),
                ),
                ("is_admin", models.BooleanField(default=False, verbose_name="관리자 여부")),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
