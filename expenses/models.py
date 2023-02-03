# django
from django.db import models

# mptt
from mptt.models import MPTTModel, TreeForeignKey

# account_books
from account_books.models import TimeStampModel


class Expense(TimeStampModel):
    PAYMENT_METHOD = (
        ("현금", "현금"),
        ("카드", "카드"),
    )
    
    money = models.IntegerField("금액")
    expense_detail = models.CharField("지출 내역", max_length=15, null=True)
    payment_method = models.CharField("결제 수단", max_length=2, default=PAYMENT_METHOD[0][0], choices=PAYMENT_METHOD)
    memo = models.CharField("메모", max_length=255, null=True)
    
    category = TreeForeignKey("ExpenseCategory", verbose_name="카테고리", null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    owner = models.ForeignKey("users.User", verbose_name="유저", on_delete=models.CASCADE, related_name="expenses")
    account_book = models.ForeignKey("account_books.AccountBook", verbose_name="가계부", on_delete=models.CASCADE, related_name="expenses")
    
    @property
    def brief_expense_detail(self):
        try:
            if len(self.expense_detail) > 10:
                return f"{self.expense_detail[:10]}..."
    
            elif self.expense_detail:
                return self.expense_detail
    
        except TypeError:
            return None
    
    class Meta: 
        db_table = "Expense"
    
    def __str__(self):
        return f"[{self.created_at}]{self.money}원"


class ExpenseCategory(MPTTModel):
    name = models.CharField("이름", max_length=50, unique=True, error_messages={"unique": "이미 사용중인 카테고리입니다."})
    parent = TreeForeignKey("self", verbose_name="부모", on_delete=models.CASCADE, null=True, blank=True, related_name="children", db_index=True)
    
    class MPTTMeta:
        order_insertion_by = ["name"]
        
    class Meta:
        db_table = "ExpenseCategory"
        
    def __str__(self):
        return self.name


class ExpenseURL(models.Model):
    shared_url = models.URLField("공유 링크")
    expired_at = models.DateTimeField("만료일")
    
    expense = models.OneToOneField("Expense", verbose_name="지출", on_delete=models.CASCADE, related_name="expense_urls")
    
    class Meta: 
        db_table = "ExpenseURL"
    
    def __str__(self):
        return f"[{self.expired_at}][{self.shared_url}]"