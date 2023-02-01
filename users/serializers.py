# rest_framework
from rest_framework import serializers

# rest_framework_simplejwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# users
from .models import User
from .validators import (
    password_validator,
    nickname_validator,
)


# 회원가입 serializer
class SignupSerializer(serializers.ModelSerializer):
    repassword = serializers.CharField(
        error_messages={
            "required": "비밀번호를 입력해주세요.",
            "blank": "비밀번호를 입력해주세요.",
            "write_only": True,
        }
    )

    class Meta:
        model = User
        fields = (
            "nickname",
            "password",
            "repassword",
            "email",
        )
        extra_kwargs = {
            "nickname": {
                "error_messages": {
                    "required": "닉네임을 입력해주세요.",
                    "blank": "닉네임을 입력해주세요",
                }
            },
            "password": {
                "write_only": True,
                "error_messages": {
                    "required": "비밀번호를 입력해주세요.",
                    "blank": "비밀번호를 입력해주세요.",
                },
            },
            "email": {
                "error_messages": {
                    "required": "이메일을 입력해주세요.",
                    "invalid": "알맞은 형식의 이메일을 입력해주세요.",
                    "blank": "이메일을 입력해주세요.",
                }
            },
        }

    def validate(self, data):
        nickname = data.get("nickname")
        password = data.get("password")
        repassword = data.get("repassword")

        # 닉네임 유효성 검사
        if nickname_validator(nickname):
            raise serializers.ValidationError(detail={"nickname": "닉네임은 3자이상 10자 이하로 작성해야하며 특수문자는 포함할 수 없습니다."})

        # 비밀번호 일치
        if password != repassword:
            raise serializers.ValidationError(detail={"password": "비밀번호가 일치하지 않습니다."})

        # 비밀번호 유효성 검사
        if password_validator(password):
            raise serializers.ValidationError(detail={"password": "비밀번호는 8자 이상 16자이하의 영문 소문자, 숫자, 특수문자 조합이어야 합니다."})

        return data

    def create(self, validated_data):
        nickname = validated_data["nickname"]
        email = validated_data["email"]

        user = User(
            nickname=nickname,
            email=email,
        )
        user.set_password(validated_data["password"])
        user.save()

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["user_id"] = user.id
        token["nickname"] = user.nickname
        token["email"] = user.email

        return token