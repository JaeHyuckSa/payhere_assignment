# django
from django.db import transaction


class ExpenseCalcUtil:
    @transaction.atomic
    def sub_total_money_expense(account_book, expense):
        account_book.day_total_money -= expense
        account_book.save()

    @transaction.atomic
    def add_total_money_expense(account_book, expense):
        account_book.day_total_money += expense
        account_book.save()
    
    @transaction.atomic
    def mix_total_money_expense(account_book, current_money, request_money):
        if current_money < request_money:
            account_book.day_total_money -= (request_money - current_money)
            account_book.save()
            
        elif current_money > request_money:
            account_book.day_total_money += (current_money - request_money)
            account_book.save()