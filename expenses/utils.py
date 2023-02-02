# django
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, force_str
from django.utils import timezone
from django.db import transaction

# python
import uuid


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


class ExpenseUrlUtil:
    def get_expense_link_expired_at(expense):
        expired_at = timezone.now() + timezone.timedelta(days=1)
        return expired_at

    def get_expense_link(request, expense):
        uid = str(uuid.uuid4())[:7]
        uidb64 = urlsafe_base64_encode(smart_bytes(expense.id))
        encode_key = uidb64 + uid
        currnt_site = f"{get_current_site(request).domain}/"
        shared_url = "http://" + currnt_site + encode_key
        return shared_url

    def get_expense_id(encode_key):
        uidb64 = encode_key[:-7]
        expense_id = force_str(urlsafe_base64_decode(uidb64))
        return expense_id