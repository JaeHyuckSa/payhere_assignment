# rest_framework
from rest_framework import serializers

# django
from django.utils.dateformat import DateFormat

# incomes
from .models import Income


class IncomeSerializer(serializers.ModelSerializer):
    money = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Income
        fields = ("id", "money", "income_detail", "payment_method", "memo",  "updated_at", "created_at",)
    
    def get_updated_at(self, obj):
        return DateFormat(obj.updated_at).format("Y-m-d H:i")
    
    def get_created_at(self, obj):
        return DateFormat(obj.created_at).format("Y-m-d H:i")
    
    def get_money(self, obj):
        return format(obj.money, ",")
    

class IncomeCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Income
        fields = ("money", "income_detail", "payment_method", "memo", )
        extra_kwargs = {
            "money": {
                "error_messages": {
                    "required": "금액을 입력해주세요.",
                    "blank": "금액을 입력해주세요.",
                    "invalid": "숫자만 입력해주세요.",
                }
            },
        }


class IncomeShareUrlSerializer(serializers.ModelSerializer):
    date_at = serializers.SerializerMethodField("get_date_at")
    owner = serializers.SerializerMethodField()
    money = serializers.SerializerMethodField()
    
    class Meta:
        model = Income
        fields = ("money", "income_detail", "payment_method", "memo",  "owner", "account_book", "date_at", )
    
    def get_date_at(self, obj):
        return DateFormat(obj.account_book.date_at).format("Y-m-d")
    
    def get_owner(self, obj):
        return obj.owner.nickname
    
    def get_money(self, obj):
        return format(obj.money, ",")