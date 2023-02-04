# rest_framework
from rest_framework import permissions

# django
from django.contrib import admin
from django.urls import path, include

# drf_yasg
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Payhere Assignment",
        default_version="v1",
        description="Payhere 가계부 프로젝트 API",
        contact=openapi.Contact(email="wogur981208@gmail.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # Apps
    path("users/auth/", include("users.urls")),
    path("account-books/", include("account_books.urls")),
    path("expenses/", include("expenses.urls")),
    path("incomes/", include("incomes.urls")),
    
    # Swagger
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/api.json/", schema_view.without_ui(cache_timeout=0), name="schema-swagger-json"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
