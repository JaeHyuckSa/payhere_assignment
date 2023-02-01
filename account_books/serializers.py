from rest_framework import serializers

from .models import AccountBook
from django.utils.dateformat import DateFormat


class AccountBookSerializer(serializers.ModelSerializer):
    date_at = serializers.SerializerMethodField()
    day_total_money = serializers.SerializerMethodField()
    
    class Meta:
        model = AccountBook
        fields = ("date_at",  "day_total_money", )
        
    def get_date_at(self, obj):
        return DateFormat(obj.date_at).format("Y-m-d")
    
    def get_day_total_money(self, obj):
        return format(obj.day_total_money, ",")


class AccountBookCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AccountBook
        fields = ("date_at",)
        extra_kwargs = {
            "date_at": {
                "error_messages": {
                    "required": "날짜를 입력해주세요.",
                    "blank": "날짜를 입력해주세요.",
                    "invalid": "알맞은 날짜 형식을 입력해주세요. (Ex:YYYY-MM-DD)",
                }
            },
        }
    
    def validate(self, data):
        date_at = data.get("date_at")
        user_id = self.context.get("request").user.id
        
        # 날짜 중복 검사
        try:
            if AccountBook.objects.get(date_at=date_at, owner=user_id):
                raise serializers.ValidationError(detail={"date_at": "해당 날짜에 가계부 목록이 존재합니다."})

        except AccountBook.DoesNotExist:
            pass
        
        return data