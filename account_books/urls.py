# django
from django.urls import path

# account_books
from . import views


urlpatterns = [
    # Account book
    path("", views.AccountBookView.as_view(), name="account-book"),
    path("details/<int:account_book_id>/", views.AccountBookDetailView.as_view(), name="account-book-detail"),
]
