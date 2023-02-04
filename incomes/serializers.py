# rest_framework
from rest_framework import serializers

# django
from django.utils.dateformat import DateFormat

# incomes
from .models import Income, IncomeCategory


class IncomeListSerializer(serializers.ModelSerializer):
    money = serializers.SerializerMethodField()
    income_detail = serializers.SerializerMethodField()

    class Meta:
        model = Income
        fields = (
            "id",
            "money",
            "income_detail",
            "payment_method",
        )

    def get_money(self, obj):
        return format(obj.money, ",")

    def get_income_detail(sefl, obj):
        return obj.brief_income_detail


class IncomeDetailSerializer(serializers.ModelSerializer):
    money = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Income
        fields = (
            "id",
            "money",
            "income_detail",
            "payment_method",
            "memo",
            "category",
        )

    def get_money(self, obj):
        return format(obj.money, ",")

    def get_category(self, obj):
        try:
            # 상위 카테고리가 없을 경우
            if not obj.category.parent_id:
                return obj.category.name

            # 상위 카테고리가 있을 경우
            main = IncomeCategory.objects.get(id=obj.category.parent_id)
            sub = obj.category.name
            return f"{main} >> {sub}"

        # 카테고리 null 값일 때
        except AttributeError:
            return "없음"


class IncomeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = (
            "money",
            "income_detail",
            "payment_method",
            "memo",
            "category",
        )
        extra_kwargs = {
            "money": {
                "error_messages": {
                    "required": "금액을 입력해주세요.",
                    "blank": "금액을 입력해주세요.",
                    "invalid": "숫자만 입력해주세요.",
                }
            },
        }


class IncomeSearchListSerializer(serializers.ModelSerializer):
    money = serializers.SerializerMethodField()
    income_detail = serializers.SerializerMethodField()
    date_at = serializers.SerializerMethodField("get_date_at")

    class Meta:
        model = Income
        fields = ("id", "money", "income_detail", "payment_method", "date_at")

    def get_money(self, obj):
        return format(obj.money, ",")

    def get_income_detail(sefl, obj):
        return obj.brief_income_detail

    def get_date_at(self, obj):
        return DateFormat(obj.account_book.date_at).format("Y-m-d")


class IncomeShareUrlSerializer(serializers.ModelSerializer):
    date_at = serializers.SerializerMethodField("get_date_at")
    owner = serializers.SerializerMethodField()
    money = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Income
        fields = (
            "money",
            "income_detail",
            "payment_method",
            "memo",
            "owner",
            "date_at",
            "category",
        )

    def get_date_at(self, obj):
        return DateFormat(obj.account_book.date_at).format("Y-m-d")

    def get_owner(self, obj):
        return obj.owner.nickname

    def get_money(self, obj):
        return format(obj.money, ",")

    def get_category(self, obj):
        try:
            # 상위 카테고리가 없을 경우
            if not obj.category.parent_id:
                return obj.category.name

            # 상위 카테고리가 있을 경우
            main = IncomeCategory.objects.get(id=obj.category.parent_id)
            sub = obj.category.name
            return f"{main} >> {sub}"

        # 카테고리 null 값일 때
        except AttributeError:
            return "없음"


class IncomeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeCategory
        fields = (
            "id",
            "name",
        )