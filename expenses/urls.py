# django
from django.urls import path

# expenses
from . import views


urlpatterns = [
    # Expense
    path("", views.ExpenseListView.as_view(), name="expense-list"),
]
