# django
from django.urls import path

# incomes
from . import views


urlpatterns = [
    # Income
    path("", views.IncomeListView.as_view(), name="income-list"),
    path("<int:account_book_id>/", views.IncomeCreateView.as_view(), name="income-create"),
    path("details/<int:income_id>/", views.IncomeDetailView.as_view(), name="income-detail"),
    
    # Income Category
    path("categories/", views.IncomeCategoryView.as_view(), name="income-category"),
    path("categories/search/", views.IncomeCategorySearchView.as_view(), name="income-category-search"),
    
    # Income Share Url
    path("share-urls/<int:income_id>/", views.IncomeShareUrlCreateView.as_view(), name="income-share-url-create"),
    path("share-urls/", views.IncomeShareUrlView.as_view(), name="income-share-url"),
]
