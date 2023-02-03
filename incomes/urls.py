# django
from django.urls import path

# incomes
from . import views


urlpatterns = [
    # Income
    path("", views.IncomeListView.as_view(), name="income-list"),
    path("<int:account_book_id>/", views.IncomeCreateView.as_view(), name="income-create"),
    path("details/<int:income_id>/", views.IncomeDetailView.as_view(), name="income-detail"),
    
]
