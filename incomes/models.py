# django
from django.db import models

# account_books
from account_books.models import TimeStampModel


class Income(TimeStampModel):
    PAYMENT_METHOD = (
        ("0", "현금"),
    )
    
    money = models.IntegerField("금액")
    income_detail = models.CharField("수입 내역", max_length=15, null=True)
    payment_method = models.CharField("결제 수단", max_length=2, null=True, choices=PAYMENT_METHOD)
    memo = models.CharField("메모", max_length=255, null=True)
    owner = models.ForeignKey("users.User", verbose_name="유저", on_delete=models.CASCADE, related_name="incomes")
    account_book = models.ForeignKey("account_books.AccountBook", verbose_name="가계부", on_delete=models.CASCADE, related_name="incomes")
    
    @property
    def brief_income_detail(self):
        if self.income_detail:
            return f"{self.income_detail[:10]}..."
        return None


class IncomeURL(models.Model):
    shared_url = models.URLField("공유 링크")
    shared_url_limited_time = models.DateTimeField("공유 링크 제한 시간")
    
    account_book = models.ForeignKey("Income", verbose_name="가계부", on_delete=models.CASCADE, related_name="income_urls")