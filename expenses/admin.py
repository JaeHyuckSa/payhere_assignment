# django
from django.contrib import admin

# expenses
from .models import Expense, ExpenseURL


admin.site.register(Expense)
admin.site.register(ExpenseURL)