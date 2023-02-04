# django
from django.contrib import admin

# mptt
from mptt.admin import DraggableMPTTAdmin

# incomes
from .models import Income, IncomeURL, IncomeCategory


admin.site.register(Income)
admin.site.register(IncomeURL)
admin.site.register(IncomeCategory, DraggableMPTTAdmin)