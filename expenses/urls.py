# django
from django.urls import path

# expenses
from . import views


urlpatterns = [
    # Expense
    path("", views.ExpenseListView.as_view(), name="expense-list"),
    path("<int:account_book_id>/", views.ExpenseCreateView.as_view(), name="expense-create"),
]
