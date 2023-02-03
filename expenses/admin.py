# django
from django.contrib import admin

# mptt
from mptt.admin import DraggableMPTTAdmin

# expenses
from .models import Expense, ExpenseURL, ExpenseCategory


admin.site.register(Expense)
admin.site.register(ExpenseURL)
admin.site.register(ExpenseCategory, DraggableMPTTAdmin)