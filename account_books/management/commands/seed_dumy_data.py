# django
from django.core.management.base import BaseCommand

# faker
from faker import Faker

# python
import time
import random

# apps
from users.models import User
from account_books.models import AccountBook
from expenses.models import Expense
from incomes.models import Income

class Command(BaseCommand):
    
    help = '더미 데이터를 생성합니다.'
    
    def handle(self, *args, **options):
        """100명의 더미 유저 데이터 생성
        """
        self.stdout.write("100명의 유저 생성")
        start_time = time.time()
        users_list = [
            User(
                email=f"test{i}@test.com",
                nickname=f"test{i}",
                password="test1234!",
            ) for i in range(1, 101)
        ]
        User.objects.bulk_create(users_list)
        end_time = time.time()
        self.stdout.write(f"100명 유저 생성 시간{round(end_time-start_time, 2)}초")
        
        """3000개의 가계부 더미 데이터 생성
        """
        self.stdout.write("1명당 30개의 가계부 생성(100명/3000개)")
        start_time = time.time()
        for i in range(1, 101):
            account_books_list = [
                AccountBook(
                    date_at=f"2023-01-{j}",
                    owner_id=i,
                ) for j in range(1, 31)
            ]
            AccountBook.objects.bulk_create(account_books_list)
        end_time = time.time()
        self.stdout.write(f"100명의 3000개 가계부 생성 시간{round(end_time-start_time, 2)}초")
        
        """10000개의 지출 데이터 생성
        """
        self.stdout.write("10000개의 지출 생성")
        start_time = time.time()
        for _ in range(1, 100):
            expense_list = [
                Expense(
                    money=random.randint(10000, 1000000),
                    expense_detail=Faker().word(),
                    memo=Faker().sentence(),
                    owner_id=random.randint(1,100),
                    account_book_id=random.randint(1,3000),
                ) for _ in range(1, 100)
            ]
            Expense.objects.bulk_create(expense_list)
        self.stdout.write(f"10000개의 지출 생성 시간{round(end_time-start_time, 2)}초")

        """10000개의 수익 데이터 생성
        """
        self.stdout.write("10000개의 수익 생성")
        for _ in range(1, 100):
            income_list = [
                Income(
                    money=random.randint(10000, 1000000),
                    income_detail=Faker().word(),
                    memo=Faker().sentence(),
                    owner_id=random.randint(1,100),
                    account_book_id=random.randint(1,3000),
                ) for _ in range(1, 100)
            ]
            Income.objects.bulk_create(income_list)
        end_time = time.time()
        self.stdout.write(f"10000개의 수익 생성 시간{round(end_time-start_time, 2)}초")