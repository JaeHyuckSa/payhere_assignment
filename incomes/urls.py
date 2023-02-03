# django
from django.urls import path

# incomes
from . import views


urlpatterns = [
    # Income
    path("", views.IncomeListView.as_view(), name="income-list"),
]
