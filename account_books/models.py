from django.db import models


class AccountBook(models.Model):
    date_at = models.DateTimeField("날짜")
    day_total_money = models.PositiveIntegerField("일 총 금액", default=0)
    
    owner = models.ForeignKey("users.User", verbose_name="유저", on_delete=models.CASCADE, related_name="account_books")
    
    class Meta:
        db_table = "AccountBook"
        ordering = ["-date_at"]
        
    def __str__(self):
        return f"{self.date_at}/[일 총 금액:{self.day_total_money}]"


class TimeStampModel(models.Model):
    created_at = models.DateTimeField("생성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        abstract = True