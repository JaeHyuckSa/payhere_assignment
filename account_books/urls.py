# django
from django.urls import path

# account_books
from . import views


urlpatterns = [
    # Account book
    path("", views.AccountBookView.as_view(), name="account-book"),
    path("date-set/", views.AccountBookDateSetView.as_view(), name="account-book-date-set"),
    path("details/<int:account_book_id>/", views.AccountBookDetailView.as_view(), name="account-book-details"),
]
