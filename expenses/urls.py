# django
from django.urls import path

# expenses
from . import views


urlpatterns = [
    # Expense
    path("", views.ExpenseListView.as_view(), name="expense-list"),
    path("<int:account_book_id>/", views.ExpenseCreateView.as_view(), name="expense-create"),
    path("details/<int:expense_id>/", views.ExpenseDetailView.as_view(), name="expense-detail"),    
    
    # Expense Category
    path("categories/", views.ExpenseCategoryView.as_view(), name="expense-category"),
    path("categories/search/", views.ExpenseCategorySearchView.as_view(), name="expense-category-search"),
    
    # Expense Share Url
    path("share-urls/<int:expense_id>/", views.ExpenseShareUrlCreateView.as_view(), name="expense-share-url-create"),
    path("share-urls/", views.ExpenseShareUrlView.as_view(), name="expense-share-url"),
]
