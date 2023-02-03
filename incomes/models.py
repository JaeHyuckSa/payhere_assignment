# django
from django.db import models

# account_books
from account_books.models import TimeStampModel


class Income(TimeStampModel):
    PAYMENT_METHOD = (
        ("현금", "현금"),
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
    
    class Meta: 
        db_table = "Income"
    
    def __str__(self):
        return f"[{self.created_at}]{self.moeny}원"


class IncomeURL(models.Model):
    shared_url = models.URLField("공유 링크")
    expired_at = models.DateTimeField("만료일")
    
    income = models.OneToOneField("Income", verbose_name="수익", on_delete=models.CASCADE, related_name="income_urls")
    
    class Meta: 
        db_table = "IncomeURL"
    
    def __str__(self):
        return f"[{self.expired_at}][{self.shared_url}]"