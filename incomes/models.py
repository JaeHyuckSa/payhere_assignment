# django
from django.db import models

# mptt
from mptt.models import MPTTModel, TreeForeignKey

# account_books
from account_books.models import TimeStampModel


class Income(TimeStampModel):
    PAYMENT_METHOD = (
        ("현금", "현금"),
    )
    
    money = models.IntegerField("금액")
    income_detail = models.CharField("수익 내역", max_length=15, null=True)
    payment_method = models.CharField("결제 수단", max_length=2, null=True, choices=PAYMENT_METHOD)
    memo = models.CharField("메모", max_length=255, null=True)
    
    category = TreeForeignKey("IncomeCategory", verbose_name="카테고리", null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    owner = models.ForeignKey("users.User", verbose_name="유저", on_delete=models.CASCADE, related_name="incomes")
    account_book = models.ForeignKey("account_books.AccountBook", verbose_name="가계부", on_delete=models.CASCADE, related_name="incomes")
    
    @property
    def brief_income_detail(self):
        try:
            if len(self.income_detail) > 10:
                return f"{self.income_detail[:10]}..."
    
            elif self.income_detail:
                return self.income_detail
    
        except TypeError:
            return None
    
    class Meta: 
        db_table = "Income"
    
    def __str__(self):
        return f"[{self.created_at}]{self.money}원"


class IncomeCategory(MPTTModel):
    name = models.CharField("이름", max_length=50, unique=True, error_messages={"unique": "이미 사용중인 카테고리입니다."})
    parent = TreeForeignKey("self", verbose_name="부모", on_delete=models.CASCADE, null=True, blank=True, related_name="children", db_index=True)
    
    class MPTTMeta:
        order_insertion_by = ["name"]
        
    class Meta:
        db_table = "IncomeCategory"
        
    def __str__(self):
        return self.name


class IncomeURL(models.Model):
    shared_url = models.URLField("공유 링크")
    expired_at = models.DateTimeField("만료일")
    
    income = models.OneToOneField("Income", verbose_name="수익", on_delete=models.CASCADE, related_name="income_urls")
    
    class Meta: 
        db_table = "IncomeURL"
    
    def __str__(self):
        return f"[{self.expired_at}][{self.shared_url}]"