# django
from django.contrib import admin

# incomes
from .models import Income, IncomeURL


admin.site.register(Income)
admin.site.register(IncomeURL)